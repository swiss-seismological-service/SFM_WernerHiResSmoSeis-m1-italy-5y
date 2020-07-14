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

#### Implement model
# Read xml file into structure searchable by lat, lon.
# for bin in reservoir, check minlat, minlon, maxlat, maxlon
# against data by returning datapoints that overlap with region
# and the fraction of overlap.
#
# Write data to various arrays.


# Please see ../server/model_adaptor.py for where this is called
# What inputs are requires are entirely dependant on model.
def exec_model(mag_bin_list,
               epoch_duration,
               reservoir_geom,
               datetime_start,
               datetime_end,
               epoch_duration)
    """
    Run the model training and forecast stages.

    :param datetime_start: Start of period to forecast.
    :param datetime_end: End of period to forecast.
    :param epoch_duration: Number of seconds between returned forecast
        rate values.
    # TODO

    :rtypes: (a) float, (b) float, (mc) float, (forecast_values) pd.DataFrame
    """
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
    args = parser.parse_args()
    return args


# It is not required to make the file executable, however nice to have for running
# independently.
if __name__ == "__main__":
    args = parseargs()
    results = exec_model(args.datetime_start,
                         args.datetime_end,
                         args.epoch_duration)
