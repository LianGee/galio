#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s_builder.py
# @Author: zaoshu
# @Date  : 2020-06-04
# @Desc  :
import math


class K8sBuilder:

    @classmethod
    def namespace_builder(cls, namespace):
        return {
            'uid': namespace.metadata.uid,
            'name': namespace.metadata.name,
            'annotations': namespace.metadata.annotations,
            'created_at': math.floor(namespace.metadata.creation_timestamp.timestamp()),
            'phase': namespace.status.phase
        }

    @classmethod
    def role_builder(cls, role):
        return {
            'uid': role.metadata.uid,
            'name': role.metadata.name,
            'created_at': role.metadata.creation_timestamp,
        }

    @classmethod
    def node_builder(cls, node):
        return {
            'uid': node.metadata.uid,
            'name': node.metadata.name,
            'annotations': node.metadata.annotations,
            'labels': node.metadata.labels,
            'status': node.status.conditions[-1].type,
            'created_at': math.floor(node.metadata.creation_timestamp.timestamp()),
        }

    @classmethod
    def deployment_builder(cls, deployment):
        return {
            'uid': deployment.metadata.uid,
            'name': deployment.metadata.name,
            'namespace': deployment.metadata.namespace,
            'created_at': math.floor(deployment.metadata.creation_timestamp.timestamp()),
            'labels': deployment.metadata.labels,
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
        }

    @classmethod
    def replica_builder(cls, replica):
        return {
            'uid': replica.metadata.uid,
            'name': replica.metadata.name,
            'annotations': replica.metadata.annotations,
            'namespace': replica.metadata.namespace,
            'labels': replica.metadata.labels,
            'created_at': math.floor(replica.metadata.creation_timestamp.timestamp()),
            'status': {
                'available_replicas': replica.status.available_replicas,
                'ready_replicas': replica.status.ready_replicas,
                'replicas': replica.status.replicas,
                'fully_labeled_replicas': replica.status.fully_labeled_replicas
            },
        }
