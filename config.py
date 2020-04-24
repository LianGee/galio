#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  :

import os

from redis import Redis

from common import env_util
from common.config_util import ConfigUtil

APP_NAME = 'galio'
SECRET_KEY = 'XKCWJC6KN99GRZPOYDJTALF45WG3RNQ9'
JSONIFY_PRETTYPRINT_REGULAR = True
JSON_AS_ASCII = False
DEBUG = True
ADDRESS = '0.0.0.0'
PORT = 8010
WORKERS = 1
FLASK_USE_RELOAD = True
BASE_DIR = os.path.abspath(os.getcwd())
ENV = env_util.get_env()

# server config
DEFAULT_DATABASE_URL = ConfigUtil.get_str_property('DEFAULT_DATABASE_URL')
DB_KWARGS = ConfigUtil.get_dict_property('DB_KWARGS')
DATABASES = {
    "default": DEFAULT_DATABASE_URL,
}
SESSION_TYPE = 'redis'
SESSION_REDIS = Redis(
    host=ConfigUtil.get_str_property(key='redis.host'),
    port=ConfigUtil.get_int_property(key='redis.port')
)
SESSION_USE_SIGNER = True
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = ConfigUtil.get_int_property('PERMANENT_SESSION_LIFETIME')
REDIS_CACHE = ConfigUtil.get_dict_property('REDIS_CACHE')
# socket
SOCKET_NAMESPACE = ConfigUtil.get_str_property('socket.namespace')

# app config key
CAS_URL = 'cas.url'
FRONT_URL = 'front.url'
SERVER_URL = 'server.url'

# workspace
GIT_WORKSPACE = 'git.workspace'

# qiniu
QINIU_ACCESS_KEY = 'qiniu.access_key'
QINIU_SECRET_KEY = 'qiniu.secret_key'
QINIU_GALIO_BUCKET = 'qiniu.galio.bucket'
QINIU_GALIO_DOMAIN = 'qiniu.galio.domain'

# query max size
QUERY_MAX_SIZE = 'query.max.size'

# kubernetes auth key
K8S_HOST = 'k8s.host'
K8S_SEC = 'k8s.secret'
K8S_POD_LOG_LENGTH = 'k8s.pod.log.length'
