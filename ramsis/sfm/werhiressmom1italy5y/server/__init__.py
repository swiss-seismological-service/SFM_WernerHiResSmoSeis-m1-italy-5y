# Copyright 2018, ETH Zurich - Swiss Seismological Service SED
"""
SFM-Worker (server) related general purpose utilities.
"""

import uuid

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app(config_dict={}):
    """
    Factory function for Flask application.

    :param :cls:`flask.Config config` flask configuration object
    """
    app = Flask(__name__)
    app.config.update(config_dict)
    db.init_app(app)

    # XXX(damb): Avoid circular imports.
    from ramsis.sfm.werhiressmom1italy5y.server.v1 import blueprint as api_v1_bp, API_VERSION_V1
    app.register_blueprint(
        api_v1_bp,
        url_prefix='/v{version}'.format(version=API_VERSION_V1))

    @app.before_request
    def generate_request_id():
        """
        Generate a unique request identifier.
        """
        g.request_id = uuid.uuid4()

    return app
