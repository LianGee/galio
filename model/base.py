#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : base.py
# @Author: zaoshu
# @Date  : 2020-02-06
# @Desc  :
import json
import math
from copy import copy
from datetime import datetime

from sqlalchemy import Column, BigInteger, Boolean

from model.db import db_session, clean_db_session


class BaseModel:
    id = Column(BigInteger, primary_key=True)
    created_at = Column(BigInteger, index=True, default=math.floor(datetime.now().timestamp()))
    updated_at = Column(BigInteger, index=True, default=math.floor(datetime.now().timestamp()))
    is_delete = Column(Boolean, index=True, default=False)

    @classmethod
    def get_session(cls):
        return db_session()

    def __del__(self):
        clean_db_session()

    @classmethod
    def select(cls, *args, **kwargs):
        session = cls.get_session()
        try:
            if len(args) != 0:
                q = session.query(*args, **kwargs)
            else:
                q = session.query(cls, *args, **kwargs)
            return q._clone()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, *args, **kwargs):
        session = self.get_session()
        try:
            self.updated_at = datetime.now().timestamp()
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def insert(self):
        session = self.get_session()
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self):
        session = self.get_session()
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def bulk_insert(cls, lst: []):
        session = cls.get_session()
        try:
            session.bulk_insert_mappings(cls, [obj.__dict__ for obj in lst])
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def to_dict(self):
        result = copy(self.__dict__)
        for k in result.keys():
            try:
                value = json.loads(result[k], encoding="utf-8")
                result[k] = value
            except Exception:
                continue
        result.pop('_sa_instance_state')
        return result

    @classmethod
    def fill_model(cls, model, dic):
        for k in dic.keys():
            if hasattr(model, k):
                setattr(model, k, dic.get(k))
        return model
