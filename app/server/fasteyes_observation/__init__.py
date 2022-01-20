import csv
import json
import os
import shutil

from app.core.config import FASTEYES_OUTPUT_PATH
from app.server.fasteyes_observation.crud import output_observations_by_group, get_attendence_by_time_interval
from datetime import datetime, time
from sqlalchemy.orm import Session


def output_interval_attendance_csv(db: Session, group_id: int, start_timestamp: datetime,
                                   end_timestamp: datetime, status_in: int, select_device_id: int,
                                   working_time_1: time,
                                   working_time_2: time,
                                   working_time_off_1: time,
                                   working_time_off_2: time):
    title = ["員工", "部門", "ID", "最早時間", "體溫", "最晚時間", "體溫", "類型"]
    observation_model_list = get_attendence_by_time_interval(db, group_id, start_timestamp, end_timestamp,
                                                             status_in, select_device_id, working_time_1,
                                                             working_time_2, working_time_off_1, working_time_off_2)

    observation_list = [title]

    for observation_model in observation_model_list:
        each_date_data = observation_model["attendance"]
        for data in each_date_data:
            each_data = []
            status = "正常"
            if "staff_name" in data:
                each_data.append(data["staff_name"])
            else:
                each_data.append("Unknow")

            if "department_name" in data:
                each_data.append(data["department_name"])
            else:
                each_data.append("訪客")

            if "staff_serial_number" in data:
                each_data.append(data["staff_serial_number"])
            else:
                each_data.append("None")

            if "punch_in" in data:
                each_data.append(data["punch_in"])
            else:
                each_data.append("無資料")

            if "punch_in_temperature" in data:
                each_data.append(data["punch_in_temperature"])
            else:
                each_data.append("無資料")

            if "punch_out" in data:
                each_data.append(data["punch_out"])
            else:
                each_data.append("無資料")

            if "punch_out_temperature" in data:
                each_data.append(data["punch_out_temperature"])
            else:
                each_data.append("無資料")

            if "punch_in_temperature_result" in data and "punch_out_temperature_result" in data:
                if data["punch_in_temperature_result"] or data["punch_out_temperature_result"]:
                    status = "異常"
            else:
                status = "異常"

            each_data.append(status)
            observation_list.append(each_data)

    # print(observation_list)
    file_location = FASTEYES_OUTPUT_PATH + str(group_id) + '/fasteyes_attendance_data.csv'
    with open(file_location, 'w', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for eachdata in observation_list:
            w.writerow(eachdata)

    return file_location


def output_interval_data_csv(db, group_id, start_timestamp, end_timestamp):
    path = FASTEYES_OUTPUT_PATH + str(group_id) + "/output_form.json"
    # Opening JSON file
    f = open(path)
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Closing file
    f.close()

    output_fasteyes = data["output_fasteyes"]
    output_sequence = data["output_sequence"]
    resign_staff_output = data["resign_staff_output"]
    name_list = [sequence["english_name"] for sequence in output_sequence]
    output_fasteyes_list = [each_fasteyes["id"] for each_fasteyes in output_fasteyes]
    title = [sequence["name"] for sequence in output_sequence]

    observation_model_list = output_observations_by_group(db, group_id, start_timestamp, end_timestamp,
                                                          resign_staff_output, output_fasteyes_list)

    observation_list = []
    observation_list.append(title)
    for observation_model in observation_model_list:
        observation_dict = observation_model.__dict__
        each_data = []
        for each_item in name_list:
            if each_item in observation_dict.keys():
                if each_item == "result":
                    if observation_dict[each_item] == 1:
                        each_data.append("異常")
                    else:
                        each_data.append("正常")
                else:
                    each_data.append(observation_dict[each_item])
            elif each_item in observation_dict["info"].keys():
                if each_item == "wear_mask":
                    if observation_dict["info"][each_item] == 1:
                        each_data.append("有戴口罩")
                    else:
                        each_data.append("未戴口罩")
                elif each_item == "temperature" or each_item == "threshold_temperature" or each_item == "compensate_temperature":
                    each_data.append(str(observation_dict["info"][each_item]) + "°C")
                else:
                    each_data.append(observation_dict["info"][each_item])

        observation_list.append(each_data)

    # print(observation_list)
    file_location = FASTEYES_OUTPUT_PATH + str(group_id) + '/fasteyes_observation_data.csv'
    with open(file_location, 'w', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for eachdata in observation_list:
            w.writerow(eachdata)

    return file_location


def get_output_data_form(group_id):
    path = FASTEYES_OUTPUT_PATH + str(group_id) + "/output_form.json"
    # Opening JSON file
    f = open(path)
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Closing file
    f.close()
    return data


def modify_output_data_form(group_id, output_form):
    path = FASTEYES_OUTPUT_PATH + str(group_id) + "/output_form.json"
    with open(path, "w") as outfile:
        json.dump(output_form.__dict__, outfile)
    return output_form


def create_output_data_form(group_id):
    source = "sample.json"

    destination = FASTEYES_OUTPUT_PATH + str(group_id) + "/output_form.json"

    if not os.path.exists(FASTEYES_OUTPUT_PATH):
        os.mkdir(FASTEYES_OUTPUT_PATH)
    if not os.path.exists(FASTEYES_OUTPUT_PATH + str(group_id)):
        os.mkdir(FASTEYES_OUTPUT_PATH + str(group_id))

    shutil.copyfile(source, destination)
    return destination
