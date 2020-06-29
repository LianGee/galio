#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : harbor_service.py
# @Author: zaoshu
# @Date  : 2020-06-28
# @Desc  :
import config
from common.config_util import ConfigUtil
from common.http_util import HttpUtil


class HarborService:

    @classmethod
    def search(cls, q):
        url = f'{ConfigUtil.get_str_property(config.HARBOR_HOST)}/search?q={q}'
        http_util = HttpUtil(
            url=url
        )
        response = http_util.get()
        return response.json()

    @classmethod
    def get_base_project(cls):
        base_project = ConfigUtil.get_str_property(config.HARBOR_BASE_PROJECT_NAME)
        response = cls.search(q=base_project)
        projects = response.get('project')
        for project in projects:
            if project.get('name') == base_project:
                return project
        return None

    @classmethod
    def get_repository_tags(cls, name):
        url = f"{ConfigUtil.get_str_property(config.HARBOR_HOST)}/repositories/{name}/tags?detail=true"
        http_util = HttpUtil(url)
        return http_util.get().json()

    @classmethod
    def list_base_repository(cls, page_num=1, page_size=10):
        base_project = cls.get_base_project()
        base_project_id = base_project.get('project_id')
        url = f"{ConfigUtil.get_str_property(config.HARBOR_HOST)}/repositories?" \
            f"page={page_num}&page_size={page_size}&project_id={base_project_id}"
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
                    'name': f"{repository.get('name')}:{tag_name}"

                }, **tag))
        return images
