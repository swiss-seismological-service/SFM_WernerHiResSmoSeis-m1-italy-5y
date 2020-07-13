# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
Service related schema facilities.
"""
from marshmallow import fields

from ramsis.sfm.worker.parser import ModelParameterSchemaBase, \
    create_sfm_worker_imessage_schema, UTCDateTime

# Note: Update all instances of WerHiResSmoM1Italy5y, wer_hires_smo_m1_italy_5y including the directory and import
# names to your model abbreviation.
#
# This file contains the model specific parameters or data that are not
# included by default in ramsis/sfm/worker/parser.py in
# ModelParameterSchemaBase.
# These are some examples of what could be required for a model, where
# The parsing is done by marshmallow. Logic can be included to pre process
# the incoming data, see file quoted above for examples of this.
#
# The parameters that are model specific are all prefixed with the model
# name so that it is recognizable which inputs are designed for the model.
# This is not a requirement, but it is helpful for distinction.


class WerHiResSmoM1Italy5yModelParameterSchema(ModelParameterSchemaBase):

    wer_hires_smo_m1_italy_5y_training_magnitude_bin = fields.Float()
    wer_hires_smo_m1_italy_5y_training_epoch_duration = fields.Float()
    wer_hires_smo_m1_italy_5y_end_training = UTCDateTime('utc_isoformat')
    wer_hires_smo_m1_italy_5y_training_events_threshold = fields.Integer()
    wer_hires_smo_m1_italy_5y_threshold_magnitude = fields.Float()
    wer_hires_smo_m1_italy_5y_return_subgeoms = fields.Boolean()


SFMWorkerIMessageSchema = create_sfm_worker_imessage_schema(
    model_parameters_schema=WerHiResSmoM1Italy5yModelParameterSchema)
