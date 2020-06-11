#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : build_log.py
# @Author: zaoshu
# @Date  : 2020-04-13
# @Desc  :
import uuid

from sqlalchemy import Column, String, Text, Integer

from model.base import BaseModel
from model.db import Model


class BuildLog(Model, BaseModel):
    __tablename__ = 'build_log'

    uuid = Column(String(32), default=uuid.uuid4().hex)
    project_name = Column(String(50))
    branch = Column(String(120), default="master")
    user_name = Column(String(50))
    image_name = Column(String(50))
    description = Column(Text)
    status = Column(Integer, default=0)
    log_path = Column(String, default='')
