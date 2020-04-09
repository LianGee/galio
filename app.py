import traceback

from flask import Flask, request
from flask_cors import CORS

import config
from common.log import Logger
from common.response import Response
from model.db import clean_db_session
from view.user import user_bp

app = Flask(__name__)
log = Logger(__name__)
app.config.from_object(config)
CORS(app, supports_credentials=True)
app.register_blueprint(user_bp, url_prefix='/user')


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
