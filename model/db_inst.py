#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : db_inst.py
# @Author: zaoshu
# @Date  : 2020-04-15
# @Desc  :
from sqlalchemy import Column, String

from model.base import BaseModel
from model.db import Model


class DBInst(Model, BaseModel):
    __tablename__ = 'db_inst'

    ip = Column(String(15), default='127.0.0.1')
    port = Column(String(5), default='3306')
    user_name = Column(String(50))
    password = Column(String(50))
