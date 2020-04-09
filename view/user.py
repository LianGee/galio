#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user.py
# @Author: zaoshu
# @Date  : 2020-02-10
# @Desc  :
import json
import flask
from flask import Blueprint, request, session, g

from common.config_util import ConfigUtil
from common.http_util import HttpUtil
from common.log import Logger
from common.loged import log_this
from common.login import login_required
from common.response import Response
import config
from model.user import User
from service.user_service import UserService

user_bp = Blueprint('user', __name__)
log = Logger(__name__)


@user_bp.route('/login', methods=['GET'])
@log_this
def login():
    user = session.get('user')
    if user is not None:
        user = json.loads(user)
        g.user = User.fill_model(User(), user)
        return flask.redirect(request.args.get('redirect') or ConfigUtil.get_str_property(config.FRONT_URL))
    ticket = request.args.get('ticket')
    http_util = HttpUtil(
        url=f'{ConfigUtil.get_str_property(config.CAS_URL)}/cas/p3/serviceValidate?'
        f'format=json&service={request.url}&ticket={ticket}')
    response = http_util.get()
    user = UserService.get_user_from_cas_resp(response)
    g.user = user
    session['user'] = json.dumps(user.to_dict(), ensure_ascii=False)
    return flask.redirect(request.args.get('redirect') or ConfigUtil.get_str_property(config.FRONT_URL))


@user_bp.route('/logout')
@login_required
@log_this
def logout():
    session.clear()
    g.user = None
    return Response.success(data=f'{ConfigUtil.get_str_property(config.CAS_URL)}/cas/logout')


@user_bp.route('/current')
@login_required
def current():
    return Response.success(g.user)
