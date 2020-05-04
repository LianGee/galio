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
        template = Template.select().get(id)
        res = template.to_dict()
        if template.path is not '':
            http_util = HttpUtil(url=template.path)
            res['content'] = http_util.get().text
        else:
            res['content'] = ''
        return res

    @classmethod
    def save_template(cls, data):
        if data.get('id') is not None:
            template = Template.select().get(data.get('id'))
            template.fill_model(template, data)
            if data.get('content'):
                template.path = QiniuService.upload_doc(data.get('content'), file_name=template.name)
            template.update()
        else:
            template = Template()
            template.fill_model(template, data)
            if data.get('content'):
                template.path = QiniuService.upload_doc(data.get('content'), file_name=template.name)
            template.insert()

    @classmethod
    def delete_template(cls, template_id):
        template = Template.select().get(template_id)
        template.delete()
        return True
