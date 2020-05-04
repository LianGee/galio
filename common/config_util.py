#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config_util.py
# @Author: zaoshu
# @Date  : 2020-04-06
# @Desc  :
import json

from cacheout import Cache

from common.env_util import is_prod
from common.http_util import HttpUtil

cache = Cache()


class ConfigUtil:

    @classmethod
    def get_str_property(cls, key, default=None):
        properties = cls.get_all_properties()
        return properties.get(key, default)

    @classmethod
    def get_int_property(cls, key, default=None):
        properties = cls.get_all_properties()
        return int(properties.get(key, default))

    @classmethod
    def get_dict_property(cls, key, default=None):
        properties = cls.get_all_properties()
        return json.loads(properties.get(key, default))

    @classmethod
    def get_bool(cls, key, default=False):
        properties = cls.get_all_properties()
        return properties.get(key, default) is 'true'

    @classmethod
    @cache.memoize(ttl=60)
    def get_all_properties(cls,
                           app_id='galio',
                           cluster_name='default',
                           namespace_name='application'):
        assert app_id is not None
        assert cluster_name is not None
        assert namespace_name is not None
        if is_prod():
            server_url = 'http://pro.apollo.client.bchen.xyz/'
        else:
            server_url = 'http://dev.apollo.client.bchen.xyz/'
        http_util = HttpUtil(
            url=f'{server_url}/configfiles/json/{app_id}/{cluster_name}/{namespace_name}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': ''
            }
        )
        return http_util.get().json()
