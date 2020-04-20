#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : build.py
# @Author: zaoshu
# @Date  : 2020-04-11
# @Desc  :
from flask import Blueprint, g, request

import config
from common.config_util import ConfigUtil, cache
from common.log import log_this
from common.login import login_required
from common.response import Response
from model.project import Project
from service.build_service import BuildService
from service.git_service import GitService

build_bp = Blueprint('build', __name__)


@build_bp.route('/branches', methods=['GET'])
@login_required
@log_this
@cache.memoize(ttl=60 * 5)
def branches():
    project = Project.select().get(1)
    git_service = GitService(
        workspace=f'{ConfigUtil.get_str_property(config.GIT_WORKSPACE)}/project',
        project=project
    )
    git_service.init()
    return Response.success(data=git_service.get_branches())


@build_bp.route('/logs', methods=['GET'])
@login_required
@log_this
def get_logs():
    return Response.success(data=BuildService.get_logs(g.user.name))


@build_bp.route('/log/content', methods=['GET'])
@login_required
@log_this
def get_log_content():
    log_path = request.args.get('log_path')
    assert id is not None
    return Response.success(data=BuildService.get_log_content(log_path))
