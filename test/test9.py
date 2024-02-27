import sys

# if sys.version_info[0] == 3:
#     import tkinter as tk
# else:
#     import Tkinter as tk

# r = tk.Tk()
# r.title('Counting Seconds')
# button = tk.Button(r, text='Stop', width=25,height=20, command=r.destroy)
# button.pack()
# r.mainloop()


data=[{'id': 2, 'name': 'Manager', 'description': None, 'status': True, 
  'screen': [{'id': 1, 'name': 'Overview', 'description': None, 'status': True, 'auth': 1}, 
             {'id': 2, 'name': 'Login', 'description': None, 'status': True, 'auth': 1}]}, 
 {'id': 3, 'name': 'Customer', 'description': None, 'status': True, 
  'screen': [{'id': 1, 'name': 'Overview', 'description': None, 'status': True, 'auth': 2}, 
             {'id': 3, 'name': 'Quick Start', 'description': None, 'status': True, 'auth': 2}]}]
# 
array1 = [1, 2, 3]
array2 = [2, 3, 4]

# combined_array = list(set(array1 + array2))
# print(combined_array)
combined_array=[1,2,3]

role_screen={}
screen_list=[]
for role_item in data:
  for screen_item in role_item["screen"]:
    screen_list.append(screen_item)
    if screen_item["id"] in combined_array:
      id_role="id"+str(screen_item["id"])
      if str(id_role) in role_screen.keys():
        auth=[]
        auth=role_screen[id_role]["auth"]
        auth.append(screen_item["auth"])
        role_screen[id_role]={
          "id":screen_item["id"],
          "auth":auth
        }
      else:
        role_screen[id_role]={
          "id":screen_item["id"],
          "auth":[screen_item["auth"]]
        }
# print(len(screen_list))
new_Data = [x for i, x in enumerate(screen_list) if x['id'] not in {y['id'] for y in screen_list[:i]}]
print(new_Data)
def convert_binary_auth(auth):
    try:
        result_auth=""
        for i,item in enumerate(auth):
            if i < len(auth)-1:
                result_auth=result_auth + str(item)+"|"
            else:
                result_auth=result_auth + str(item)
        if not result_auth:
            return 0
        else:
            return int(bin(eval(result_auth)),2)
    except Exception as err:
        print('Convert_binary_auth: '+err)
        return 0
new_role_screen=[]
for item in new_Data:
    new_item={
      "id":item["id"],
      "auth":convert_binary_auth(role_screen["id"+str(item["id"])]["auth"]),
      "name":item["name"],
      "description":item["description"],
    }
    new_role_screen.append(new_item)
print(new_role_screen)
# print(new_role_screen[0][])