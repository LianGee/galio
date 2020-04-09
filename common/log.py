#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : log.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  : 

import logging


class Logger:
    def __init__(self, name=None):
        self.stream_handler = logging.StreamHandler()
        self.formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s:%(thread)s - %(message)s ')
        self.stream_handler.setFormatter(self.formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.stream_handler)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, exception):
        self.logger.exception(exception)

