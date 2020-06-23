#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : scheduler.py
# @Author: zaoshu
# @Date  : 2020-05-19
# @Desc  :
from apscheduler.schedulers.background import BackgroundScheduler

from service.build_service import BuildService
from service.docker_service import DockerService


def run_schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(DockerService.clean_docker, trigger='interval', minutes=15, id='clean_docker')
    scheduler.add_job(BuildService.clean_log, trigger='interval', minutes=15, id='clean_build_log')
    scheduler.start()
