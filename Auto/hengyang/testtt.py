# import os
# import datetime
# # first = datetime.datetime.now()
# with open("/Users/judhaha/AIOT_fasteyes-8/Auto/hengyang/hengyang.txt", "r", encoding="utf-8") as file:
#     file_data = file.read()
# all_observation = eval(file_data)
# # observartion = []
# # for i in all_observation:
# #     if "Parameters" in i:
# #         observartion.append(i)
# # second = datetime.datetime.now()
#
# # print(observartion)
# # print(len(observartion))
#
# first_1 = datetime.datetime.now()
# obbo = [i for i in all_observation if "Parameters" in i]
# print(len(obbo))
# first_2 = datetime.datetime.now()
# import time
#
# # serial_number_list = []
# # staff_name_list = []
# # file_name_list = []
# # gender_list = []
# # department_id_list = []
# # status_list = []
# # start_date_list = []
# #
# # with open("/Users/judhaha/AIOT_fasteyes-8/Auto/hengyang/hengyang_staff_info.txt", "r", encoding="utf-8") as file:
# #     file_data = file.read()
# #     staff_info = eval(file_data)
# # first = datetime.datetime.now()
# # # 整理舊資料
# # for info in staff_info:
# #     serial_number_list.append(info["SerialNumber"])
# #     staff_name_list.append(info["Name"])
# #     file_name_list.append(str(info["Id"]) + "_EMP_" + str(info["SerialNumber"]))
# #     # department_id_list.append(int(job.index(info["Department"]) + 1))
# #     start_date_list.append(info["CreatedAt"])
# #     if info["Gender"] == "女" or "Female":
# #         gender_list.append(0)
# #     else:
# #         gender_list.append(1)
# #     if info["Status"] == "在職中":
# #         status_list.append(1)
# #     elif info["Status"] == "離職":
# #         status_list.append(0)
# #     else:
# #         status_list.append(2)
# # second = datetime.datetime.now()
#
#
#
# # print(serial_number_list)
# # print(staff_name_list)
# # print(file_name_list)
# # print(gender_list)
# # print(department_id_list)
# # print(status_list)
# # print(start_date_list)
#
# # print(first)
# # print(second)
#
# print(obbo)
# print(first_1)
# print(first_2)

from app.db.database import SessionLocal
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.models.domain.staff import staff
sessionlocal = SessionLocal()

data = fasteyes_observation(phenomenon_time=observation_in.phenomenon_time,
                                              result=observation_in.result,
                                              image_name=observation_in.image_name,
                                              info=info,
                                              staff_id=observation_in.staff_id,
                                              group_id=group_id,
                                              fasteyes_device_id=fasteyes_device_id)
sessionlocal.add(data)