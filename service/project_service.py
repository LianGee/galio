#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : project_service.py
# @Author: zaoshu
# @Date  : 2020-04-09
# @Desc  :
import json

import config
from common.config_util import ConfigUtil
from model.project import Project
from service.domain_service import DomainService


class ProjectService:

    @classmethod
    def save(cls, data, user_name):
        if data.get('id') is None:
            project = Project.fill_model(Project(), data)
            project.user_name = user_name
            project.port = DomainService.generate_valid_node_port()
            project.domain = f'{project.name}.{ConfigUtil.get_str_property(config.DOMAIN_EXTERNAL)}'
            project.service_domain = f'{project.namespace}.{project.name}.' \
                f'{ConfigUtil.get_str_property(config.DOMAIN_INTERNAL)}'
            project.nginx_proxies = json.dumps(project.nginx_proxies, ensure_ascii=False)
            project.insert()
            return Project.select().filter(Project.name == data.get('name')).one().id
        else:
            project = Project.select().get(data.get('id'))
            project = Project.fill_model(project, data)
            project.user_name = user_name
            project.nginx_proxies = json.dumps(project.nginx_proxies, ensure_ascii=False)
            project.update()
            return data.get('id')

    @classmethod
    def list(cls, user_name):
        projects = Project.select().filter(Project.user_name == user_name).all()
        results = []
        for project in projects:
            result = project.to_dict()
            results.append(result)
        return results
