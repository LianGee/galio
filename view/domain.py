#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : domain.py
# @Author: zaoshu
# @Date  : 2020-04-24
# @Desc  :
from flask import Blueprint, request

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.domain_service import DomainService

domain_bp = Blueprint('domain', __name__)


@domain_bp.route('/list/record')
@login_required
@log_this
def list_domain():
    return Response.success(data=DomainService.list_domain_record())


@domain_bp.route('/record/save', methods=['POST'])
@login_required
@log_this
def save_record():
    return Response.success(data=DomainService.save_domain_record(request.json))
