import traceback

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

import config
from service.deploy_namespace import deploy_namespace
from service.build_namespace import build_namespace
from common.logger import Logger
from common.response import Response
from model.db import clean_db_session
from view.build import build_bp
from view.cloud_host import cloud_host_bp
from view.db_inst import db_inst_bp
from view.deploy import deploy_bp
from view.docker import docker_bp
from view.domain import domain_bp
from view.k8s import k8s_bp
from view.project import project_bp
from view.template import template_bp
from view.user import user_bp

app = Flask(__name__)
log = Logger(__name__)
app.config.from_object(config)
CORS(app, supports_credentials=True)
socketio = SocketIO(
    app,
    engineio_logger=True,
    logger=True,
    cors_allowed_origins='*',
)

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(project_bp, url_prefix='/project')
app.register_blueprint(build_bp, url_prefix='/build')
app.register_blueprint(template_bp, url_prefix='/template')
app.register_blueprint(db_inst_bp, url_prefix='/db_inst')
app.register_blueprint(k8s_bp, url_prefix='/k8s')
app.register_blueprint(docker_bp, url_prefix='/docker')
app.register_blueprint(deploy_bp, url_prefix='/deploy')
app.register_blueprint(domain_bp, url_prefix='/domain')
app.register_blueprint(cloud_host_bp, url_prefix='/cloud_host')


@app.before_request
def before_request():
    log.info(request)


@app.after_request
def after_request(response):
    if response.json:
        log.info(response)
    return response


@app.teardown_request
def teardown_request(error):
    clean_db_session()
    if error is not None:
        log.error(error)


@app.errorhandler(Exception)
def error_handler(exception: Exception):
    if exception:
        log.error(traceback.format_exc())
        return Response.failed(msg=f'{exception}')


@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.png')


socketio.on_namespace(build_namespace)
socketio.on_namespace(deploy_namespace)

if __name__ == '__main__':
    socketio.init_app(app, async_mode='gevent')
    socketio.run(
        app,
        use_reloader=config.FLASK_USE_RELOAD,
        debug=config.DEBUG,
        host='0.0.0.0',
        port=config.PORT
    )
