#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : scheduler.py
# @Author: zaoshu
# @Date  : 2020-05-19
# @Desc  :
from apscheduler.schedulers.background import BackgroundScheduler

from service.build_service import BuildService
from service.docker_service import DockerService

scheduler = BackgroundScheduler()
scheduler.add_job(DockerService.clean_docker, trigger='interval', minutes=5, id='clean_docker')
scheduler.add_job(BuildService.clean_log, trigger='interval', hours=1, id='clean_docker')
scheduler.start()
