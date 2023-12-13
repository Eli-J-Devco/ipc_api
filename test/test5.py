

import os
import sys

import mybatis_mapper2sql


# arr = sys.argv
# print(f'arr: {arr[1]}')
def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    # print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
      return -1
    result=path_os[0:int(index_os)+len(string_find)]
    # print("Path directory relative:", result)
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
newdict = [{"A":0},{ "B":0},{"C":0}]
def get_mybatis(newdict):
    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/test.xml')
    statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
    result={}
    for item,value in enumerate(statement):
      for key in value.keys():
        result[key]=value[key]   
    print(result)
    return   result  
result=get_mybatis(newdict)
print(result["testParameters"])
