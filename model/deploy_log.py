#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_log.py
# @Author: zaoshu
# @Date  : 2020-06-10
# @Desc  :
from sqlalchemy import Column, String, Text, Integer

from model.base import BaseModel
from model.db import Model


class DeployLog(Model, BaseModel):
    __tablename__ = 'deploy_log'

    project_name = Column(String(50))
    user_name = Column(String(50))
    image_name = Column(String(50))
    reason = Column(Text)
    status = Column(Integer, default=0)
