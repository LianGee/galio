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
ENV = env_util.get_env()
JSONIFY_PRETTYPRINT_REGULAR = True
JSON_AS_ASCII = False
DEBUG = False
ADDRESS = '0.0.0.0'
PORT = 8010
WORKERS = 4
FLASK_USE_RELOAD = True if env_util.is_dev() else False
BASE_DIR = os.path.abspath(os.getcwd())

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
SOCKET_BUILD_NAMESPACE = ConfigUtil.get_str_property('socket.build.namespace')
SOCKET_DEPLOY_NAMESPACE = ConfigUtil.get_str_property('socket.deploy.namespace')
# app config key
CAS_URL = 'cas.url'
FRONT_URL = 'front.url'
SERVER_URL = 'server.url'

# code_path
GIT_WORKSPACE = 'git.workspace'

# query max size
QUERY_MAX_SIZE = 'query.max.size'

# kubernetes auth key
K8S_HOST = 'k8s.host'
K8S_SEC = 'k8s.secret'
K8S_POD_LOG_LENGTH = 'k8s.pod.log.length'
K8S_NODE_PORT_RANGE = 'k8s.node.port.range'

# domain
DOMAIN_EXTERNAL = 'domain.external'
DOMAIN_INTERNAL = 'domain.internal'
