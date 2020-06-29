#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : docker_service.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :

import docker

import config
from common.config_util import ConfigUtil
from common.exception import ServerException
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
            try:
                if len(image.tags) == 0:
                    cls.client.images.remove(image.id, True, False)
            except Exception as e:
                log.exception(f'删除镜像{image.id}失败{e.__str__()}')
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

    @classmethod
    def push(cls, image_name, repository, tag, console):
        try:
            console(f'开始推送镜像{image_name}到{repository}，请稍等...')
            cls.client.api.tag(
                image=image_name,
                repository=repository,
                tag=tag
            )
            response = cls.client.api.push(
                repository=repository,
                tag=tag,
                stream=True,
                decode=True,
                auth_config={
                    'username': ConfigUtil.get_str_property(config.HARBOR_USERNAME),
                    'password': ConfigUtil.get_str_property(config.HARBOR_PASSWORD),
                }
            )
            for line in response:
                if line.get('error') is not None:
                    raise ServerException(msg=line.get('error'))
            console(f'推送镜像{image_name}到{repository}成功')
        except Exception as e:
            console(f'推送镜像{image_name}到{repository}失败：{e.__str__()}')
            raise e
