import csv
import json

from app.core.config import FASTEYES_OUTPUT_PATH
from app.server.fasteyes_observation.crud import output_observations_by_group


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
        # pop_key = ['_sa_instance_state', ]  # + pop_name_list
        # for key in pop_key:
        #     observation_dict.pop(key, None)
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

    file_location = FASTEYES_OUTPUT_PATH + str(group_id) + '/fasteyes_observation_data.csv'
    with open(file_location, 'w') as f:
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
