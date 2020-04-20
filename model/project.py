#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : project.py
# @Author: zaoshu
# @Date  : 2020-04-09
# @Desc  :
from sqlalchemy import Column, String, Integer, Text, BigInteger

from model.base import BaseModel
from model.db import Model


class Project(Model, BaseModel):
    __tablename__ = 'project'

    name = Column(String)
    user_name = Column(String)
    type = Column(Integer)
    build_type = Column(Integer, default=0)
    docker_template_id = Column(BigInteger)
    nginx_template_id = Column(BigInteger)
    domain = Column(String)
    port = Column(Integer, default=8080)
    git = Column(String)
    logo = Column(Text)
    base_image = Column(String)
    description = Column(String)
