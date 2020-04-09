#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : response.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  :
from flask import jsonify

from common.constant import ErrorCode
from model.base import BaseModel


class Response:
    def __init__(self, status: int, msg: str, data):
        self.status = status
        self.msg = msg
        self.data = data

    @staticmethod
    def convert_data(data):
        if isinstance(data, BaseModel):
            return data.to_dict()
        if isinstance(data, list) and all(isinstance(d, BaseModel) for d in data):
            return [d.get_json() for d in data]
        if isinstance(data, object) and hasattr(data, '__dict__'):
            return data.__dict__
        return data

    @staticmethod
    def success(data, status=ErrorCode.SUCCESS, msg=None):
        response = Response(status=status, msg=msg, data=Response.convert_data(data))
        return jsonify(response.__dict__)

    @staticmethod
    def failed(msg, status=ErrorCode.FAILED, data=None):
        response = Response(status=status, msg=msg, data=data)
        return jsonify(response.__dict__)
