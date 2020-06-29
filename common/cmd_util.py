#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cmd_util.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
from subprocess import Popen, PIPE, STDOUT

from common.exception import ServerException
from common.logger import Logger

log = Logger(__name__)


class CmdUtil:

    @classmethod
    def run(cls, cmd, console=print, t=True):
        assert cmd is not None
        assert console is not None
        console(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        for line in iter(p.stdout.readline, b''):
            line = line.rstrip().decode('utf8')
            console(line)
        p.communicate()
        if p.returncode and t:
            raise ServerException(msg=f'命令{cmd}执行失败')


