# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
EM1 model adaptor facilities.
"""
import traceback
from collections import ChainMap
from osgeo import ogr
import numpy as np

from ramsis.sfm.worker import orm
from ramsis.sfm.worker.utils.misc import subgeoms_for_single_result,\
    single_reservoir_result, transform
from ramsis.sfm.worker.model_adaptor import (ModelAdaptor as _ModelAdaptor,
                                             ModelError, ModelResult)
from ramsis.sfm.em1.core.utils import obspy_catalog_parser, hydraulics_parser
from ramsis.sfm.em1.core import em1_model

# Example of a model adaptor. This takes inputs from the base worker
# and converts data to something the model can consume. Further validations
# can also be done here.

# Subclassing of Error class, modify as required.
class EM1Error(ModelError):
    """Base EM1 model error ({})."""

class ValidationError(EM1Error):
    """ValidationError ({})."""


class ModelAdaptor(_ModelAdaptor):
    """
    EM1 model implementation running the EM1 model code. The class wraps up
    model specifc code providing a unique interface.

    :param str reservoir_geometry: Reservoir geometry used by default.
        WKT format.
    :param dict model_parameters: Dictionary of model parameters used by
        default.
    """

    LOGGER = 'ramsis.sfm.worker.model_adaptor'

    NAME = 'EM1'
    DESCRIPTION = 'Shapiro and Smoothed Seismicity'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_defaults = kwargs
        self._default_reservoir = kwargs.get("reservoir")
        self._default_model_parameters = kwargs.get("model_parameters")

    def _run(self, **kwargs):
        """
        :param kwargs: Model specific keyword value parameters.
        """
        self.logger.debug(
            'Importing model specific configuration ...')
        # Simple chain map can combine parameters if they are a flat hierarchy
        # and in-place modification not required. otherwise see ChainMapTree
        # in parser.py.
        model_config = ChainMap(kwargs.get('model_parameters', {}),
                                self._default_model_parameters)

        self.logger.debug(
            'Received model configuration: {!r}'.format(model_config))

        ####
        # Validations on data
        try:
            end_training = model_config['em1_end_training']
        except KeyError:
            end_training = model_config['datetime_start']

        epoch_duration = model_config['epoch_duration']
        forecast_duration = (model_config['datetime_end'] -
                             model_config['datetime_start']).total_seconds()

        if epoch_duration > forecast_duration:
            self.logger.info("The epoch duration is less than the "
                             "total time of forecast")
            epoch_duration = forecast_duration
            self.logger.info("The epoch duration has been set to the"
                             f"forcast duration: {forecast_duration} (s)")

        self.logger.debug('Importing reservoir geometry ...')
        try:
            reservoir_geom = kwargs['reservoir']['geom']
        except KeyError:
            self.logger.info('No reservoir exists.')
            raise EM1Error("No reservoir provided.")

        ###
        # We have a quakeml catalog, convert so something the model
        # can process. In this case a pandas dataframe.
        self.logger.debug('Importing seismic catalog ...')
        try:
            catalog = obspy_catalog_parser(
                kwargs["seismic_catalog"]["quakeml"])
            self.logger.info(
                f'Received seismic catalog with {len(catalog)} event(s).')
        except KeyError:
            self.logger.warning(
                'Received catalog without quakeml key.')
            raise ValidationError('No quakeml key found for catalog.')

        ###
        # Remove events from catalog that are outside scope in space or time.
        catalog = self._filter_catalog(catalog, reservoir_geom,
                                       kwargs.get("spatialreference"),
                                       kwargs.get("referencepoint"))

        ###
        # Parse hydraulic data if required. Again imports only data required
        # into pandas dataframe. Any format required can be used.
        self.logger.debug('Importing real hydraulic data ...')
        try:
            hydraulics = hydraulics_parser(kwargs["well"])

            self.logger.info(
                'Received borehole ({} hydraulic sample(s)).'.format(
                    len(hydraulics)))
        except KeyError:
            raise EM1Error(
                'Received borehole without hydraulic samples.')

        self.logger.debug('Importing scenario hydraulic data...')
        ###
        # Import the hydraulics planned scenario (for the future)
        # into same format as observed data.
        try:
            hydraulics_scenario = hydraulics_parser(
                kwargs["scenario"]["well"])
            self.logger.info(
                'Received scenario ({} hydraulic sample(s)).'.format(
                    len(hydraulics_scenario)))
        except KeyError:
            raise EM1Error(
                'Received scenario without hydraulic samples.')

        self.logger.debug('Checking training period...')
        try:
            training_epoch_duration = model_config[
                'em1_training_epoch_duration']
        except KeyError:
            self.logger.info("No training_epoch_duration is set.")
            start_time_hydraulics = hydraulics.sort_index().index[0].\
                to_pydatetime()
            training_epoch_duration = (end_training - start_time_hydraulics).\
                total_seconds()

            if training_epoch_duration <= 0.:
                raise EM1Error("End of training set to before the "
                               "first training data hydraulic sample.")
            self.logger.info("Setting training_epoch_duration to: "
                             f"{training_epoch_duration}.")

        ### If model is not python, it would be here that a system call
        # to model would take place, with waiting enabled.
        self.logger.info("Calling the EM1 model...")
        try:
            a, b, mc, forecast_values = em1_model.exec_model(
                catalog,
                hydraulics,
                hydraulics_scenario,
                end_training,
                training_epoch_duration,
                model_config['em1_training_magnitude_bin'],
                model_config['em1_training_events_threshold'],
                model_config['datetime_start'],
                model_config['datetime_end'],
                epoch_duration)
        except Exception:
            # sarsonl This is not nice, but we need to raise an error twice
            # if one occurs in the model, best not to alter this apart to
            # change the name of the 'a' variable to something that needs
            # to be populated as a means of checking the result.
            err = traceback.print_exc()
            a = None
        else:
            err = False
        if err:
            raise
        # Quirk of set-up means that we need to raise another error.
        if not a:
            raise EM1Error('Error raised in EM1 model')

        self.logger.debug("Result received from EM1 model.")

        ###
        # Then the processing of results may take place so that they
        # can be read into the database.
        start_date = None

        samples = []
        for dttime, row in forecast_values.iterrows():
            if not start_date:
                start_date = dttime
                continue
            if row.volume <= 0.0 or np.isnan(row.volume):
                self.logger.warning(
                    f"Forecast for {start_date}:{dttime} is not being written "
                    f"as injected volume is {row.volume}")
                continue
            # (sarsonl) round floats as difference in
            # decimal places returned in sqlite/postgresql
            samples.append(orm.ModelResultSample(
                           starttime=start_date,
                           endtime=dttime,
                           # Rounding here for consistancy of results
                           # as different numerical limits apply to different
                           # databases. Not required to apply.
                           b_value=round(b, 10),
                           a_value=round(a, 10),
                           mc_value=round(mc, 10),
                           numberevents_value=row.N,
                           hydraulicvol_value=row.volume))
            start_date = dttime

        self.logger.info(f"{len(samples)} valid forecast samples")
        if model_config['em1_return_subgeoms']:
            reservoir = subgeoms_for_single_result(reservoir_geom,
                                                   samples)
        else:
            reservoir = single_reservoir_result(reservoir_geom,
                                                samples)
        ###
        # return a ModelResult object where reservoir holds all the
        # results in a hierachical format of ORM objects
        return ModelResult.ok(
            data={"reservoir": reservoir},
            warning=self.stderr if self.stderr else self.stdout)

    def _filter_catalog(self, catalog, geom, spatial_reference,
                        referencepoint):
        # Apply the reference point offset to the resrevoir.
        min_reservoir_height = min(geom["z"])
        max_reservoir_height = max(geom["z"])
        min_reservoir_x = min(geom["x"]) + referencepoint["x"]
        max_reservoir_x = max(geom["x"]) + referencepoint["x"]
        min_reservoir_y = min(geom["y"]) + referencepoint["y"]
        max_reservoir_y = max(geom["y"]) + referencepoint["y"]
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(*transform(min_reservoir_x,
                                min_reservoir_y,
                                spatial_reference))
        ring.AddPoint(*transform(min_reservoir_x,
                                max_reservoir_y,
                                spatial_reference))
        ring.AddPoint(*transform(max_reservoir_x,
                                max_reservoir_y,
                                spatial_reference))
        ring.AddPoint(*transform(max_reservoir_x,
                                 min_reservoir_y,
                                 spatial_reference))
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        poly.CloseRings()
        poly.FlattenTo2D()
        self.logger.info('Filtering catalog on latitude and longitude...{}'.format(poly.Area()))

        catalog = catalog[catalog.apply(self.filter_catalog_ogr, axis=1,
                                        args=[poly])]
        self.logger.info('After filtering on reservoir, seismic catalog '
                         f'contains: {len(catalog)} events')
        self.logger.info('Filtering catalog on depth')
        max_reservoir_depth = -min_reservoir_height
        min_reservoir_depth = -max_reservoir_height
        catalog = self.filter_catalog_depth(
            catalog, min_reservoir_depth, max_reservoir_depth)
        self.logger.info('After filtering on depth, seismic catalog '
                         f'contains: {len(catalog)} events')
        return catalog

    @staticmethod
    def filter_catalog_ogr(catalog, geom):
        event_loc = ogr.CreateGeometryFromWkt(
            f"POINT ({catalog['lon']} {catalog['lat']})")
        return geom.Contains(event_loc)

    @staticmethod
    def filter_catalog_depth(catalog, min_depth, max_depth):
        """
        The obspy filtering does not work for the third dimension
        for unexplained reasons (sfcgal library linked to gdal should support
        3D functionality, but this does not solve the problem)

        As a simplified work-around, the depth will be filtered by the
        geometry envelope, which means that the events with depth
        outside the minimum depth and maximum depth in the reservoir
        will be excluded. The expected geometry is of a cuboid.

        :param catalog: Catalog of seismic events
        :type catalog: pandas DataFrame
        :param geom: geometry of reservoir defined by a polyhedral suface
            of a cuboid shape.
        :type geom: ogr Geometry

        :rtype: pandas DataFrame
        """

        catalog = catalog[catalog.depth < max_depth]
        catalog = catalog[catalog.depth > min_depth]
        return catalog
