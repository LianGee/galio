#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : project.py
# @Author: zaoshu
# @Date  : 2020-04-09
# @Desc  :
from flask import Blueprint, request, g

from common.log import log_this
from common.logger import Logger
from common.login import login_required
from common.response import Response
from service.project_service import ProjectService

project_bp = Blueprint('project', __name__)
log = Logger(__name__)


@project_bp.route('/save', methods=['POST'])
@login_required
@log_this
def save():
    project = request.json
    return Response.success(data=ProjectService.save(project, g.user.name))


@project_bp.route('/list', methods=['GET'])
@login_required
@log_this
def project_list():
    return Response.success(data=ProjectService.list(g.user.name))


@project_bp.route('/query', methods=['GET'])
@login_required
@log_this
def query_project_by_id():
    project_id = request.args.get('project_id')
    assert project_id is not None
    return Response.success(data=ProjectService.query_project_by_id(project_id))
