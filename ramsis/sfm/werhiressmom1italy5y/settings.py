# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
General purpose configuration constants.
"""
from numpy import arange
from numpy import round as nround
from ramsis.sfm.worker import settings

RAMSIS_WORKER_WerHiResSmoM1Italy5y_ID = 'WerHiResSmoM1Italy5y'
RAMSIS_WORKER_WerHiResSmoM1Italy5y_PORT = 5000
RAMSIS_WORKER_WerHiResSmoM1Italy5y_CONFIG_SECTION = 'CONFIG_SFM_WORKER_WerHiResSmoM1Italy5y'

PATH_RAMSIS_WerHiResSmoM1Italy5y_SCENARIOS = ('/' + RAMSIS_WORKER_WerHiResSmoM1Italy5y_ID +
                             settings.PATH_RAMSIS_WORKER_SCENARIOS)


# choose how data is handled when input to
# ramsis.sfm.worker.parser._SFMWorkerRunsAttributesSchema.
# options: required, optional, ignored, not_allowed
PARSER_CONFIG = {
    "seismic_catalog": "ignored",
    "well": "ignored",
    "scenario": "ignored"}

# Reservoir default is that already implemented by CSEP as the standard Italy
# grid.
lon_min = 5.55
lon_max = 19.45
lat_min = 35.85
lat_max = 47.85
lon_increment = 0.1
lat_increment = 0.1
z_max = 0.0
z_min = -30000.0

mag_start = 4.95
mag_end = 9.05
mag_increment = 0.1

# avoid precision errors by rounding.
lon_list = nround(arange(lon_min, lon_max, lon_increment), 2).tolist()
lat_list = nround(arange(lat_min, lat_max, lat_increment), 2).tolist()

RAMSIS_WORKER_SFM_DEFAULTS = {
    "reservoir": {"geom": {"x": lon_list,
                           "y": lat_list,
                           "z": [z_min, z_max]}},
    "model_parameters": {
        # If epoch_duration is None, will make single forecast for the whole
        # time between dateime_start and datetime_end
        "epoch_duration": None,
        "model_min_mag": mag_start,
        "model_max_mag": mag_end,
        "mag_increment": mag_increment}}
