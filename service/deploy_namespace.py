#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_namespace.py
# @Author: zaoshu
# @Date  : 2020-06-04
# @Desc  : 
from datetime import datetime

from flask_socketio import Namespace, emit

import config
from service.deploy_service import DeployService


class DeployNamespace(Namespace):

    def __init__(self, namespace):
        super(DeployNamespace, self).__init__(namespace=namespace)

    def on_connect(self):
        self.console('connect')

    def console(self, message):
        emit('console', f"[{datetime.now().strftime('%y-%m-%d %H:%M:%S')}]-{message}")

    def on_replica(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_replica(project_id, send_replica=self.send_replica)

    def on_pod(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_pod(project_id, send_pod=self.send_pod)

    def on_event(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_event(project_id, send_event=self.send_event)

    def send_replica(self, data):
        emit('replica', data)

    def send_pod(self, data):
        emit('pod', data)

    def send_event(self, data):
        emit('event', data)


deploy_namespace = DeployNamespace(namespace=config.SOCKET_DEPLOY_NAMESPACE)