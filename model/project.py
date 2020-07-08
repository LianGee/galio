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
    namespace = Column(String)
    user_name = Column(String)
    type = Column(Integer)
    logo = Column(Text)
    git = Column(String)
    description = Column(String)
    build_type = Column(Integer, default=0)
    dockerfile_type = Column(Integer, default=0)
    docker_template_id = Column(BigInteger)
    base_image = Column(String)
    nginx_template_id = Column(BigInteger)
    nginx_proxies = Column(Text, default='[]')
    harbor_project = Column(String, default='library')
    domain = Column(String)
    port = Column(Integer, default=30080)
    service_domain = Column(String)
    deployment_template_id = Column(BigInteger)
    svc_template_id = Column(BigInteger)
    ingress_template_id = Column(BigInteger)
    deploy_config = Column(Text, default='{}')
