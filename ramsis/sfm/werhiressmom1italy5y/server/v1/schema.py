# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
Service related schema facilities.
"""
from marshmallow import fields

from ramsis.sfm.worker.parser import ModelParameterSchemaBase, \
    create_sfm_worker_imessage_schema, UTCDateTime


class WerHiResSmoM1Italy5yModelParameterSchema(ModelParameterSchemaBase):

    model_training_epoch_duration = fields.Float()
    model_end_training = UTCDateTime('utc_isoformat')
    model_training_events_threshold = fields.Integer()
    model_threshold_magnitude = fields.Float()


SFMWorkerIMessageSchema = create_sfm_worker_imessage_schema(
    model_parameters_schema=WerHiResSmoM1Italy5yModelParameterSchema)
