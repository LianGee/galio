#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : response.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  :
import math
from copy import copy
from datetime import datetime

from flask import jsonify

from common.constant import ErrorCode
from model.base import BaseModel


class Response:
    def __init__(self, status: int, msg: str, data):
        self.status = status
        self.msg = msg
        self.data = data

    @classmethod
    def to_dict(cls, data):
        if isinstance(data, datetime):
            return math.floor(data.timestamp())
        elif isinstance(data, list):
            return [cls.to_dict(d) for d in data]
        elif isinstance(data, dict) or hasattr(data, '__dict__'):
            res = {}
            dic = data if isinstance(data, dict) else vars(data)
            for key in dic.keys():
                if not isinstance(dic[key], object) and hasattr(dic[key], '__dict__'):
                    res[key] = vars(dic[key])
                else:
                    res[key] = cls.to_dict(dic[key])
            return res

        else:
            return data

    @staticmethod
    def convert_data(data):
        if isinstance(data, BaseModel):
            return data.to_dict()
        elif isinstance(data, list) and all(isinstance(d, BaseModel) for d in data):
            return [d.to_dict() for d in data]
        elif isinstance(data, list) or isinstance(data, dict) or hasattr(data, '__dict__'):
            return Response.to_dict(data)
        else:
            return data

    @staticmethod
    def success(data, status=ErrorCode.SUCCESS, msg=None):
        response = Response(status=status, msg=msg, data=Response.convert_data(copy(data)))
        return jsonify(vars(response))

    @staticmethod
    def failed(msg, status=ErrorCode.FAILED, data=None):
        response = Response(status=status, msg=msg, data=data)
        return jsonify(vars(response))
