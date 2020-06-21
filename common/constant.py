#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : constant.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  : 


class ErrorCode:
    SUCCESS = 0
    FAILED = 500
    NOT_LOGIN = 400


class HttpCode:
    HTTP_SUCCESS = [201, 200]


class BuildType:
    NPM = 0
    TAR = 1
    MVN = 2
    GRADLE = 3
    USER_DEFINE = 4


class DeployStatus:
    INIT = 0
    NAMESPACE = 1
    DEPLOYMENT = 2
    SERVICE = 3
    INGRESS = 4


class ProgressType:
    WAIT = 'wait'
    PROGRESS = 'process'
    FINISH = 'finish'
    ERROR = 'error'
