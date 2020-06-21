#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : progress.py
# @Author: zaoshu
# @Date  : 2020-06-21
# @Desc  :
from common.constant import ProgressType


class Progress:

    def __init__(self, current: int = -1, percent: int = 0, type=ProgressType.WAIT, description='等待开始'):
        self.current = current
        self.percent = percent
        self.type = type
        self.description = description
