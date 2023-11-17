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

                     
                     