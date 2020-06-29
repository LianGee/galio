#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : package_service.py
# @Author: zaoshu
# @Date  : 2020-06-19
# @Desc  :
import os
import tarfile
import time

from jinja2 import Template
from pynpm import NPMPackage

from common.cmd_util import CmdUtil
from common.constant import BuildType
from common.exception import ServerException
from model.project import Project
from service.template_service import TemplateService


class PackageService:

    def __init__(self, project: Project, code_path, target_path, console=print):
        self.project = project
        self.code_path = code_path
        self.target_path = target_path
        self.console = console

    def gen_nginx_conf(self):
        template = TemplateService.get_template_by_id(self.project.nginx_template_id)
        nginx_template = Template(template.content)
        nginx_conf = nginx_template.render(project=self.project.to_dict())
        with open(f'{self.target_path}/default.conf', 'w') as f:
            f.write(nginx_conf)
        return nginx_conf

    def gen_docker_file(self):
        target_dockerfile = f'{self.target_path}/dockerfile'
        if self.project.docker_template_id is None:
            src_dockerfile = f'{self.code_path}/dockerfile'
            if not os.path.exists(src_dockerfile):
                raise ServerException(f'{src_dockerfile}不存在')
            with open(src_dockerfile, 'r') as f:
                dockerfile = f.read()
        else:
            template = TemplateService.get_template_by_id(self.project.docker_template_id)
            docker_template = Template(template.content)
            dockerfile = docker_template.render(
                project=self.project.to_dict()
            )
        with open(target_dockerfile, 'w') as f:
            f.write(dockerfile)
        return dockerfile

    def package_project(self):
        self.console(f'开始打包{self.project.name}')
        if self.project.build_type == BuildType.NPM:
            self.package_npm()
        elif self.project.build_type == BuildType.TAR:
            self.package_tar()
        elif self.project.build_type == BuildType.MVN:
            pass
        elif self.project.build_type == BuildType.GRADLE:
            self.package_gradle()
        elif self.project.build_type == BuildType.USER_DEFINE:
            pass
        else:
            raise ServerException(msg=f'unknown build type {self.project.build_type}')
        if self.project.nginx_template_id is not None:
            self.console(f'生成nginx file default.conf')
            self.console(self.gen_nginx_conf())
        self.console(f'生成dockerfile')
        self.console(self.gen_docker_file())
        self.console(f'{self.project.name}打包完成')

    '''
        将源代码打包成dist放在target目录下
    '''

    def package_npm(self):
        pkg = NPMPackage(f'{self.code_path}/package.json')
        self.console('正在执行npm install，请稍后...')
        p = pkg.install(wait=False)
        for line in iter(p.stdout.readline, b''):
            line = line.rstrip().decode('utf8')
            self.console(line)
        self.console('正在执行npm build，此过程可能需要几分钟，请耐心等待...')
        p = pkg.run_script('build', '--report', wait=False)
        flag = True
        for line in iter(p.stdout.readline, b''):
            line = line.rstrip().decode('utf8', 'ignore')
            if '● Webpack' in line:
                flag = False
            if '✔ Webpack' in line:
                flag = True
            if line.isprintable() and flag:
                self.console(line)
                time.sleep(0.05)
        self.package_tar(sub_path='dist')

    '''
        将源代码打成tar包放在target目录下
    '''

    def package_tar(self, sub_path=None):
        if sub_path:
            src_path = f'{self.code_path}/{sub_path}/'
        else:
            src_path = f'{self.code_path}/'
        t = tarfile.open(f"{self.target_path}/{self.project.name}.tar.gz", "w:gz")
        for root, dirs, files in os.walk(src_path):
            if '.git' in root:
                continue
            for file in files:
                if sub_path is None:
                    arcname = os.path.join(root.replace(src_path, './'), file)
                else:
                    arcname = os.path.join(root.replace(src_path, f'./{sub_path}'), file)
                t.add(
                    os.path.join(root, file),
                    arcname=arcname
                )
        t.close()

    '''
        将源代码打包成jar包
    '''

    def package_gradle(self):
        cmd = f'cd {self.code_path} && gradle clean build'
        CmdUtil.run(cmd, console=self.console)
