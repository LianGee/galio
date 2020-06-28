#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : build_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import os
import shutil
from datetime import datetime

from flask_socketio import emit

from common.constant import ProgressType
from common.exception import ServerException
from common.logger import Logger
from model.build_log import BuildLog
from model.entity.progress import Progress
from model.project import Project
from service.docker_service import DockerService
from service.git_service import GitService
from service.package_service import PackageService

log = Logger(__name__)


class BuildService:
    def __init__(self, workspace, project: Project, branch, description=None, user=None):
        self.workspace = workspace
        self.project = project
        self.branch = branch
        self.user = user
        self.status = 0
        self.description = description if description else f"{branch}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.image_name = f'{project.name}:{branch}'
        self.code_path = f'{self.workspace}/project/{project.name}'
        self.target_path = f'{self.workspace}/target/{project.name}'
        self.log_path = f"{self.workspace}/log/{self.project.name}/{int(datetime.now().timestamp())}.log"
        self.progress = Progress()
        self.log_file = None
        self.build_log = None

    def build(self):
        self.before_build()
        self.console(f'代码目录{self.code_path}')
        self.console(f'目标目录{self.target_path}')
        self.console(f'日志目录{self.log_path}')
        git_service = GitService(
            code_path=self.code_path,
            project=self.project,
            branch=self.branch,
            console=self.console
        )
        package_service = PackageService(
            project=self.project,
            console=self.console,
            code_path=self.code_path,
            target_path=self.target_path
        )
        try:
            self.before_progress(description='拉取代码')
            git_service.pull_project()
            self.after_progress(description='代码拉取成功', percent=25)

            self.before_progress(description='打包项目')
            package_service.package_project()
            self.after_progress(description='项目打包成功', percent=30)

            self.before_progress(description='构建镜像')
            DockerService.build(
                self.target_path,
                tag=self.image_name,
                console=self.console,
                dockerfile='dockerfile',
            )
            self.after_progress(description='镜像构建完成', percent=55)
            self.status = 1
            self.console('恭喜，构建成功!')
        except Exception as e:
            log.exception(e)
            self.status = 2
            self.build_log.reason = e.__str__()
            self.console(f'{self.build_log.uuid}构建失败:{e.__str__()}')
            self.progress.type = ProgressType.ERROR
            self.progress.description = e.__str__()
            emit('progress', self.progress.__dict__)
        finally:
            if self.log_file:
                self.log_file.close()
            self.log_build()
            emit('done', self.build_log.to_dict())

    def before_build(self):
        if os.path.exists(self.target_path):
            shutil.rmtree(self.target_path, ignore_errors=True)
        os.makedirs(self.target_path)
        if not os.path.exists(self.code_path):
            os.makedirs(self.code_path)
        if not os.path.exists(f'{self.workspace}/log/{self.project.name}'):
            os.makedirs(f'{self.workspace}/log/{self.project.name}')
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
        self.log_file = open(self.log_path, 'w+')

    def before_progress(self, description):
        self.progress.current += 1
        self.progress.type = ProgressType.PROGRESS
        self.progress.description = description
        emit('progress', self.progress.__dict__)

    def after_progress(self, description, percent):
        self.progress.percent += percent
        self.progress.type = ProgressType.FINISH
        self.progress.description = description
        emit('progress', self.progress.__dict__)

    def log_build(self):
        self.build_log.status = self.status
        self.build_log.update()

    def console(self, message):
        msg = f"[{datetime.now().strftime('%y-%m-%d %H:%M:%S')}]-{message}"
        log.info(msg)
        emit('console', msg)
        if hasattr(self.log_file, 'write'):
            self.log_file.write(f'{msg}\n')

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

    @classmethod
    def recent_build(cls, user_name):
        build_log = BuildLog.select().filter(
            BuildLog.user_name == user_name
        ).order_by(BuildLog.created_at.desc()).first()
        return build_log

    # todo 启用定时任务，每个项目保留20次构建
    @classmethod
    def clean_log(cls):
        log.info('开始清理build log记录')
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
        log.info('build log清理完毕')
