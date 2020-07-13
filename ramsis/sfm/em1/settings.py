# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
General purpose configuration constants.
"""

from ramsis.sfm.worker import settings

RAMSIS_WORKER_EM1_ID = 'EM1'
RAMSIS_WORKER_EM1_PORT = 5000
RAMSIS_WORKER_EM1_CONFIG_SECTION = 'CONFIG_SFM_WORKER_EM1'

PATH_RAMSIS_EM1_SCENARIOS = ('/' + RAMSIS_WORKER_EM1_ID +
                             settings.PATH_RAMSIS_WORKER_SCENARIOS)

# Configure defaults for the inputs parsed in the schema
# file. Defaults are not required, if not needed leave an
# empty dict here.
RAMSIS_WORKER_SFM_DEFAULTS = {
    "model_parameters": {
        "epoch_duration": 14400.0,
        "em1_training_magnitude_bin": 0.2,
        "em1_training_threshold_magnitude": 2.6,
        "em1_training_events_threshold": 4.0,
        "em1_return_subgeoms": False}}
