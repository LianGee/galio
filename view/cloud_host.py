#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cloud_host.py
# @Author: zaoshu
# @Date  : 2020-04-24
# @Desc  :
from flask import Blueprint, request

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.cloud_host_service import CloudHostService

cloud_host_bp = Blueprint('cloud_host', __name__)


@cloud_host_bp.route('/list')
@login_required
@log_this
def list_cloud_host():
    return Response.success(data=CloudHostService.list_cloud_host())


@cloud_host_bp.route('/save', methods=['POST'])
@login_required
@log_this
def save_cloud_host():
    return Response.success(data=CloudHostService.save_cloud_host(request.json))
