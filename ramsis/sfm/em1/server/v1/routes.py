# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
EM1 resource facilities.
"""
from flask_restful import Api

from ramsis.sfm.em1 import settings
from ramsis.sfm.em1.server import db
from ramsis.sfm.em1.server.model_adaptor import ModelAdaptor
from ramsis.sfm.em1.server.v1 import blueprint
from ramsis.sfm.em1.server.v1.schema import SFMWorkerIMessageSchema
from ramsis.sfm.worker.parser import parser
from ramsis.sfm.worker.resource import (SFMRamsisWorkerResource,
                                        SFMRamsisWorkerListResource)

api_v1 = Api(blueprint)

# Note: Update all instances of EM1, em1 including the directory and import
# names to your model abbreviation.
#
# This file contains the possible routes for the API.
# These two routes are for a GET request to inquire about the status and
# results of a task, and a POST request to trigger a task to be created and
# the model run with provided data.
# So far only two routes are required for interation with RAMSIS, but more
# can be configured for other purposes.
# Each route has an attached resource which is required for the logic behind
# each call.

class EM1API(SFMRamsisWorkerResource):
    """
    Concrete implementation of an asynchronous EM1 worker resource.

    This route is used with a GET call to the API and produces
    a task status and results if available, or an error message
    when used with a task_id (see the add_resource calls at the
    bottom of the file).
    """

    LOGGER = 'ramsis.sfm.worker.em1_api'


class EM1ListAPI(SFMRamsisWorkerListResource):
    """
    Concrete implementation of an asynchronous EM1 worker resource.

    This route is configured for a POST call to the API with json
    data and returns a message saying task accepted with a task id,
    or error code and message.
    :param model: Model to be handled by :py:class:`EM1ListAPI`.
    :type model: :py:class:`ramsis.sfm.worker.em1.server.model.EM1Model`
    """
    LOGGER = 'ramsis.sfm.worker.em1_list_api'

    def _parse(self, request, locations=('json', )):
        p = parser.parse(SFMWorkerIMessageSchema(), request,
                         locations=locations)
        return p


api_v1.add_resource(EM1API,
                    '{}/<task_id>'.format(settings.PATH_RAMSIS_EM1_SCENARIOS),
                    resource_class_kwargs={
                        'db': db})

api_v1.add_resource(EM1ListAPI,
                    settings.PATH_RAMSIS_EM1_SCENARIOS,
                    resource_class_kwargs={
                        'model': ModelAdaptor,
                        'db': db})
