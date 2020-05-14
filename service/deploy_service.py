#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import yaml
from jinja2 import Template

from common.exception import ServerException
from model.project import Project
from service.k8s_service import K8sService
from service.template_service import TemplateService


class DeployService:

    @classmethod
    def deploy(cls, user, project_id, image_name):
        project = Project.select().get(project_id)
        if not K8sService.create_namespace(project.name, project.name):
            raise ServerException('创建空间失败')
        template = TemplateService.get_template_by_id(3)
        deploy_template = Template(template.get('content'))
        deploy_template_yaml = yaml.safe_load(deploy_template.render(project=project, image_name=image_name))
        response = K8sService.create_namespaced_deployment(
            name=project.name,
            namespace=project.name,
            body=deploy_template_yaml
        )
        # 创建service
        template = TemplateService.get_template_by_id(6)
        service_template = Template(template.get('content'))
        service_template_yaml = yaml.safe_load(service_template.render(project=project))
        service_response = K8sService.create_namespaced_service(
            namespace=project.name,
            name=project.name,
            body=service_template_yaml
        )
        # 创建ingress
        template = TemplateService.get_template_by_id(5)
        ingress_template = Template(template.get('content'))
        ingress_template_yaml = yaml.safe_load(ingress_template.render(project=project))
        # ingress service 删除发布会造成不可访问，需要探索修改
        ingress_response = K8sService.create_namespaced_ingress(
            namespace=project.name,
            name=project.name,
            body=ingress_template_yaml
        )
        return response

    @classmethod
    def replace(cls, name, namespace):
        pass

    @classmethod
    def list_pod_status(cls, project_id):
        project = Project.select().get(project_id)
        pod_status = K8sService.list_pod_status(namespace=project.name if project else None)
        return pod_status

    @classmethod
    def read_namespaced_pod_log(cls, name, namespace, previous):
        response = K8sService.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            previous=previous
        )
        return response
