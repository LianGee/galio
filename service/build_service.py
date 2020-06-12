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

from common.cmd_util import CmdUtil
from common.constant import BuildType
from common.exception import ServerException
from common.logger import Logger
from model.build_log import BuildLog
from model.project import Project
from service.docker_service import DockerService
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
        log.info(template.get('content'))
        nginx_conf = nginx_template.render(project=self.project.to_dict())
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

    def npm_build(self):
        if not os.path.exists(f'{self.code_path}/dist'):
            self.package_dist()
        self.gen_nginx_conf()
        dockerfile = self.gen_docker_file()
        DockerService.build(
            path=f'{self.target}/lib',
            dockerfile=dockerfile,
            tag=f'{self.project.name}:{self.branch}',
            console=self.log
        )

    def tar_build(self):
        dockerfile = self.gen_docker_file()
        self.package_python()
        DockerService.build(
            path=f'{self.target}/lib',
            dockerfile=dockerfile,
            tag=f'{self.project.name}:{self.branch}',
            console=self.log
        )

    def mvn_build(self):
        pass

    def gradle_build(self):
        pass

    def user_define_build(self):
        pass

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

    def build(self):
        self.before_build()
        try:
            if self.project.build_type == BuildType.NPM:
                self.npm_build()
            elif self.project.build_type == BuildType.TAR:
                self.tar_build()
            elif self.project.build_type == BuildType.MVN:
                self.mvn_build()
            elif self.project.build_type == BuildType.GRADLE:
                self.gradle_build()
            elif self.project.build_type == BuildType.USER_DEFINE:
                self.user_define_build()
            else:
                raise ServerException(msg=f'unknown build type {self.project.build_type}')
            self.status = 1
        except Exception as e:
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
            log_path=self.log_path,
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

    # todo 启用定时任务，每个项目保留20次构建
    @classmethod
    def clean_log(cls):
        logs = BuildLog.select().order_by(BuildLog.created_at.desc()).all()
        project_record_map = {}
        for _log in logs:
            if project_record_map.get(_log.project_name) is None:
                project_record_map[_log.project_name] = [_log.id]
            elif len(project_record_map.get(_log.project_name, [])) <= 20:
                project_record_map[_log.project_name].append(_log.id)
        not_delete_id = []
        for project_name in project_record_map.keys():
            not_delete_id.extend(project_record_map.get(project_name, []))
        delete_logs = BuildLog.select().filter(BuildLog.id.notin_(not_delete_id))
        for delete_log in delete_logs:
            delete_log.delete()
