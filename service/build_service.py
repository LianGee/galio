#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : build_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import os
from datetime import datetime

from flask_socketio import emit
from jinja2 import Template

import config
from common.cmd_util import CmdUtil
from common.config_util import ConfigUtil
from common.constant import BuildType
from common.exception import ServerException
from common.logger import Logger
from model.build import BuildLog
from model.project import Project
from service.git_service import GitService
from service.template_service import TemplateService

log = Logger(__name__)


class BuildService:
    def __init__(self, workspace, project: Project, branch, description=None, user=None, console=log.info):
        self.workspace = workspace
        self.project = project
        self.branch = branch
        self.console = console
        self.user = user
        self.status = 0
        self.description = description if description else f"{branch}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.image_name = f'{project.name}:{branch}'
        self.target = os.path.join(self.workspace, f'target/{self.project.name}')
        self.code_path = f'{self.workspace}/project/{self.project.name}'
        self.log_dir = os.path.join(self.workspace, f'log/{self.project.name}')
        self.log_path = f"{self.log_dir}/{int(datetime.now().timestamp())}.log"
        self.log_file = None
        self.build_log = None

    def gen_nginx_conf(self):
        self.log('generate nginx file begin')
        template = TemplateService.get_template_by_id(self.project.nginx_template_id)
        nginx_template = Template(template.get('content'))
        nginx_conf = nginx_template.render(
            project=self.project, template=template
        )
        self.log(nginx_conf)
        with open(f"{self.target}/lib/{template.get('name')}", 'w', encoding='utf-8') as f:
            f.write(nginx_conf)
        self.log('generate dockerfile success')
        return f"{self.target}/lib/{template.get('name')}"

    def gen_docker_file(self):
        self.log('generate dockerfile begin')
        template = TemplateService.get_template_by_id(self.project.docker_template_id)
        docker_template = Template(template.get('content'))
        dockerfile = docker_template.render(
            project=self.project, template=template
        )
        self.log(dockerfile)
        with open(f'{self.target}/src/dockerfile', 'w', encoding='utf-8') as f:
            f.write(dockerfile)
        self.log('generate dockerfile success')
        return f'{self.target}/src/dockerfile'

    def package(self):
        pass

    def clean(self):
        self.log('clean target begin')
        if os.path.exists(self.target):
            cmd = f'rm -rf {self.target}/lib/*'
            CmdUtil.run(cmd, console=self.log)
        self.log('clean target end')

    def package_python(self):
        self.log('package source code begin')
        self.clean()
        cmd = f'cd {self.code_path} && tar czvf {self.project.name}.tar ./'
        CmdUtil.run(cmd, console=self.log)
        cmd = f'mv {self.code_path}/{self.project.name}.tar {self.target}/lib'
        CmdUtil.run(cmd, console=self.log)
        self.log('package source code success')

    def clean_container(self):
        self.log('清理镜像')
        cmd = 'docker rmi $(docker images -f "dangling=true" -q)'
        CmdUtil.run(cmd, console=self.log, t=False)
        cmd = "docker rmi $(docker images | grep \"None\" | awk '{print $3}')"
        CmdUtil.run(cmd, console=self.log, t=False)
        self.log('清理容器')
        cmd = "docker stop $(docker ps -a | grep \"Exited\" | awk '{print $1 }')"
        CmdUtil.run(cmd, console=self.log, t=False)
        cmd = "docker rm $(docker ps -a | grep \"Exited\" | awk '{print $1 }')"
        CmdUtil.run(cmd, console=self.log, t=False)
        CmdUtil.run('docker images', console=self.log)

    def build_python(self, version='2'):
        dockerfile = self.gen_docker_file()
        self.package_python()
        cmd = f'docker build -f {dockerfile} -t {self.project.name}:{self.branch} --force-rm {self.target}/lib'
        CmdUtil.run(cmd, console=self.log)
        self.clean_container()

    def package_dist(self):
        self.log('package source code begin')
        self.clean()
        cmd = f'cd {self.code_path} && npm install'
        CmdUtil.run(cmd, console=self.log)
        cmd = f'cd {self.code_path} && npm run build'
        CmdUtil.run(cmd, console=self.log)
        cmd = f'cd {self.code_path} && tar czvf {self.project.name}.tar ./dist'
        CmdUtil.run(cmd, console=self.log)
        cmd = f'mv {self.code_path}/{self.project.name}.tar {self.target}/lib'
        CmdUtil.run(cmd, console=self.log)
        self.log('package source code success')

    def build_dist(self):
        if not os.path.exists(f'{self.code_path}/dist'):
            self.log(f'dist 不存在 {self.code_path}/dist，请本地构建后上传dist文件到git上')
        self.package_dist()
        nginx_conf = self.gen_nginx_conf()
        dockerfile = self.gen_docker_file()
        cmd = f'docker build -f {dockerfile} -t {self.project.name}:{self.branch} --force-rm {self.target}/lib'
        CmdUtil.run(cmd, console=self.log)
        self.clean_container()

    def build_java_with_mvn(self, mvn_version='3.6'):
        pass

    def build_java_with_gradle(self, gradle_version='4.10.14'):
        pass

    def build(self):
        self.before_build()
        try:
            if self.project.build_type == BuildType.DIST:
                self.build_dist()
            elif self.project.build_type == BuildType.PYTHON2:
                self.build_python(version='2')
            elif self.project.build_type == BuildType.PYTHON3:
                self.build_python(version='3')
            elif self.project.build_type == BuildType.JAVA8_MAVEN_3:
                self.build_java_with_mvn()
            elif self.project.build_type == BuildType.JAVA8_GRADLE_4:
                self.build_java_with_gradle()
            else:
                raise ServerException(msg=f'unknown build type {self.project.build_type}')
            self.status = 1
        except Exception:
            self.status = 2
        finally:
            if self.log_file:
                self.log_file.close()
            self.log_build()

    def before_build(self):
        self.build_log = BuildLog(
            project_name=self.project.name,
            branch=self.branch,
            user_name=self.user.get('name'),
            image_name=self.image_name,
            description=self.description,
            status=self.status,
            log_path=self.log_path
        )
        self.build_log.insert()
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        if not os.path.exists(self.target):
            os.makedirs(self.target)
            os.makedirs(f'{self.target}/lib', exist_ok=True)
            os.makedirs(f'{self.target}/src', exist_ok=True)
        self.log_file = open(self.log_path, 'w+')
        git_service = GitService(
            workspace=f'{self.workspace}/project',
            project=self.project,
            branch=self.branch
        )
        self.log('初始化仓库')
        git_service.init()
        self.log('拉取master')
        git_service.pull()
        self.log('切换分支')
        git_service.check_out_branch()
        self.log('拉取分支代码')
        git_service.pull()
        self.log(f'代码拉取完毕: {self.code_path}')

    def log_build(self):
        self.build_log.status = self.status
        self.build_log.update()
        emit('build_event', self.build_log.to_dict())

    def log(self, message):
        self.console(message)
        if hasattr(self.log_file, 'write'):
            self.log_file.write(f"[{datetime.now().strftime('%y-%m-%d %H:%M:%S')}]-{message}\n")

    @classmethod
    def get_logs(cls, user_name):
        return BuildLog.select().filter(BuildLog.user_name == user_name) \
            .order_by(BuildLog.created_at.desc()).all()

    @classmethod
    def get_log_content(cls, log_path):
        if log_path is None or log_path == '':
            raise ServerException('日志不存在')
        with open(log_path) as f:
            content = f.read()
        return content
