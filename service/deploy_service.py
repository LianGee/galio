#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import json

import yaml
from jinja2 import Template

from common.constant import DeployStatus
from common.exception import ServerException
from common.logger import Logger
from model.deploy_log import DeployLog
from model.project import Project
from service.k8s_service import K8sService
from service.template_service import TemplateService

log = Logger(__name__)


class DeployService:

    @classmethod
    def deploy(cls, user, project_id, image_name):
        project = Project.select().get(project_id)
        deploy_log = DeployLog(
            project_name=project.name,
            project_id=project_id,
            image_name=image_name,
            user_name=user.name,
            status=DeployStatus.INIT
        )
        log.info(f'{deploy_log.uuid}:{user.name}正在发布{project.name} 镜像 {image_name}')
        try:
            if not K8sService.create_namespace(project.name, project.name):
                raise ServerException('创建空间失败')
            log.info(f'{deploy_log.uuid}:namespace {project.namespace} 校验成功')
            deploy_log.status = DeployStatus.NAMESPACE
            template = TemplateService.get_template_by_id(project.deployment_template_id)
            deploy_template = Template(template.content)
            deploy_template_yaml = yaml.safe_load(deploy_template.render(project=project, image_name=image_name))
            log.info(f'{deploy_log.uuid}:发布镜像{json.dumps(deploy_template_yaml, indent=2)}')
            deployment_response = K8sService.create_namespaced_deployment(
                name=project.name,
                namespace=project.name,
                body=deploy_template_yaml
            )
            log.info(f'{deploy_log.uuid}:镜像发布成功{deployment_response}')
            deploy_log.status = DeployStatus.DEPLOYMENT
            # 创建service
            template = TemplateService.get_template_by_id(project.svc_template_id)
            service_template = Template(template.content)
            service_template_yaml = yaml.safe_load(service_template.render(project=project))
            log.info(f'{deploy_log.uuid}:发布service {json.dumps(service_template_yaml, indent=2)}')
            service_response = K8sService.create_namespaced_service(
                namespace=project.name,
                name=project.name,
                body=service_template_yaml
            )
            log.info(f'{deploy_log.uuid}:service发布成功{service_response}')
            deploy_log.status = DeployStatus.SERVICE
            # 创建ingress
            template = TemplateService.get_template_by_id(project.ingress_template_id)
            ingress_template = Template(template.content)
            ingress_template_yaml = yaml.safe_load(ingress_template.render(project=project))
            # ingress service 删除发布会造成不可访问，需要探索修改
            log.info(f'{deploy_log.uuid}:发布ingress {json.dumps(ingress_template_yaml, indent=2)}')
            ingress_response = K8sService.create_namespaced_ingress(
                namespace=project.name,
                name=project.name,
                body=ingress_template_yaml
            )
            log.info(f'{deploy_log.uuid}:ingress发布成功{ingress_response}')
            deploy_log.status = DeployStatus.INGRESS
            return True
        except Exception as e:
            deploy_log.reason = e
        finally:
            deploy_log.insert()

    @classmethod
    def replace(cls, name, namespace):
        pass

    @classmethod
    def get_label_selector(cls, project_id):
        project = Project.select().get(project_id)
        deployments = K8sService.get_deployment_by_project(project)
        if len(deployments) == 0:
            return None, project
        match_labels = deployments[0].get('match_labels', {})
        return ','.join(list(map(lambda key: f'{key}={match_labels.get(key)}', match_labels))), project

    @classmethod
    def list_project_replica(cls, project_id, send_replica):
        label_selector, project = cls.get_label_selector(project_id)
        K8sService.get_labeled_replicas(label_selector, send_replica=send_replica)

    @classmethod
    def list_project_pod(cls, project_id, send_pod):
        label_selector, project = cls.get_label_selector(project_id)
        K8sService.get_namespace_labeled_pods(project.namespace, label_selector, send_pod)

    @classmethod
    def list_project_event(cls, project_id, send_event):
        label_selector, project = cls.get_label_selector(project_id)
        K8sService.get_namespace_event(project.namespace, send_event)

    @classmethod
    def read_namespaced_pod_log(cls, name, namespace, previous):
        response = K8sService.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            previous=previous
        )
        return response
