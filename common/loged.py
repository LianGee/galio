#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : loged.py
# @Author: zaoshu
# @Date  : 2020-03-01
# @Desc  :
import functools
import json

from flask import request

from common.log import Logger

log = Logger(__name__)


def log_this(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        params = request.args if request.method == 'GET' else request.json
        log.info(json.dumps(params, ensure_ascii=False, indent=4))
        result = func(*args, **kwargs)
        if hasattr(result, 'json'):
            log.info(json.dumps(result.json, ensure_ascii=False, indent=4))
        return result

    return wrapper
