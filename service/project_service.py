#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : project_service.py
# @Author: zaoshu
# @Date  : 2020-04-09
# @Desc  :
from model.project import Project


class ProjectService:

    @classmethod
    def save(cls, data, user_name):
        if data.get('id') is None:
            project = Project.fill_model(Project(), data)
            project.user_name = user_name
            project.insert()
            return Project.select().filter(Project.name == data.get('name')).one().id
        else:
            project = Project.select().get(data.get('id'))
            project = Project.fill_model(project, data)
            project.user_name = user_name
            project.update()
            return data.get('id')

    @classmethod
    def list(cls, user_name):
        return Project.select().filter(Project.user_name == user_name).all()
