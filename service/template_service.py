#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : template_service.py
# @Author: zaoshu
# @Date  : 2020-04-13
# @Desc  :
from common.http_util import HttpUtil
from model.template import Template
from service.qiniu_service import QiniuService


class TemplateService:

    @classmethod
    def get_templates(cls, type=None):
        if type is None:
            return Template.select().all()
        else:
            return Template.select().filter(Template.type == type).all()

    @classmethod
    def get_template_by_id(cls, id):
        return Template.select().get(id)

    @classmethod
    def save_template(cls, data):
        if data.get('id') is not None:
            template = Template.select().get(data.get('id'))
            template.fill_model(template, data)
            template.update()
        else:
            template = Template()
            template.fill_model(template, data)
            template.insert()

    @classmethod
    def delete_template(cls, template_id):
        template = Template.select().get(template_id)
        template.delete()
        return True
