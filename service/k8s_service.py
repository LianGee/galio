#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s_service.py
# @Author: zaoshu
# @Date  : 2020-04-17
# @Desc  :
import json

import kubernetes
from kubernetes import watch

import config
from common.config_util import ConfigUtil
from common.exception import ServerException
from common.logger import Logger
from model.builder.k8s_builder import K8sBuilder
from model.project import Project

log = Logger(__name__)


class K8sService:

    @classmethod
    def get_api_client(cls):
        kubernetes.config.load_kube_config()
        configuration = kubernetes.client.Configuration()
        configuration.api_key['Accept'] = 'application/json'
        return kubernetes.client.ApiClient(configuration)

    @classmethod
    def list_namespace(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        api_response = api_instance.list_namespace()
        namespaces = []
        for namespace in api_response.items:
            namespaces.append(K8sBuilder.namespace_builder(namespace))
        return namespaces

    @classmethod
    def list_node(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_node()
        nodes = []
        for node in response.items:
            nodes.append(K8sBuilder.node_builder(node))
        return nodes

    @classmethod
    def get_deployment_by_project(cls, project: Project):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_deployment_for_all_namespaces(
            field_selector=f'metadata.name={project.name},metadata.namespace={project.namespace}',
        )
        return cls.convert_deployment(response)

    @classmethod
    def get_labeled_replicas(cls, label_selector, send_replica):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        while True:
            stream = watch.Watch().stream(
                api_instance.list_replica_set_for_all_namespaces,
                label_selector=label_selector,
                watch=True,
                pretty=True
            )
            for replica in stream:
                send_replica(replica.get('raw_object'))

    @classmethod
    def get_namespace_labeled_pods(cls, namespace, label_selector, send_pod=None):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        while True:
            stream = watch.Watch().stream(
                api_instance.list_namespaced_pod,
                namespace=namespace,
                label_selector=label_selector,
                watch=True,
                pretty=True
            )
            pod_map = {}
            for pod in stream:
                action = pod.get('type')
                obj = pod.get('raw_object')
                if action == 'DELETED':
                    pod_map.pop(obj.get('metadata').get('name'))
                else:
                    pod_map[obj.get('metadata').get('name')] = obj
                send_pod(list(pod_map.values()))

    @classmethod
    def get_namespace_event(cls, namespace, send_event):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        while True:
            stream = watch.Watch().stream(
                api_instance.list_namespaced_event,
                namespace=namespace,
                watch=True,
                pretty=True
            )
            for event in stream:
                send_event(event.get('raw_object'))

    @classmethod
    def list_namespaced_pod(cls, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_namespaced_pod(namespace=namespace)
        return cls.convert_pod(response)

    @classmethod
    def list_replica_set(cls):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_replica_set_for_all_namespaces()
        return cls.convert_replica(response)

    @classmethod
    def list_service(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_service_for_all_namespaces()
        services = []
        for service in response.items:
            services.append({
                'uid': service.metadata.uid,
                'name': service.metadata.name,
                'annotations': service.metadata.annotations,
                'namespace': service.metadata.namespace,
                'labels': service.metadata.labels,
                'created_at': service.metadata.creation_timestamp,
                'type': service.spec.type,
                'cluster_ip': service.spec.cluster_ip,
                'external_ip': service.spec.external_i_ps,
                'ports': [
                    {
                        'name': port.name,
                        'node_port': port.node_port,
                        'port': port.port,
                        'protocol': port.protocol,
                        'target_port': port.target_port
                    } for port in service.spec.ports
                ]
            })
        return services

    @classmethod
    def list_secrets(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_secret_for_all_namespaces()
        return response

    @classmethod
    def list_cluster_role(cls):
        api_instance = kubernetes.client.RbacAuthorizationV1Api(cls.get_api_client())
        response = api_instance.list_cluster_role()
        roles = []
        for role in response.items:
            roles.append(K8sBuilder.role_builder(role))
        return roles

    @classmethod
    def list_deployment(cls):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_deployment_for_all_namespaces()
        return cls.convert_deployment(response)

    @classmethod
    def read_namespaced_deployment(cls, name, namespace):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.read_namespaced_deployment(name=name, namespace=namespace)
        return response

    @classmethod
    def read_namespaced_pod_log(cls, name, namespace, previous=False):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            tail_lines=ConfigUtil.get_int_property(config.K8S_POD_LOG_LENGTH),
            previous=previous
        )
        return response

    @classmethod
    def list_pod_events(cls, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        if namespace:
            events = api_instance.list_namespaced_event(namespace=namespace, pretty=True)
        else:
            events = api_instance.list_event_for_all_namespaces()
        pod_events = []
        for event in events.items:
            if event.involved_object.kind == 'Pod':
                pod_events.append({
                    'pod_name': event.involved_object.name,
                    'type': event.type,
                    'reason': event.reason,
                    'message': event.message,
                    'name': event.metadata.name,
                    'namespace': event.metadata.namespace,
                    'created_at': event.metadata.creation_timestamp,
                })
        return pod_events

    @classmethod
    def create_namespace(cls, name, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        body = kubernetes.client.V1Namespace()
        body.metadata = kubernetes.client.V1ObjectMeta(
            name=name,
            labels={
                'name': namespace,
            }
        )
        try:
            api_instance.create_namespace(body)
            return True
        except kubernetes.client.rest.ApiException as e:
            body = json.loads(e.body)
            if body.get('reason') == 'AlreadyExists':
                return True
            raise ServerException(f'创建namespace {namespace}失败')

    @classmethod
    def create_namespaced_deployment(cls, name, namespace, body):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        try:
            api_instance.delete_namespaced_deployment(name=name, namespace=namespace)
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'namespace {namespace} deployment {name} exist, just created.')
            else:
                raise ServerException('删除namespaced deployment失败')
        api_instance.create_namespaced_deployment(namespace=namespace, body=body)
        response = api_instance.read_namespaced_deployment(name=name, namespace=namespace)
        return response

    @classmethod
    def create_namespaced_service(cls, name, namespace, body):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        try:
            api_instance.create_namespaced_service(namespace=namespace, body=body)
        except kubernetes.client.rest.ApiException as e:
            body = json.loads(e.body)
            if body.get('reason') == 'AlreadyExists':
                return True
            raise ServerException(f'创建service {name} namespace {namespace}失败')
        response = api_instance.read_namespaced_service(name=name, namespace=namespace)
        return response

    @classmethod
    def create_namespaced_ingress(cls, name, namespace, body):
        api_instance = kubernetes.client.ExtensionsV1beta1Api(cls.get_api_client())
        try:
            api_instance.create_namespaced_ingress(namespace=namespace, body=body)
        except kubernetes.client.rest.ApiException as e:
            body = json.loads(e.body)
            if body.get('reason') == 'AlreadyExists':
                return True
            raise ServerException(f'创建ingress {name} namespace {namespace}失败')
        response = api_instance.read_namespaced_ingress(name=name, namespace=namespace)
        return response

    @classmethod
    def replace_namespaced_pod(cls, name, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        body = kubernetes.client.V1Pod()
        response = api_instance.replace_namespaced_pod(name=name, namespace=namespace, body=body)
        return response

    @classmethod
    def get_state(cls, status):
        if status.running:
            return 'running'
        elif status.terminated:
            return 'terminated'
        elif status.waiting:
            return 'waiting'
        return 'unknown'

    @classmethod
    def convert_deployment(cls, response):
        deployments = []
        for deployment in response.items:
            deployments.append(K8sBuilder.deployment_builder(deployment))
        return deployments

    @classmethod
    def convert_replica(cls, response):
        replica_set = []
        for replica in response.items:
            replica_set.append(K8sBuilder.replica_builder(replica))
        return replica_set

    @classmethod
    def convert_pod(cls, response, events=[]):
        pods = []
        event_map = {}
        for event in events:
            if event_map.get(event.get('pod_name')) is not None:
                event_map[event.get('pod_name')].append(event)
            else:
                event_map[event.get('pod_name')] = [event]
        for pod in response.items:
            pods.append({
                'name': pod.metadata.name,
                'uid': pod.metadata.uid,
                'namespace': pod.metadata.namespace,
                'host_ip': pod.status.host_ip,
                'pod_ip': pod.status.pod_ip,
                'phase': pod.status.phase,
                'start_time': pod.status.start_time,
                'reason': pod.status.reason or pod.status.conditions[0].message,
                'restart_count': pod.status.container_statuses[
                    0].restart_count if pod.status.container_statuses else 0,
                'events': event_map.get(pod.metadata.name)
            })
        return pods
