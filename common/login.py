#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : login.py
# @Author: zaoshu
# @Date  : 2020-02-10
# @Desc  :
import functools
import json

from flask import session, request, g

import config
from common.config_util import ConfigUtil
from common.response import Response
from urllib.parse import urlencode
from model.user import User


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = session.get('user')
        if user is None:
            if request.referrer:
                redirect = urlencode({'redirect': request.referrer})
                service = f'{ConfigUtil.get_str_property(config.SERVER_URL)}/user/login?{redirect}'
            else:
                service = f'{ConfigUtil.get_str_property(config.SERVER_URL)}/user/login'
            login_url = f"{ConfigUtil.get_str_property(config.CAS_URL)}/cas/login?{urlencode({'service': service})}"
            return Response.success(status=30200, data=login_url)
        user = json.loads(user)
        g.user = User.fill_model(
            User(), user
        )
        return func(*args, **kwargs)

    return wrapper
