#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : db_inst.py
# @Author: zaoshu
# @Date  : 2020-04-15
# @Desc  :
from flask import Blueprint, request

from common.log import log_this
from common.login import login_required
from common.response import Response
from service.db_service import DBInstService

db_inst_bp = Blueprint('db_inst', __name__)


@db_inst_bp.route('/list')
@login_required
@log_this
def db_inst_list():
    return Response.success(data=DBInstService.list())


@db_inst_bp.route('/ip/list')
@login_required
@log_this
def db_inst_ip_list():
    return Response.success(data=DBInstService.ip_list())


@db_inst_bp.route('/database/list')
@login_required
@log_this
def db_inst_schema():
    id = request.args.get('id')
    return Response.success(data=DBInstService.get_all_database(id))


@db_inst_bp.route('/table/list')
@login_required
@log_this
def db_inst_tables():
    id = request.args.get('id')
    database = request.args.get('database')
    return Response.success(data=DBInstService.get_table_list(id, database))


@db_inst_bp.route('/query', methods=['POST'])
@login_required
@log_this
def db_inst_query():
    id = request.json.get('id')
    database = request.json.get('database')
    sql = request.json.get('sql')
    assert id is not None
    assert database is not None
    assert sql is not None
    return Response.success(data=DBInstService.query(id, database, sql))
