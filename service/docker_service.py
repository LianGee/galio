#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : docker_service.py
# @Author: zaoshu
# @Date  : 2020-04-19
# @Desc  :

import docker
from sqlalchemy import func, distinct

from model.build import BuildLog
from model.project import Project


class DockerService:
    client = docker.from_env()

    @classmethod
    def list_image(cls):
        images = cls.client.images.list()
        result = []
        image_names = [image_name[0] for image_name in BuildLog.select(distinct(BuildLog.image_name)).all()]
        for image in images:
            if len(image.tags) > 0 and image.tags[-1] in image_names:
                result.append({
                    'id': image.id,
                    'name': image.tags[-1],
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
