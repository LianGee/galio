#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s.py
# @Author: zaoshu
# @Date  : 2020-04-17
# @Desc  :
from flask import Blueprint, request

from common.response import Response
from service.k8s_service import K8sService

k8s_bp = Blueprint('k8s', __name__)


@k8s_bp.route('/list/namespace')
def list_namespace():
    return Response.success(data=K8sService.list_namespace())


@k8s_bp.route('/list/node')
def list_node():
    return Response.success(data=K8sService.list_node())


@k8s_bp.route('/list/replica/set')
def list_replica_set():
    return Response.success(data=K8sService.list_replica_set())


@k8s_bp.route('/list/service')
def list_service():
    return Response.success(data=K8sService.list_service())


@k8s_bp.route('/list/secret')
def list_secret():
    return Response.success(data=K8sService.list_secrets())


@k8s_bp.route('/list/deployment')
def list_deployment():
    return Response.success(data=K8sService.list_deployment())


@k8s_bp.route('/list/event')
def list_namespaced_event():
    namespace = request.args.get('namespace')
    return Response.success(data=K8sService.list_pod_events(namespace))


@k8s_bp.route('/list/cluster/role')
def list_cluster_role():
    return Response.success(data=K8sService.list_cluster_role())


@k8s_bp.route('/read/namespaced/pod/log')
def read_namespaced_pod_log():
    name = request.args.get('name')
    namespace = request.args.get('namespace')
    return Response.success(data=K8sService.read_namespaced_pod_log(name=name, namespace=namespace))


@k8s_bp.route('/read/namespaced/deployment')
def read_namespaced_deployment():
    name = request.args.get('name')
    namespace = request.args.get('namespace')
    return Response.success(data=K8sService.read_namespaced_deployment(name=name, namespace=namespace))


@k8s_bp.route('/replace/namespaced/pod')
def replace_namespaced_pod():
    name = request.args.get('name')
    namespace = request.args.get('namespace')
    return Response.success(data=K8sService.replace_namespaced_pod(name, namespace))
