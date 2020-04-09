#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : env_util.py
# @Author: zaoshu
# @Date  : 2020-04-08
# @Desc  : 

import os


def get_env(default_env='PROD'):
    return os.environ.get('ENV') if os.environ.get('ENV') else default_env


def is_prod():
    return 'PROD' == get_env()


def is_dev():
    return 'DEV' == get_env()

