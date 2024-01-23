import asyncio
import datetime
from time import sleep

import mysql.connector
# # statement = mybatis_mapper2sql.get_child_statement(mapper,'insert_data_fruits', reindent=True, strip_comments=False)
# import sqlalchemy_utils
# pathSource="D:/NEXTWAVE/project/ipc_api"
# mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
#         xml=pathSource + '/mybatis/test.xml')
# from aestate.work.Annotation import (AopModel, Item, JsonIgnore, ReadXml,
#                                      Select, SelectAbst, Table)
from pony.orm import (Database, PrimaryKey, Required, commit, db_session,
                      sql_debug)

# import mybatis_mapper2sql
# from pony.orm.dbapiprovider import DBAPIProvider

# print(statement)
# from sql_athame import sql
# from sqlalchemy import TextAsFrom, alias, text

# param = {
#     "category" : 'apple',
#     "price" : 100
# }
# statement = mybatis_mapper2sql.get_statement(
#         mapper, result_type='list')
# from sqlalchemy_utils import load_query_from_xml

# db = Database()


# # db.generate_mapping(create_tables=True)
# class user(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     fullname = Required(str)
# db.bind(provider='mysql',host= '127.0.0.1',user='root', password = '12345',db = 'nextwave_ipc_dev',port=3307)
# sql_debug(True)
# db.generate_mapping(create_tables=True) 
# with db_session:
#     # User=user.get(id=49)
#     commit()
#     # print(User)
arr = [1, 2, 2, 3, 3, 4, 5, 5]
unique_values = list(set(arr))
print(unique_values)