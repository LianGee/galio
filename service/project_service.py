#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : project_service.py
# @Author: zaoshu
# @Date  : 2020-04-09
# @Desc  :
import json
import random

import config
from common.config_util import ConfigUtil
from model.project import Project
from service.k8s_service import K8sService


class ProjectService:

    @classmethod
    def save(cls, data, user_name):
        if data.get('id') is None:
            project = Project.fill_model(Project(), data)
            project.user_name = user_name
            project.port = cls.generate_valid_node_port()
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
            project.nginx_proxies = json.loads(project.nginx_proxies or '[]')
            result = project.to_dict()
            results.append(result)
        return results

    @classmethod
    def query_project_by_id(cls, project_id):
        return Project.select().get(project_id)

    @classmethod
    def generate_valid_node_port(cls):
        services = K8sService.list_service()
        node_ports = []
        for service in services:
            if service.get('type') == 'NodePort':
                node_ports.extend([port.get('node_port') for port in service.get('ports')])
        k8s_node_port_range = ConfigUtil.get_dict_property(config.K8S_NODE_PORT_RANGE)
        all_valid_node_ports = [i for i in range(k8s_node_port_range[0], k8s_node_port_range[1])]
        valid_node_ports = list(set(all_valid_node_ports) ^ set(node_ports))
        return valid_node_ports[random.randint(0, len(valid_node_ports))]
