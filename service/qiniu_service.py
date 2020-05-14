#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : qiniu_service.py
# @Author: zaoshu
# @Date  : 2020-04-13
# @Desc  :
from qiniu import Auth, put_file, put_data, BucketManager

import config
from common import enc_util
from common.config_util import ConfigUtil
from common.logger import Logger

log = Logger(__name__)


class QiniuService:
    auth = Auth(
        access_key=ConfigUtil.get_str_property(key=config.QINIU_ACCESS_KEY),
        secret_key=ConfigUtil.get_str_property(key=config.QINIU_SECRET_KEY)
    )

    @classmethod
    def upload_doc(cls, data, file_name=None):
        token = cls.auth.upload_token(bucket=ConfigUtil.get_str_property(key=config.QINIU_GALIO_BUCKET))
        bucket = BucketManager(cls.auth)
        if file_name is None:
            file_name = enc_util.md5(data)
        status, response = bucket.stat(bucket=ConfigUtil.get_str_property(key=config.QINIU_GALIO_BUCKET), key=file_name)
        if status is not None:
            log.info(f'{file_name}已存在, 尝试删除文件后上传')
            status, response = bucket.delete(
                bucket=ConfigUtil.get_str_property(key=config.QINIU_GALIO_BUCKET),
                key=file_name
            )
            log.info(f'delete status={status} response={response}')
        ret, res = put_data(up_token=token, key=file_name, data=data, mime_type='text/plain')
        log.info(f'upload data ret={ret} res={res}')
        # 路径最好带参数，否则会走CDN被缓存掉
        return f"{ConfigUtil.get_str_property(key=config.QINIU_GALIO_DOMAIN)}/" \
            f"{ret.get('key')}?hash={ret.get('hash')}"
