#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user.py
# @Author: zaoshu
# @Date  : 2020-02-10
# @Desc  :
from sqlalchemy import Column, String

from model.base import BaseModel
from model.db import Model


class User(Model, BaseModel):
    __tablename__ = 'user'
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    password = Column(String)
    avatar = Column(String)
