#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : domain_record.py
# @Author: zaoshu
# @Date  : 2020-04-25
# @Desc  : 
from sqlalchemy import Column, String, BigInteger, Boolean

from model.base import BaseModel
from model.db import Model


class DomainRecord(Model, BaseModel):
    __tablename__ = 'domain_record'

    domain = Column(String(1024))
    port = Column(BigInteger)
    host_id = Column(BigInteger)
    ssl = Column(Boolean, default=False)
    ssl_certificate = Column(String)
    ssl_certificate_key = Column(String)
