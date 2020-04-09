#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : enc_util.py
# @Author: zaoshu
# @Date  : 2020-02-10
# @Desc  :
import hashlib


def md5(s: str) -> str:
    if isinstance(s, bytes):
        s = s.decode('ISO-8859-1')
    m = hashlib.md5()
    m.update(s.encode('utf8'))
    return m.hexdigest()
