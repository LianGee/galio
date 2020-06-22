#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : create_namespaced_deployment.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :
import mimetypes

from flask import Blueprint, g, request, make_response

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


@deploy_bp.route('/download/log', methods=['GET'])
@login_required
@log_this
def download_log():
    file_name, content = DeployService.download_log(**request.args.to_dict())
    response = make_response(content)
    mime_type = mimetypes.guess_type(file_name)[0]
    response.headers['Content-Type'] = mime_type
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(file_name.encode().decode('latin-1'))
    return response
