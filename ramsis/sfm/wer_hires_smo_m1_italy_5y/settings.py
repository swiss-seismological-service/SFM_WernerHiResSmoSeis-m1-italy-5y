# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
General purpose configuration constants.
"""

from ramsis.sfm.worker import settings

RAMSIS_WORKER_WerHiResSmoM1Italy5y_ID = 'WerHiResSmoM1Italy5y'
RAMSIS_WORKER_WerHiResSmoM1Italy5y_PORT = 5000
RAMSIS_WORKER_WerHiResSmoM1Italy5y_CONFIG_SECTION = 'CONFIG_SFM_WORKER_WerHiResSmoM1Italy5y'

PATH_RAMSIS_WerHiResSmoM1Italy5y_SCENARIOS = ('/' + RAMSIS_WORKER_WerHiResSmoM1Italy5y_ID +
                             settings.PATH_RAMSIS_WORKER_SCENARIOS)

# Configure defaults for the inputs parsed in the schema
# file. Defaults are not required, if not needed leave an
# empty dict here.
RAMSIS_WORKER_SFM_DEFAULTS = {
    "model_parameters": {
        "epoch_duration": 14400.0,
        "wer_hires_smo_m1_italy_5y_training_magnitude_bin": 0.2,
        "wer_hires_smo_m1_italy_5y_training_threshold_magnitude": 2.6,
        "wer_hires_smo_m1_italy_5y_training_events_threshold": 4.0,
        "wer_hires_smo_m1_italy_5y_return_subgeoms": False}}
