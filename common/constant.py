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
    DIST = 0
    PYTHON2 = 1
    PYTHON3 = 2
    JAVA8_MAVEN_3 = 3
    JAVA8_GRADLE_4 = 4
