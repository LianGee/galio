#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : template.py
# @Author: zaoshu
# @Date  : 2020-04-13
# @Desc  :
from sqlalchemy import Column, String, Integer, Text

from model.base import BaseModel
from model.db import Model


class Template(Model, BaseModel):
    __tablename__ = 'template'

    name = Column(String)
    path = Column(String, default='')
    content = Column(Text)
    type = Column(Integer, default=0)
    author = Column(Integer)
