#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : docker.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :
from flask import Blueprint, request

from common.response import Response
from service.docker_service import DockerService

docker_bp = Blueprint('docker', __name__)


@docker_bp.route('/list/image')
def list_image():
    return Response.success(data=DockerService.list_image())


@docker_bp.route('/list/project/image')
def list_project_image():
    return Response.success(data=DockerService.list_project_image(request.args.get('project_id')))


@docker_bp.route('/test')
def clean_images():
    return Response.success(data=DockerService.test())
