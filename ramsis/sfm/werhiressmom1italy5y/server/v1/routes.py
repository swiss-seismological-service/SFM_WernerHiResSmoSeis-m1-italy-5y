# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
WerHiResSmoM1Italy5y resource facilities.
"""
from flask_restful import Api

from ramsis.sfm.werhiressmom1italy5y import settings
from ramsis.sfm.werhiressmom1italy5y.server import db
from ramsis.sfm.werhiressmom1italy5y.server.model_adaptor import ModelAdaptor
from ramsis.sfm.werhiressmom1italy5y.server.v1 import blueprint
from ramsis.sfm.werhiressmom1italy5y.server.v1.schema import create_sfm_worker_imessage_schema
from ramsis.sfm.worker.parser import parser
from ramsis.sfm.worker.resource import (SFMRamsisWorkerResource,
                                        SFMRamsisWorkerListResource)
api_v1 = Api(blueprint)

parser_config = settings.PARSER_CONFIG
SFMWorkerIMessageSchema = create_sfm_worker_imessage_schema(config=parser_config)


class WerHiResSmoM1Italy5yAPI(SFMRamsisWorkerResource):
    """
    Concrete implementation of an asynchronous WerHiResSmoM1Italy5y worker resource.

    This route is used with a GET call to the API and produces
    a task status and results if available, or an error message
    when used with a task_id (see the add_resource calls at the
    bottom of the file).
    """

    LOGGER = 'ramsis.sfm.worker.wer_hires_smo_m1_italy_5y_api'


class WerHiResSmoM1Italy5yListAPI(SFMRamsisWorkerListResource):
    """
    Concrete implementation of an asynchronous WerHiResSmoM1Italy5y worker resource.

    This route is configured for a POST call to the API with json
    data and returns a message saying task accepted with a task id,
    or error code and message.
    :param model: Model to be handled by :py:class:`WerHiResSmoM1Italy5yListAPI`.
    :type model: :py:class:`ramsis.sfm.worker.wer_hires_smo_m1_italy_5y.server.model.WerHiResSmoM1Italy5yModel`
    """
    LOGGER = 'ramsis.sfm.worker.wer_hires_smo_m1_italy_5y_list_api'

    def _parse(self, request, locations=('json', )):
        p = parser.parse(SFMWorkerIMessageSchema(), request,
                         locations=locations)
        return p



api_v1.add_resource(WerHiResSmoM1Italy5yAPI,
                    '{}/<task_id>'.format(settings.PATH_RAMSIS_WerHiResSmoM1Italy5y_SCENARIOS),
                    resource_class_kwargs={
                        'db': db})

api_v1.add_resource(WerHiResSmoM1Italy5yListAPI,
                    settings.PATH_RAMSIS_WerHiResSmoM1Italy5y_SCENARIOS,
                    resource_class_kwargs={
                        'model': ModelAdaptor,
                        'db': db})
