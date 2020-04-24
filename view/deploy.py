#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : create_namespaced_deployment.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :
from flask import Blueprint, g, request

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.deploy_service import DeployService

deploy_bp = Blueprint('create_namespaced_deployment', __name__)


@deploy_bp.route('/start', methods=['POST'])
@login_required
@log_this
def start():
    project_id = request.json.get('project_id')
    image_name = request.json.get('image_name')
    return Response.success(data=DeployService.deploy(g.user, project_id, image_name))


@deploy_bp.route('/restart', methods=['POST'])
@login_required
@log_this
def restart():
    pass


@deploy_bp.route('/log', methods=['POST'])
@login_required
@log_this
def get_log():
    namespace = request.json.get('namespace')
    name = request.json.get('name')
    previous = request.json.get('previous')
    return Response.success(data=DeployService.read_namespaced_pod_log(
        name=name,
        namespace=namespace,
        previous=previous
    ))


@deploy_bp.route('/read/namespaced/pod/status')
@login_required
def read_namespaced_pod_status():
    project_id = request.args.get('project_id')
    return Response.success(data=DeployService.list_pod_status(project_id))
