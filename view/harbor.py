#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : harbor.py
# @Author: zaoshu
# @Date  : 2020-06-28
# @Desc  :
from flask import Blueprint, request

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.harbor_service import HarborService

harbor_bp = Blueprint('harbor', __name__)


@harbor_bp.route('/list/base/image')
@login_required
@log_this
def list_base_image():
    page_num = request.args.get('page_num', 1)
    page_size = request.args.get('page_size', 10)
    return Response.success(data=HarborService.list_base_image(page_num, page_size))
