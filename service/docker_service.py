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

    @classmethod
    def build(cls, path, tag, console, dockerfile):
        build_logs = []
        try:
            console('构建镜像中，请耐心等待...')
            build_logs = cls.client.api.build(
                path=path,
                tag=tag,
                nocache=False,
                rm=True,
                forcerm=True,
                dockerfile=dockerfile,
                decode=True,
            )
        except Exception as e:
            console(e.__str__())
            raise e
        finally:
            for build_log in build_logs:
                info = build_log.get('stream', '').strip()
                if len(info) > 0:
                    console(info)
