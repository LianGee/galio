#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deploy_log.py
# @Author: zaoshu
# @Date  : 2020-06-10
# @Desc  :
import uuid

from sqlalchemy import Column, String, Text, Integer, BigInteger

from model.base import BaseModel
from model.db import Model


class DeployLog(Model, BaseModel):
    __tablename__ = 'deploy_log'

    uuid = Column(String(32), default=uuid.uuid4().hex)
    project_id = Column(BigInteger)
    project_name = Column(String(50))
    user_name = Column(String(50))
    image_name = Column(String(50))
    reason = Column(Text)
    status = Column(Integer, default=0)
