"""
WerHiResSmoM1Italy5y model code that uses hydraulic borehole data and a seismicity catalog
to forecast the number of events above a certain magnitude based on a
hydraulics plan.
"""

# Note: Please change all references to WerHiResSmoM1Italy5y, wer_hires_smo_m1_italy_5y to what your model name
# abbreviation should be.

# This model has been implemented in python, however it is not required
# to be in python. If it is in another language, a system call will probably
# be made from the ../server/model_adaptor.py to your model. Your model
# may require alterations to what data is available from RAMSIS, so the
# example model adaptor may provide a guide to you on what default
# functions are availble.

import argparse
import logging
from datetime import datetime

from ramsis.sfm.wer_hires_smo_m1_italy_5y.core.error import (SeismicEventThresholdError,
                                       NegativeVolumeError)

LOGGER = 'ramsis.sfm.wer_hires_smo_m1_italy_5y_model'
NAME = 'WerHiResSmoM1Italy5yMODEL'
logger = logging.getLogger(LOGGER)

###
# Imput model code here if implemented in python.
#
# The full implementation of how WerHiResSmoM1Italy5y was implemented can be found:
# https://gitlab.seismo.ethz.ch/indu/ramsis.sfm.wer_hires_smo_m1_italy_5y/-/blob/feature/model_code/ramsis/sfm/wer_hires_smo_m1_italy_5y/core/wer_hires_smo_m1_italy_5y_model.py
#
# Please note that the inputs to this model were transformed into pandas dataframes.
# This is not a requirement for models but was the chosen method for WerHiResSmoM1Italy5y as it
# improved data handling. The model_adaptor.py file referenced above handles
# the transformation from the incoming data to something that the model can
# handle.
###


# Please see ../server/model_adaptor.py for where this is called
# What inputs are requires are entirely dependant on model.
def exec_model(catalog,
               hydraulics,
               hydraulics_plan,
               end_training,
               training_epoch_duration,
               training_magnitude_bin,
               training_events_threshold,
               datetime_start,
               datetime_end,
               epoch_duration):
    """
    Run the model training and forecast stages.

    :param catalog: Catalog of seismicity containing all seismicity between
        the dates end_training and end_training - training_epoch_duration.
    :param: hydraulics: Hydraulic measurements of the volume flowing into
        the well between the dates of end_training and
        end_training - training_epoch_duration
    :param: hydraulics_plan: Hydraulic plan of the volume flowing into
        the well between the dates of datetime_start and
        datetime_end
    :param training_epoch_duration: Time to train parameters for.
    :param training_magnitude_bin: Binning width in dB for seismic activity.
    :param training_events_threshold: Number of events threshold to
        return values
    :param datetime_start: Start of period to forecast.
    :param datetime_end: End of period to forecast.
    :param epoch_duration: Number of seconds between returned forecast
        rate values.

    :rtypes: (a) float, (b) float, (mc) float, (forecast_values) pd.DataFrame
    """
    # Call code to train model on seismic catalog/hydraulic data if required
    # Results here are Gutenberg-richter quantities that can be plugged
    # into next section.
    a, b, mc, hydraulics_cumulated= train_on_hydraulics(
        catalog, hydraulics, end_training, training_epoch_duration,
        training_magnitude_bin, training_events_threshold)
    logger.info("Completed training")
    # If using hydraulic data, it is usually expected to interpolate between
    # the last point in the observed data and the first point in the
    # injection plan data.
    last_hydraulic_row = hydraulics_cumulated.loc[:datetime_start].tail(1)
    logger.info(f"Starting point for hydraulics: {last_hydraulic_row}")
    # Call the forecasting model for the planned time period using the trained
    # model parameters.
    forecast_values = forecast_seismicity(
        a, b, mc, hydraulics_plan, datetime_start,
        datetime_end, epoch_duration,
        last_hydraulic_row=last_hydraulic_row)
    logger.info("Completed forecast")
    return a, b, mc, forecast_values

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%s")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('datetime_start', type=valid_date,
                        help='Start date for forecast, YYYYmmDDTHHMMss')
    parser.add_argument('datetime_end', type=valid_date,
                        help='End date for forecast, YYYYmmDDTHHMMss')
    parser.add_argument('epoch_duration', type=float,
                        help='Time between forecasts in seconds')
    parser.add_argument('training__epoch_duration', type=float,
                        help='Number of seconds to train for. If None, looks'
                        ' back over full seismic catalog')
    parser.add_argument('training_magnitude_bin', type=float,
                        help='Value in dB for binning seismic magnitudes')
    parser.add_argument('training_events_threshold', type=int,
                        help='number of events required within a forecast'
                        ' time window')
    parser.add_argument('catalog', type=list,
                        help='Catalog of seismic events from same'
                        ' period as hydraulic_input. List of tuples.'
                        ' e.g.[(date, {lat: 10.2, lon: 10.2,'
                        ' depth: 0, mag: 4.5})]')
    parser.add_argument('hydraulics', type=list,
                        help='Hydraulic sample data from the past, from same'
                        ' period as seismic catalog. list of tuples'
                        ' e.g. [(date, {flow_dh: 10.2, flow_xt: 10.2, '
                        'pressure_dh: 0, pressure_xt: 4.5})]')
    parser.add_argument('hydraulics_scenario',
                        help='Hydraulic sample data planned for the future.'
                        ' of same construct as hydraulic_input')
    parser.add_argument('end_training', type=valid_date,
                        help='End of training datetime.')
    args = parser.parse_args()
    return args


# It is not required to make the file executable, however nice to have for running
# independently.
if __name__ == "__main__":
    args = parseargs()
    results = exec_model(args.catalog,
                         args.hydraulics,
                         args.hydraulics_scenario,
                         args.end_training,
                         args.training_epoch_duration,
                         args.training_magnitude_bin,
                         args.training_events_threshold,
                         args.datetime_start,
                         args.datetime_end,
                         args.epoch_duration)
