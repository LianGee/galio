#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : docker_service.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :

import docker

from common.logger import Logger
from model.project import Project

log = Logger(__name__)


class DockerService:
    client = docker.from_env()

    @classmethod
    def list_image(cls):
        images = cls.client.images.list()
        result = []
        for image in images:
            result.append({
                'id': image.id,
                'name': image.tags[-1] if len(image.tags) > 0 else 'none',
                'author': image.attrs.get('Author'),
                'size': image.attrs.get('Size'),
                'created_at': image.attrs.get('Created'),
            })
        return result

    @classmethod
    def list_project_image(cls, project_id):
        images = cls.client.images.list()
        project = Project.select().get(project_id)
        result = []
        for image in images:
            if len(image.tags) == 0 or image.tags[-1].split(':')[0] != project.name:
                continue
            result.append({
                'id': image.id,
                'name': image.tags[-1],
                'author': image.attrs.get('Author'),
                'size': image.attrs.get('Size'),
                'created_at': image.attrs.get('Created'),
            })
        return result

    @classmethod
    def clean_docker(cls):
        log.info('准备清理镜像')
        images = cls.client.images.list()
        for image in images:
            if len(image.tags) == 0:
                cls.client.images.remove(image.id, True, False)
        log.info('镜像清理完毕')

    # def clean_container(self):
    #     self.log('清理镜像')
    #     cmd = 'docker rmi $(docker images -f "dangling=true" -q)'
    #     CmdUtil.run(cmd, console=self.log, t=False)
    #     cmd = "docker rmi $(docker images | grep \"None\" | awk '{print $3}')"
    #     CmdUtil.run(cmd, console=self.log, t=False)
    #     self.log('清理容器')
    #     cmd = "docker stop $(docker ps -a | grep \"Exited\" | awk '{print $1 }')"
    #     CmdUtil.run(cmd, console=self.log, t=False)
    #     cmd = "docker rm $(docker ps -a | grep \"Exited\" | awk '{print $1 }')"
    #     CmdUtil.run(cmd, console=self.log, t=False)
    #     CmdUtil.run('docker images', console=self.log)

    @classmethod
    def test(cls):
        pass

    @classmethod
    def build(cls, path, dockerfile, tag, console):
        build_log = []
        try:
            console('构建镜像中，请耐心等待')
            response = cls.client.images.build(
                path=path,
                tag=tag,
                nocache=False,
                rm=True,
                dockerfile=dockerfile
            )
            build_log = response[1]
        except Exception as e:
            build_log = e.build_log if hasattr(e, 'build_log') else []
            console('很遗憾，构建镜像失败')
            raise e
        finally:
            for info in build_log:
                i = info.get('stream', '').strip()
                if len(i) > 0:
                    console(i)
            console('恭喜，构建成功！')
