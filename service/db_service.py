#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : db_service.py
# @Author: zaoshu
# @Date  : 2020-04-15
# @Desc  :
import mysql.connector

import config
from common.config_util import ConfigUtil
from model.db_inst import DBInst


class DBInstService:

    @classmethod
    def list(cls):
        return DBInst.select().all()

    @classmethod
    def ip_list(cls):
        db_inst_list = DBInst.select().all()
        res = []
        for db_inst in db_inst_list:
            res.append({
                'id': db_inst.id,
                'ip': db_inst.ip,
                'user_name': db_inst.user_name
            })
        return res

    @classmethod
    def save(cls, data):
        if data.get('id') is None:
            db_inst = DBInst(**data)
            db_inst.insert()
        else:
            db_inst = DBInst.select().get(data.get('id'))
            db_inst = DBInst.fill_model(db_inst, data)
            db_inst.update()
        return True

    @classmethod
    def get_all_database(cls, id):
        db, cursor = cls._get_db_cursor(id)
        try:
            cursor.execute('show databases')
            return [db[0] for db in cursor.fetchall()]
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_table_list(cls, id, database):
        db, cursor = cls._get_db_cursor(id, database)
        sql = f"select " \
            f"t.TABLE_SCHEMA," \
            f"t.TABLE_NAME," \
            f"t.COLUMN_NAME," \
            f"t.COLUMN_DEFAULT," \
            f"t.COLUMN_TYPE," \
            f"t.COLUMN_COMMENT," \
            f"t.IS_NULLABLE," \
            f"t.EXTRA" \
            f" from INFORMATION_SCHEMA.COLUMNS t where t.TABLE_SCHEMA = '{database}'"
        try:
            cursor.execute(sql)
            tables = cursor.fetchall()
            table_infos = []
            column_infos = {}
            for table in tables:
                key = f'{table[0]}.{table[1]}'
                info = {
                    'schema_name': table[0],
                    'table_name': table[1],
                    'column_name': table[2],
                    'column_default': table[3],
                    'column_type': table[4],
                    'column_comment': table[5],
                    'is_nullable': table[6],
                    'extra': table[7]
                }
                if column_infos.get(key, None) is None:
                    column_infos[key] = [info]
                else:
                    column_infos.get(key).append(info)
            count = 0
            for k in column_infos.keys():
                table_infos.append({
                    'id': count,
                    'table_name': column_infos[k][0]['table_name'],
                    'columns': column_infos[k]
                })
                count += 1
            return table_infos
        except Exception as e:
            print(e)
        finally:
            db.close()

    @classmethod
    def query(cls, id, database, sql):
        db, cursor = cls._get_db_cursor(id, database)
        try:
            cursor.execute(sql)
            data = cursor.fetchmany(ConfigUtil.get_int_property(config.QUERY_MAX_SIZE))
            column_names = cursor.column_names
            result = []
            for d in data:
                res = {}
                for i in range(len(column_names)):
                    res[column_names[i]] = d[i]
                result.append(res)
            return {
                'columns': column_names,
                'total': len(data),
                'result': result
            }
        except Exception as e:
            print(e)
        finally:
            db.close()

    @classmethod
    def _get_db_cursor(cls, id, database=None):
        db_inst: DBInst = DBInst.select().get(id)
        if database is not None:
            db = mysql.connector.connect(
                host=db_inst.ip,
                user=db_inst.user_name,
                password=db_inst.password,
                port=db_inst.port,
                database=database
            )
        else:
            db = mysql.connector.connect(
                host=db_inst.ip,
                user=db_inst.user_name,
                password=db_inst.password,
                port=db_inst.port,
            )
        cursor = db.cursor()
        return db, cursor
