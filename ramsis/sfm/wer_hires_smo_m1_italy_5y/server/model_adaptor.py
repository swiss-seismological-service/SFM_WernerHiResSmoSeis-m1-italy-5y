# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
WerHiResSmoM1Italy5y model adaptor facilities.
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
from ramsis.sfm.wer_hires_smo_m1_italy_5y.core.utils import obspy_catalog_parser, hydraulics_parser
from ramsis.sfm.wer_hires_smo_m1_italy_5y.core import wer_hires_smo_m1_italy_5y_model

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
    WerHiResSmoM1Italy5y model implementation running the WerHiResSmoM1Italy5y model code. The class wraps up
    model specifc code providing a unique interface.

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

        mag_bin_list = nround(arange(model_config['model_mag_start'],
                                     model_config['model_mag_end'],
                                     model_config['model_mag_increment']), 1).to_list()
        ####
        # Validations on data
        epoch_duration = model_config['epoch_duration']
        forecast_duration = (model_config['datetime_end'] -
                             model_config['datetime_start']).total_seconds()

        if not epoch_duration:
            epoch_duration = forecast_duration
        elif epoch_duration > forecast_duration:
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
            raise WerHiResSmoM1Italy5yError("No reservoir provided.")

        self.logger.info("Calling the WerHiResSmoM1Italy5y model...")

        # Return arrays for each result attribute.
        try:
            a, b, mc, minmag, maxmag, forecast_values = wer_hires_smo_m1_italy_5y_model.exec_model(
                mag_bin_list,
                epoch_duration,
                reservoir_geom,
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
            raise WerHiResSmoM1Italy5yError('Error raised in WerHiResSmoM1Italy5y model')

        self.logger.debug("Result received from WerHiResSmoM1Italy5y model.")

        ###
        # Then the processing of results may take place so that they
        # can be read into the database.
        start_date = None

        samples = []
        for dttime, row in forecast_values.iterrows():
            if not start_date:
                start_date = dttime
                continue
            if row.a <= 0.0 or np.isnan(row.a):
                # Option to raise warning if we have zero seismicity
                continue

            samples.append(orm.ModelResultSample(
                           starttime=start_date,
                           endtime=dttime,
                           minmag=minmag,
                           maxmag=maxmag,
                           b_value=round(b, 10),
                           a_value=round(a, 10),
                           mc_value=round(mc, 10)))
            start_date = dttime

        self.logger.info(f"{len(samples)} valid forecast samples")
        if model_config['wer_hires_smo_m1_italy_5y_return_subgeoms']:
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
