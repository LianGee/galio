#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : harbor_service.py
# @Author: zaoshu
# @Date  : 2020-06-28
# @Desc  :
import config
from common.config_util import ConfigUtil
from common.exception import ServerException
from common.http_util import HttpUtil
from model.project import Project


class HarborService:
    harbor_host = ConfigUtil.get_str_property(key=config.HARBOR_HOST)
    harbor_app_project_name = ConfigUtil.get_str_property(config.HARBOR_APP_PROJECT_NAME)
    harbor_api = f'https://{ConfigUtil.get_str_property(config.HARBOR_HOST)}/api'
    harbor_base_project_name = ConfigUtil.get_str_property(config.HARBOR_BASE_PROJECT_NAME)

    @classmethod
    def search(cls, q):
        url = f'{cls.harbor_api}/search?q={q}'
        http_util = HttpUtil(
            url=url
        )
        response = http_util.get()
        return response.json()

    @classmethod
    def get_base_project(cls):
        response = cls.search(q=cls.harbor_base_project_name)
        projects = response.get('project')
        for project in projects:
            if project.get('name') == cls.harbor_base_project_name:
                return project
        raise ServerException(msg=f'{cls.harbor_base_project_name}不存在，请检查harbor设置')

    @classmethod
    def get_repository_tags(cls, name):
        url = f"{cls.harbor_api}/repositories/{name}/tags?detail=true"
        http_util = HttpUtil(url)
        return http_util.get().json()

    @classmethod
    def list_base_repository(cls, page_num=1, page_size=10):
        base_project = cls.get_base_project()
        base_project_id = base_project.get('project_id')
        url = f'{cls.harbor_api}/repositories?page={page_num}&page_size={page_size}&project_id={base_project_id}'
        http_util = HttpUtil(url)
        response = http_util.get()
        return response.json()

    @classmethod
    def list_base_image(cls, page_num=1, page_size=10):
        base_repositories = cls.list_base_repository(page_num, page_size)
        images = []
        for repository in base_repositories:
            tags = cls.get_repository_tags(name=repository.get('name'))
            for tag in tags:
                tag_name = tag.pop('name')
                images.append(dict({
                    'name': f"{cls.harbor_host}/{repository.get('name')}:{tag_name}"

                }, **tag))
        return images

    @classmethod
    def list_project_image(cls, project_id):
        project = Project.select().get(project_id)
        url = f'{cls.harbor_api}/repositories/{cls.harbor_app_project_name}/{project.name}/tags'
        http_util = HttpUtil(url)
        tags = http_util.get().json()
        images = []
        for tag in tags:
            tag_name = tag.pop('name')
            images.append(dict({
                'name': f'{cls.harbor_host}/{cls.harbor_app_project_name}/{project.name}:{tag_name}'
            }, **tag))
        return images
