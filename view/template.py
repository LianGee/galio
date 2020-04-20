#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : template.py
# @Author: zaoshu
# @Date  : 2020-04-13
# @Desc  :
from flask import Blueprint, request, g

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.template_service import TemplateService

template_bp = Blueprint('template', __name__)


@template_bp.route('/list', methods=['GET'])
@login_required
@log_this
def get_template_list():
    type = request.args.get('type')
    return Response.success(TemplateService.get_templates(type))


@template_bp.route('/get', methods=['GET'])
@login_required
@log_this
def get_template_by_id():
    id = request.args.get('id')
    assert id is not None
    return Response.success(TemplateService.get_template_by_id(id))


@template_bp.route('/save', methods=['POST'])
@login_required
@log_this
def save_template():
    data = request.json
    data['author'] = g.user.name
    return Response.success(TemplateService.save_template(request.json))
