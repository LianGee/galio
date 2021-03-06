#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s_service.py
# @Author: zaoshu
# @Date  : 2020-04-17
# @Desc  :
import json
import time

import kubernetes
from kubernetes import watch

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
    def get_deployment_by_project(cls, project: Project):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        response = api_instance.list_deployment_for_all_namespaces(
            field_selector=f'metadata.name={project.name},metadata.namespace={project.namespace}',
        )
        return cls.convert_deployment(response)

    @classmethod
    def get_labeled_replicas(cls, label_selector, send_replica):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
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
        stream = watch.Watch().stream(
            api_instance.list_namespaced_event,
            namespace=namespace,
            watch=True,
            pretty=True,
            timeout_seconds=5,
            limit=10
        )
        for event in stream:
            raw_object = event.get('raw_object')
            if raw_object.get('eventTime') and raw_object.get('type') == 'Error':
                send_event(raw_object)

    @classmethod
    def get_namespaced_pod_log(
            cls,
            name,
            namespace,
            trace,
            previous,
            tail_lines,
            send_log
    ):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        w = watch.Watch()
        stream = w.stream(
            api_instance.read_namespaced_pod_log,
            name=name,
            namespace=namespace,
            previous=previous,
            follow=True,
            since_seconds=3600 * 12,
            tail_lines=tail_lines
        )
        try:
            for evnet in stream:
                send_log(evnet)
                time.sleep(0.05)
                if not trace:
                    w.stop()
        except Exception as e:
            send_log(json.loads(e.body).get('message'))

    @classmethod
    def download_pod_log(cls, name, namespace, tail_lines):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        return api_instance.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            tail_lines=min(int(tail_lines), 100000)
        )

    @classmethod
    def create_namespace(cls, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        try:
            return api_instance.read_namespace(name=namespace, pretty=True)
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                body = kubernetes.client.V1Namespace()
                body.metadata = kubernetes.client.V1ObjectMeta(
                    name=namespace,
                    labels={
                        'name': namespace,
                    }
                )
                return api_instance.create_namespace(body=body, pretty=True)
        raise ServerException(f'创建namespace {namespace}失败')

    @classmethod
    def create_namespaced_deployment(cls, name, namespace, body):
        api_instance = kubernetes.client.AppsV1Api(cls.get_api_client())
        try:
            deployment_body = api_instance.read_namespaced_deployment(name=name, namespace=namespace, pretty=True)
            log.info(f'deployment name={name} namespace={namespace} 存在，删除该deployment {deployment_body}')
            delete_response = api_instance.delete_namespaced_deployment(name=name, namespace=namespace, pretty=True)
            log.info(f'删除 deployment name={name} namespace={namespace} {delete_response}')
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'deployment name={name} namespace={namespace} 不存在，直接创建')
        return api_instance.create_namespaced_deployment(namespace=namespace, body=body, pretty=True)

    @classmethod
    def create_namespaced_service(cls, name, namespace, body):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        try:
            service_body = api_instance.read_namespaced_service(name=name, namespace=namespace, pretty=True)
            log.info(f'service name={name} namespace={namespace} 存在，删除该service {service_body}')
            delete_response = api_instance.delete_namespaced_service(name=name, namespace=namespace, pretty=True)
            log.info(f'删除 service name={name} namespace={namespace} {delete_response}')
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'service name={name} namespace={namespace} 不存在，直接创建')
        return api_instance.create_namespaced_service(namespace=namespace, body=body, pretty=True)

    @classmethod
    def create_namespaced_ingress(cls, name, namespace, body):
        api_instance = kubernetes.client.ExtensionsV1beta1Api(cls.get_api_client())
        try:
            ingress_body = api_instance.read_namespaced_ingress(name=name, namespace=namespace, pretty=True)
            log.info(f'ingress name={name} namespace={namespace} 存在，删除该ingress {ingress_body}')
            delete_response = api_instance.delete_namespaced_ingress(namespace=namespace, name=name, pretty=True)
            log.info(f'删除 service name={name} namespace={namespace} {delete_response}')
        except kubernetes.client.rest.ApiException as e:
            if e.reason == 'Not Found':
                log.info(f'ingress name={name} namespace={namespace} 不存在，直接创建')
        return api_instance.create_namespaced_ingress(namespace=namespace, body=body, pretty=True)

    @classmethod
    def delete_namespaced_pod(cls, name, namespace):
        api_instance = kubernetes.client.CoreV1Api(cls.get_api_client())
        return api_instance.delete_namespaced_pod(
            name=name,
            namespace=namespace,
            pretty=True,
        )

    @classmethod
    def convert_deployment(cls, response):
        deployments = []
        for deployment in response.items:
            deployments.append(K8sBuilder.deployment_builder(deployment))
        return deployments
