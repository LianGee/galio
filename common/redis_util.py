#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : redis_util.py
# @Author: zaoshu
# @Date  : 2020-03-12
# @Desc  :
import redis

import config

pool = redis.ConnectionPool(
    host=config.REDIS_CACHE.get('CACHE_REDIS_HOST'),
    port=config.REDIS_CACHE.get('CACHE_REDIS_PORT'),
)
r = redis.StrictRedis(connection_pool=pool)
