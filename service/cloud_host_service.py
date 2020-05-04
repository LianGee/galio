#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cloud_host_service.py
# @Author: zaoshu
# @Date  : 2020-04-24
# @Desc  :
from model.cloud_host import CloudHost


class CloudHostService:

    @classmethod
    def list_cloud_host(cls):
        cloud_host = CloudHost.select().all()
        return cloud_host

    @classmethod
    def save_cloud_host(cls, data):
        if data.get('id'):
            cloud_host = CloudHost.select().get(data.get('id'))
            cloud_host.fill_model(cloud_host, data)
            cloud_host.update()
        else:
            cloud_host = CloudHost()
            cloud_host.fill_model(cloud_host, data)
            cloud_host.insert()
        cloud_host = CloudHost.select().filter(CloudHost.public_ip == data.get('public_ip')).one()
        return cloud_host.id
