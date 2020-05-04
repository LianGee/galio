#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cloud_host.py
# @Author: zaoshu
# @Date  : 2020-04-24
# @Desc  :
from sqlalchemy import Column, String

from model.base import BaseModel
from model.db import Model


class CloudHost(Model, BaseModel):
    __tablename__ = 'cloud_host'

    name = Column(String(127), default='')
    public_ip = Column(String(15), default='127.0.0.1')
    internal_ip = Column(String(15), default='127.0.0.1')
