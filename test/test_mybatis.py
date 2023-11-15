import datetime

import mybatis_mapper2sql

# pathSource="D:/NEXTWAVE/project/ipc_api"
# mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
#         xml=pathSource + '/mybatis/device_list.xml')
# # statement = mybatis_mapper2sql.get_statement(
# #         mapper, result_type='list', reindent=True, strip_comments=True)
# statement = mybatis_mapper2sql.get_child_statement(mapper,'testSet', reindent=True, strip_comments=False)
# print(statement)

now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d")
print(now)