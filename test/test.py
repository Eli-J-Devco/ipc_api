import pandas as pd

result_rs485_group = [   {'id':4, 'name': 'MFM383A-1', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 1'}, 
              {'id':5, 'name': 'MFM383A-2', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 1'}, 
              {'id':6, 'name': 'MFM383A-3', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 2'} 
             ]
# df = pd.DataFrame(records)
# print(df)
# no_dups = df.drop_duplicates()
# result=no_dups[no_dups.duplicated(keep = False, subset="Name")]
# print(result)
# print(result[0]["Name"])
# students = ['Python', 'R', 'C#', 'Python', 'R', 'Java']

# new_list = []
# new_list.append()
# for one_student_choice in students:
#     if one_student_choice not in new_list:
#         new_list.append(one_student_choice)

# print(new_list)
# result_rs485_list = [x for i, x in enumerate(result_rs485_group) if x['serialport_name'] not in {y['serialport_name'] for y in result_rs485_group[:i]}]
# # print(new_Data)
# data=[]
# for rs485_item in result_rs485_list:
#        item=[]
#        for device_item in result_rs485_group:
#               if rs485_item["serialport_name"]==device_item["serialport_name"]:
#                     item.append({
#                             'id':device_item['id'],
#                             'name':device_item['name'],
#                             'connect_type':device_item['connect_type'],                            
#                             "serialport_name":rs485_item["serialport_name"]
#                            })
#        data.append(item)
# print(data)

dict_example = {'a': 1, 'b': 2}

print("original dictionary: ", dict_example)

dict_example['a'] = 100  # existing key, overwrite
dict_example['c'] = 3  # new key, add
dict_example['d'] = 4  # new key, add 

print("updated dictionary: ", dict_example)


user={
    "name":"root",
    "pass":1234
}    
print(user)                 
modify_user={
    "pass":4567
}  
                 
user|=modify_user
# 
print(user)
print(f'{4+4=}')
import string

print(string.punctuation)

percent=11111111.2567
print(f'{percent:,.2%}')
data={
    "id":1,
    "name":[{"A":1},{"B":1}],
    "desc":"2222222222222222222222222222222222222222222"
}

from pprint import pprint

pprint(data, sort_dicts=False)

my_list=['sp1','sp2','sp3']

for index, item in enumerate(my_list, 1):
    print(f'{index} :{item}')
my_list=[1,1,1,2,3,4]
import statistics

print(statistics.mode(my_list))

list1=[1,2,3]
list2=[4,5,6]
list1.extend(list2)
print(list1)
data=[
        {"id":1,
        "value":[{"tag1":1}]},
        {"id":2,
        "value":[{"tag1":23}]}
      ]
data={}
data["ID"]=1
data["NAME"]="INV1"
print(data)

