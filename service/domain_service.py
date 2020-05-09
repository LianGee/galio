#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : domain_service.py
# @Author: zaoshu
# @Date  : 2020-04-24
# @Desc  :
import random
import socket

import config
from common.config_util import ConfigUtil
from model.cloud_host import CloudHost
from model.domain_record import DomainRecord
from service.k8s_service import K8sService


class DomainService:

    @classmethod
    def list_domain_record(cls):
        domain_records = DomainRecord.select().all()
        host_ids = [domain_record.host_id for domain_record in domain_records]
        hosts = CloudHost.select().filter(CloudHost.id.in_(host_ids)).all()
        host_map = {}
        for host in hosts:
            host_map[host.id] = host.to_dict()
        result = []
        for domain_record in domain_records:
            res = domain_record.to_dict()
            try:
                ips = socket.getaddrinfo(domain_record.domain, None)
                res['addr_info'] = list(set([ip[4][0] for ip in ips]))
            except Exception:
                res['addr_info'] = []
            res['host'] = host_map.get(domain_record.host_id)
            result.append(res)
        return result

    @classmethod
    def save_domain_record(cls, data):
        if data.get('id'):
            domain_record = DomainRecord.select().get(data.get('id'))
            domain_record.fill_model(domain_record, data)
            domain_record.update()
        else:
            domain_record = DomainRecord()
            domain_record.fill_model(domain_record, data)
            domain_record.insert()
        domain_record = DomainRecord.select().filter(DomainRecord.domain == data.get('domain')).one()
        return domain_record.id

    @classmethod
    def generate_valid_node_port(cls):
        services = K8sService.list_service()
        node_ports = []
        for service in services:
            if service.get('type') == 'NodePort':
                node_ports.extend([port.get('node_port') for port in service.get('ports')])
        k8s_node_port_range = ConfigUtil.get_dict_property(config.K8S_NODE_PORT_RANGE)
        all_valid_node_ports = [i for i in range(k8s_node_port_range[0], k8s_node_port_range[1])]
        valid_node_ports = list(set(all_valid_node_ports) ^ set(node_ports))
        return valid_node_ports[random.randint(0, len(valid_node_ports))]