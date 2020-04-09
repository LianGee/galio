#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user_service.py
# @Author: zaoshu
# @Date  : 2020-02-10
# @Desc  :
import json

from common.exception import ServerException
from model.user import User


class UserService:

    @classmethod
    def get_user_from_cas_resp(cls, response) -> User:
        resp = json.loads(response.text).get('serviceResponse')
        if resp.get('authenticationFailure'):
            raise ServerException(msg=f"{resp.get('authenticationFailure').get('description')}")
        else:
            attributes = resp.get('authenticationSuccess').get('attributes')
            return User(
                name=attributes.get('name')[0],
                email=attributes.get('email')[0],
                phone=attributes.get('phone')[0],
                avatar=attributes.get('avatar')[0],
                id=int(attributes.get('id')[0])
            )
