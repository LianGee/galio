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
from service.k8s_service import K8sService


class DeployNamespace(Namespace):

    def __init__(self, namespace):
        super(DeployNamespace, self).__init__(namespace=namespace)

    def on_replica(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_replica(project_id, send_replica=self.send_replica)

    def on_pod(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_pod(project_id, send_pod=self.send_pod)

    def on_event(self, message):
        project_id = message.get('project_id')
        DeployService.list_project_event(project_id, send_event=self.send_event)

    def on_log(self, message):
        namespace = message.get('namespace')
        name = message.get('name')
        previous = message.get('previous', False)
        trace = message.get('trace')
        tail_lines = message.get('tail_lines')
        K8sService.get_namespaced_pod_log(
            name=name,
            namespace=namespace,
            trace=trace,
            previous=previous,
            tail_lines=tail_lines,
            send_log=self.send_log
        )

    def send_replica(self, data):
        emit('replica', data)

    def send_pod(self, data):
        emit('pod', data)

    def send_event(self, data):
        emit('event', data)

    def send_log(self, data):
        emit('log', data)


deploy_namespace = DeployNamespace(namespace=config.SOCKET_DEPLOY_NAMESPACE)
