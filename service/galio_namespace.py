#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : galio_namespace.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
from datetime import datetime

from flask_socketio import Namespace, emit

import config
from common.config_util import ConfigUtil
from model.build import BuildLog
from model.project import Project
from service.build_service import BuildService


class GalioNamespace(Namespace):

    def __init__(self, namespace):
        super(GalioNamespace, self).__init__(namespace=namespace)

    def on_connect(self):
        self.console('connect')

    def on_build_ping(self, message):
        build_log = BuildLog.select().filter(
            BuildLog.user_name == message.get('name')
        ).order_by(BuildLog.created_at.desc()).first()
        emit('build_pong', build_log.to_dict())

    def on_build(self, message):
        project_id = message.get('project_id')
        branch = message.get('branch')
        project = Project.select().get(project_id)
        build_service = BuildService(
            workspace=ConfigUtil.get_str_property(config.GIT_WORKSPACE),
            project=project,
            branch=branch,
            user=message.get('user'),
            console=self.console
        )
        build_service.build()

    def console(self, message):
        emit('console', f"[{datetime.now().strftime('%y-%m-%d %H:%M:%S')}]-{message}")


galio_namespace = GalioNamespace(namespace=config.SOCKET_NAMESPACE)
