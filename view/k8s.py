#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : k8s.py
# @Author: zaoshu
# @Date  : 2020-04-17
# @Desc  :
from flask import Blueprint

from common.response import Response
from service.k8s_service import K8sService

k8s_bp = Blueprint('k8s', __name__)


@k8s_bp.route('/list/namespace')
def list_namespace():
    return Response.success(data=K8sService.list_namespace())


@k8s_bp.route('/list/service')
def list_service():
    return Response.success(data=K8sService.list_service())
