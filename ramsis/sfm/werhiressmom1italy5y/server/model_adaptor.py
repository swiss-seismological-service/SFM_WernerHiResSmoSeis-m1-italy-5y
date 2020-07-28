# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
WerHiResSmoM1Italy5y model adaptor facilities.
"""
import traceback
from collections import ChainMap
import numpy as np
from datetime import timedelta

from ramsis.sfm.worker import orm
from ramsis.sfm.worker.model_adaptor import \
    ModelAdaptor as _ModelAdaptor, ModelError, ModelResult
from ramsis.sfm.werhiressmom1italy5y.core import \
    werner_model

# Example of a model adaptor. This takes inputs from the base worker
# and converts data to something the model can consume. Further validations
# can also be done here.

# Subclassing of Error class, modify as required.
class WerHiResSmoM1Italy5yError(ModelError):
    """Base WerHiResSmoM1Italy5y model error ({})."""

class ValidationError(WerHiResSmoM1Italy5yError):
    """ValidationError ({})."""


class ModelAdaptor(_ModelAdaptor):
    """
    WerHiResSmoM1Italy5y model implementation running the
    model code. The class wraps up model specifc code providing
    a unique interface.

    :param str reservoir_geometry: Reservoir geometry used by default.
        WKT format.
    :param dict model_parameters: Dictionary of model parameters used by
        default.
    """

    LOGGER = 'ramsis.sfm.worker.model_adaptor'

    NAME = 'WerHiResSmoM1Italy5y'
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

        # Validations on data
        epoch_duration = model_config['epoch_duration']
        forecast_duration = (model_config['datetime_end'] - # noqa
                             model_config['datetime_start']).total_seconds()

        if not epoch_duration:
            epoch_duration = forecast_duration
        elif epoch_duration > forecast_duration:

            self.logger.info("The epoch duration is less than the "
                             "total time of forecast")
            epoch_duration = forecast_duration
            self.logger.info("The epoch duration has been set to the"
                             f"forcast duration: {forecast_duration} (s)")
        datetime_list = [model_config['datetime_start'] + # noqa
                         timedelta(seconds=int(epoch_duration * i))
                         for i in range(
                             int(forecast_duration // epoch_duration) + 1)]

        self.logger.debug('Importing reservoir geometry ...')
        try:
            reservoir_geom = kwargs['reservoir']['geom']
        except KeyError:
            self.logger.info('No reservoir exists.')
            raise WerHiResSmoM1Italy5yError("No reservoir provided.")

        self.logger.info("Calling the WerHiResSmoM1Italy5y model...")

        # Return arrays for each result attribute.
        try:
            (forecast_values,
             mag_list,
             mc,
             depth_km) = werner_model.exec_model(
                reservoir_geom)
        except Exception:
            # sarsonl This is not nice, but we need to raise an error twice
            # if one occurs in the model to get a sensible traceback statement
            err = traceback.print_exc()
            forecast_values = None
        else:
            err = False
        if err:
            raise
        # Quirk of set-up means that we need to raise another error.
        if forecast_values is None:
            raise WerHiResSmoM1Italy5yError(
                'Error raised in WerHiResSmoM1Italy5y model')

        self.logger.debug("Result received from WerHiResSmoM1Italy5y model.")

        # Read values into database
        min_mag = min(mag_list)
        max_mag = max(mag_list)
        # Assume that the increment between bins is static and positive
        mag_increment = round(float(mag_list[1]) - float(mag_list[0]), 1)
        subgeoms = []
        samples = []
        for index, row in forecast_values.iterrows():
            # Validate the depths list in the parsing stage.
            for min_depth, max_depth in \
                    zip(reservoir_geom['z'], reservoir_geom['z'][1:]):
                depth_fraction = (max_depth - min_depth) / (depth_km * 1000.0)
                samples = []
                for start_date, end_date in zip(datetime_list,
                                                datetime_list[1:]):
                    result_bins = []
                    for mag_bin in mag_list:
                        event_number = row[mag_bin]/depth_fraction
                        result_bins.append(orm.MFDBin(
                            referencemagnitude=mag_bin,
                            eventnumber_value=event_number,
                            # Question: a variance/uncertainty at this level
                            # won't propagate to OQ hazard, so what would
                            # be preferential to store, given the
                            # choice between:
                            # uncertainty/variance/confidencelevel/any?
                            eventnumber_uncertainty=np.sqrt(event_number)))

                    mfd_curve = orm.DiscreteMFD(
                        minmag=min_mag,
                        maxmag=max_mag,
                        binwidth=mag_increment,
                        magbins=result_bins)

                    samples.append(orm.ModelResultSample(
                                   starttime=start_date,
                                   endtime=end_date,
                                   mc_value=mc,
                                   discretemfd=mfd_curve))

                subgeom = orm.Reservoir(
                    x_min=row['min_lon'],
                    x_max=row['max_lon'],
                    y_min=row['min_lat'],
                    y_max=row['max_lat'],
                    z_min=min_depth,
                    z_max=max_depth,
                    samples=samples)

                subgeoms.append(subgeom)

        # Top level reservoir contains the total dimensions of the
        # requested search area.
        reservoir = orm.Reservoir(
            x_min=min(reservoir_geom['x']),
            x_max=max(reservoir_geom['x']),
            y_min=min(reservoir_geom['y']),
            y_max=max(reservoir_geom['y']),
            z_min=min(reservoir_geom['z']),
            z_max=max(reservoir_geom['z']),
            subgeometries=subgeoms)
        self.logger.info(f"{len(samples)} valid forecast samples")

        return ModelResult.ok(
            data={"reservoir": reservoir},
            warning=self.stderr if self.stderr else self.stdout)
