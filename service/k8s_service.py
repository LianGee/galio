#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s_service.py
# @Author: zaoshu
# @Date  : 2020-04-17
# @Desc  :
import json

import kubernetes

import config
from common.config_util import ConfigUtil
from common.exception import ServerException
from common.http_util import HttpUtil
from common.logger import Logger

log = Logger(__name__)


class K8sService:

    @classmethod
    def get_api_client(cls):
        kubernetes.config.load_kube_config()
        configuration = kubernetes.client.Configuration()
        configuration.host = f'{ConfigUtil.get_str_property(config.K8S_HOST)}'
        configuration.api_key['Accept'] = 'application/json'
        configuration.api_key['authorization'] = ConfigUtil.get_str_property(config.K8S_SEC)
        return kubernetes.client.ApiClient(configuration)

    @classmethod
    def apiregistration(cls):
        http_util = HttpUtil(
            url=f'{ConfigUtil.get_str_property(config.K8S_HOST)}/apis/apiregistration.k8s.io',
            headers={
                'Authorization': ConfigUtil.get_str_property(config.K8S_SEC)
            }
        )
        return http_util.request().json()

    @classmethod
    def k8s_test(cls):
        api_instance = kubernetes.client.AdmissionregistrationApi(cls.get_api_client())
        api_response = api_instance.get_api_group()
        return api_response

    @classmethod
    def list_namespace(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        api_response = api_instance.list_namespace()
        namespaces = []
        for namespace in api_response.items:
            namespaces.append({
                'uid': namespace.metadata.uid,
                'name': namespace.metadata.name,
                'annotations': namespace.metadata.annotations,
                'created_at': namespace.metadata.creation_timestamp,
                'phase': namespace.status.phase
            })
        return namespaces

    @classmethod
    def list_node(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_node()
        nodes = []
        for node in response.items:
            nodes.append({
                'uid': node.metadata.uid,
                'name': node.metadata.name,
                'annotations': node.metadata.annotations,
                'labels': node.metadata.labels,
                'status': node.status.conditions[-1].type,
                'created_at': node.metadata.creation_timestamp,
            })
        return nodes

    @classmethod
    def list_pod(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_pod_for_all_namespaces()
        pods = []
        for pod in response.items:
            pods.append({
                'uid': pod.metadata.uid,
                'name': pod.metadata.name,
                'annotations': pod.metadata.annotations,
                'labels': pod.metadata.labels,
                'phase': pod.status.phase,
                'created_at': pod.metadata.creation_timestamp,
                'namespace': pod.metadata.namespace,
                'container_statuses': [
                    {
                        'ready': status.ready,
                        'restart_count': status.restart_count
                    } for status in pod.status.container_statuses
                ],
                'host_ip': pod.status.host_ip,
                'pod_ip': pod.status.pod_ip
            })
        return pods

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
    def list_namespaced_pod(cls, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_namespaced_pod(namespace=namespace)
        pods = []
        for pod in response.items:
            pods.append({
                'uid': pod.metadata.uid,
                'name': pod.metadata.name,
                'annotations': pod.metadata.annotations,
                'labels': pod.metadata.labels,
                'phase': pod.status.phase,
                'created_at': pod.metadata.creation_timestamp,
                'namespace': pod.metadata.namespace,
                'container_statuses': [
                    {
                        'ready': status.ready,
                        'restart_count': status.restart_count,
                        'state': cls.get_state(status.state),
                        'name': status.name,
                        'image': status.image,
                        'container_id': status.container_id
                    } for status in pod.status.container_statuses or []
                ],
                'host_ip': pod.status.host_ip,
                'pod_ip': pod.status.pod_ip
            })
        return pods

    @classmethod
    def list_pod_status(cls, namespace=None):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        if namespace:
            response = api_instance.list_namespaced_pod(namespace=namespace)
        else:
            response = api_instance.list_pod_for_all_namespaces()
        pod_statuses = []
        events = cls.list_event(namespace=namespace)
        event_map = {}
        for event in events:
            if event_map.get(event.get('pod_name')) is not None:
                event_map[event.get('pod_name')].append(event)
            else:
                event_map[event.get('pod_name')] = [event]
        for pod_status in response.items:
            pod_statuses.append({
                'name': pod_status.metadata.name,
                'uid': pod_status.metadata.uid,
                'namespace': pod_status.metadata.namespace,
                'host_ip': pod_status.status.host_ip,
                'pod_ip': pod_status.status.pod_ip,
                'phase': pod_status.status.phase,
                'start_time': pod_status.status.start_time,
                'reason': pod_status.status.reason or pod_status.status.conditions[0].message,
                'restart_count': pod_status.status.container_statuses[
                    0].restart_count if pod_status.status.container_statuses else 0,
                'events': event_map.get(pod_status.metadata.name)
            })

        return pod_statuses

    @classmethod
    def list_replica_set(cls):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_replica_set_for_all_namespaces()
        replica_set = []
        for replica in response.items:
            replica_set.append({
                'uid': replica.metadata.uid,
                'name': replica.metadata.name,
                'annotations': replica.metadata.annotations,
                'namespace': replica.metadata.namespace,
                'labels': replica.metadata.labels,
                'created_at': replica.metadata.creation_timestamp,
                'status': replica.status,
                'pods': f'{replica.status.ready_replicas or 0}/{replica.status.available_replicas or 0}'
            })
        return replica_set

    @classmethod
    def list_service(cls):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        response = api_instance.list_service_for_all_namespaces()
        services = []
        for service in response.items:
            services.append({
                'name': service.metadata.name,
                'annotations': service.metadata.annotations,
                'namespace': service.metadata.namespace,
                'labels': service.metadata.labels,
                'created_at': service.metadata.creation_timestamp,
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
            roles.append({
                'uid': role.metadata.uid,
                'name': role.metadata.name,
                'created_at': role.metadata.creation_timestamp,
            })
        return roles

    @classmethod
    def list_deployment(cls):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_deployment_for_all_namespaces()
        deployments = []
        for deployment in response.items:
            deployments.append({
                'uid': deployment.metadata.uid,
                'name': deployment.metadata.name,
                'namespace': deployment.metadata.namespace,
                'created_at': deployment.metadata.creation_timestamp,
                'container': [
                    {
                        'env': [
                            {
                                'name': env.name,
                                'value': env.value
                            } for env in container.env
                        ] if container.env else [],
                        'ports': container.ports,
                        'command': container.command,
                        'image': container.image,
                        'image_pull_policy': container.image_pull_policy,
                        'args': container.args
                    } for container in deployment.spec.template.spec.containers
                ]
            })
        return deployments

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
    def list_event(cls, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        if namespace:
            events = api_instance.list_namespaced_event(namespace=namespace)
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
        # 隔离不同的资源
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
            return False

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
            api_instance.delete_namespaced_service(name=name, namespace=namespace)
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'namespace {namespace} service {name} exist, just created.')
            else:
                raise ServerException('删除namespaced service 失败')
        api_instance.create_namespaced_service(namespace=namespace, body=body)
        response = api_instance.read_namespaced_service(name=name, namespace=namespace)
        return response

    @classmethod
    def create_namespaced_ingress(cls, name, namespace, body):
        api_instance = kubernetes.client.ExtensionsV1beta1Api(cls.get_api_client())
        try:
            api_instance.delete_namespaced_ingress(namespace=namespace, name=name)
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'namespace {namespace} ingress {name} exist, just created.')
            else:
                raise ServerException('删除namespaced ingress 失败')
        api_instance.create_namespaced_ingress(namespace=namespace, body=body)
        response = api_instance.read_namespaced_ingress(name=name, namespace=namespace)
        return response

    @classmethod
    def replace_namespaced_pod(cls, name, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        body = kubernetes.client.V1Pod()
        # body.metadata.name = name
        # body.metadata.namespace = namespace
        response = api_instance.replace_namespaced_pod(name=name, namespace=namespace, body=body)
        return response
