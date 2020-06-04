#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_namespace.py
# @Author: zaoshu
# @Date  : 2020-06-04
# @Desc  : 
from datetime import datetime

from flask_socketio import Namespace, emit

import config


class DeployNamespace(Namespace):

    def __init__(self, namespace):
        super(DeployNamespace, self).__init__(namespace=namespace)

    def on_connect(self):
        self.console('connect')

    def console(self, message):
        emit('console', f"[{datetime.now().strftime('%y-%m-%d %H:%M:%S')}]-{message}")


deploy_namespace = DeployNamespace(namespace=config.SOCKET_DEPLOY_NAMESPACE)
