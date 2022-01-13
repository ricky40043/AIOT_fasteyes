import json, random, datetime
from Auto import *
from faker import Faker
from faker_schema.faker_schema import FakerSchema

fake = Faker()
faker = FakerSchema()

# staff 數量 ＋ default, Dave and Ricky
staff = 10

# 過去Ｎ天上班天數
work_day = 3


def get_current_user_header():
    with open(path + 'Default/User_data/Headers.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return {"Authorization": "Bearer " + data["access_token"]}


def get_user_data(user):
    with open(path + 'Default/User_data/' + user + '.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def get_uuid_data(uuid):
    with open(path + 'Default/UUID_data/' + uuid + '.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


################### default ####################
def test_clear_all_data_no_auth():
    url = URL + '/auth/clear_all_data_no_auth'
    response = client.delete(url)
    assert response.status_code == 200


def test_add_RD():
    url = URL + "/users/RD"
    RD_data = get_user_data("RD")
    response = client.post(url, json=RD_data)
    assert response.status_code == 200


def test_Login_RD():
    url = URL + "/auth/login"
    login_data = {
        "email": "Test_RD@fastwise.net",
        "password": "test"
    }
    response = client.post(url, json=login_data)
    print(response.json())
    with open(path + 'Default/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)
    assert response.status_code == 200


def test_create_device_model():
    url = URL + "/device_model"
    name_list = ["Temperature_humidity", "ip_cam", "electrostatic", "Nitrogen"]
    for name in name_list:
        device_name = {
            "name": name
        }
        response = client.post(url, json=device_name, headers=get_current_user_header())
        assert response.status_code == 200


def test_add_AdminUser():
    url = URL + "/users/admin"
    adminusers_data = get_user_data("Admin")
    response = client.post(url, json=adminusers_data)
    assert response.status_code == 200


def test_Login_RD():
    url = URL + "/auth/login"
    login_data = {
        "email": "Test_RD@fastwise.net",
        "password": "test"
    }
    response = client.post(url, json=login_data)
    print(response.json())
    with open(path + 'Default/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)
    assert response.status_code == 200


# 註冊五支真實蘑菇
def test_create_5_fasteyes_device():
    for i in range(2):
        test_Login_RD()

        url = URL + "/fasteyes_uuid"
        para = {
            "creator": "Test",
            "product_number": "000" + str(i + 1)
        }
        device_response = client.post(url, json=para, headers=get_current_user_header())
        print(device_response.json())
        assert device_response.status_code == 200

        url = URL + "/fasteyes_uuid"
        device_uuid = device_response.json()["uuid"]
        with open(os.getcwd() + "/Auto/Default/UUID_data/hardwareuuid.json", "r") as file_data:
            hardware_uuid = json.load(file_data)
        uuid_data = {
            "hardware_uuid": hardware_uuid["uuid_" + str(i + 1)],
            "device_uuid": str(device_uuid)
        }
        device_response = client.patch(url, json=uuid_data, headers=get_current_user_header())
        print(device_response.json())
        assert device_response.status_code == 200

        test_Login_admin()

        url = URL + "/fasteyes_device"
        device_uuid = device_response.json()["uuid"]
        device_data = {
            "name": "裝置" + str(i + 1),
            "description": "裝置描述",
            "device_uuid": device_uuid
        }

        response = client.post(url, json=device_data, headers=get_current_user_header())
        print(device_response.json())
        assert response.status_code == 200


##########################################(11/30 - 1)#################################################


def test_Login_admin():
    url = URL + "/auth/login"
    login_data = {
        "email": "ricky@fastwise.net",
        "password": "ricky"
    }
    response = client.post(url, json=login_data)
    with open(path + 'Default/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)
    assert response.status_code == 200


def test_invite_HR_user():
    url = URL + "/users/invite"
    HR_data = {
        "email": "ricky400430012@gmail.com",
        "level": 3
    }
    response = client.post(url, json=HR_data, headers=get_current_user_header())
    assert response.status_code == 200


def test_create_HR_user():
    with open(os.getcwd() + '/Auto/Default/User_data/invite_token.txt', 'r', encoding="utf-8") as token_data:
        token = token_data.read()
    url = URL + "/users/create/" + str(token)
    HR_data = get_user_data("HR")
    response = client.post(url, json=HR_data, headers=get_current_user_header())
    print(response.json())
    assert response.status_code == 200


def test_invite_noarmal_user():
    url = URL + "/users/invite"
    HR_data = {
        "email": "Test_normal_user@fastwise.net",
        "level": 4
    }
    response = client.post(url, json=HR_data, headers=get_current_user_header())
    assert response.status_code == 200


def test_create_normal_user():
    with open(os.getcwd() + '/Auto/Default/User_data/invite_token.txt', 'r', encoding="utf-8") as token_data:
        token = token_data.read()
    url = URL + "/users/create/" + str(token)
    HR_data = get_user_data("normal_user")
    response = client.post(url, json=HR_data, headers=get_current_user_header())
    assert response.status_code == 200


##########################################(11/30 - 2)#################################################
def test_create_department():
    url = URL + "/department"
    job = ["manager", "Human_Resources", "General_Affairs", "Sales", "International"]
    for i in job:
        department_data = {
            "name": i
        }
        response = client.post(url, json=department_data, headers=get_current_user_header())
        assert response.status_code == 200


def test_create_staff():
    for i in ["Unknow", "Dave", "Ricky"]:
        url = URL + "/staffs"
        with open(path + 'Default/staff_data/staff.json', encoding='utf-8') as json_file:
            staff_data = json.load(json_file)
        response = client.post(url, json=staff_data[i], headers=get_current_user_header())
        assert response.status_code == 200


def test_create_N_staff():
    url = URL + "/staffs"
    for i in range(staff):
        with open(os.getcwd() + '/Auto/Default/staff_data/random_staff.json') as json_file:
            info_data = json.load(json_file)
        info_data = faker.generate_fake(info_data)
        staff_data = {
            "department_id": str(random.randrange(1, 6)),
            "serial_number": i + 3,
            "info": info_data,
            "start_date": str(datetime.datetime.now()),
            "status": str(random.randrange(0, 3))
        }
        response = client.post(url, json=staff_data, headers=get_current_user_header())
        assert response.status_code == 200


def test_Staff2FaceImages():
    url = URL + "/staffs/2/faces"
    files = {'Image_file': open(path + 'Default/staff_data/Dave_img.jpg', 'rb')}
    response = client.post(url, files=files, headers=get_current_user_header())
    assert response.status_code == 200


def test_Staff2FaceFeature():
    url = URL + "/staffs/2/raw_face_features"
    with open(path + 'Default/staff_data/Dave_face_feature.txt', 'rb') as feature:
        raw_face_feature = feature.read()
    face_data = {
        "feature": raw_face_feature
    }
    response = client.post(url, params=face_data, headers=get_current_user_header())
    assert response.status_code == 200


def test_Staff3FaceImages():
    url = URL + "/staffs/3/faces"
    files = {'Image_file': open(path + 'Default/staff_data/Ricky_img.jpg', 'rb')}
    response = client.post(url, files=files, headers=get_current_user_header())
    assert response.status_code == 200


def test_Staff3FaceFeature():
    url = URL + "/staffs/3/raw_face_features"
    with open(path + 'Default/staff_data/Ricky_face_feature.txt', 'rb') as feature:
        raw_face_feature = feature.read()
    face_data = {
        "feature": raw_face_feature
    }
    response = client.post(url, params=face_data, headers=get_current_user_header())
    assert response.status_code == 200

# ##########################################(11/30 - 2)#################################################
#
#
# # def test_create_TH_device():
# #     area_list = ["room", "outside", "toilet", "school"]
# #     name_list = ["1F半品", "3F組裝", "1F半品", "RF", "5F中區", "5F電子", "4F燒機", "5FMIS", "大廳", "B1電測", "B2停車場", "陽台"]
# #     url = URL + "/devices/device_model/1"
# #     for i in range(1, 9):
# #         data = {
# #             "name": random.choice(name_list),
# #             "serial_number": random.randrange(100000, 999999),
# #             "area": random.choice(area_list),
# #             "info": {
# #                 "interval_time": "10",
# #                 "alarm_temperature_upper_limit": random.randrange(70, 100),
# #                 "alarm_temperature_lower_limit": random.randrange(0, 30),
# #                 "alarm_humidity_upper_limit": random.randrange(70, 100),
# #                 "alarm_humidity_lower_limit": random.randrange(0, 30),
# #                 "battery_alarm": random.randrange(10, 100)
# #             }
# #         }
# #         response = client.post(url, json=data, headers=get_current_user_header())
# #         assert response.status_code == 200
#
#
# # def test_create_TH_device():
# #     area_list = ["機房", "大廳", "電測區", "成品區"]
# #     name_list = ["冷凍", "零食", "冷藏", "Ricky", "黑盒子", "Frank", "Dave", "機房"]
# #     serial_number_list = ["170434", "1705EF", "170681", "170438", "170432", "170414", "170436", "170431"]
# #     url = URL + "/devices/device_model/1"
# #     for name, serial_number in zip(name_list, serial_number_list):
# #         data = {
# #             "name": name,
# #             "serial_number": serial_number,
# #             "area": random.choice(area_list),
# #             "info": {
# #                 "interval_time": "10",
# #                 "alarm_temperature_upper_limit": random.randrange(70, 100),
# #                 "alarm_temperature_lower_limit": random.randrange(0, 30),
# #                 "alarm_humidity_upper_limit": random.randrange(70, 100),
# #                 "alarm_humidity_lower_limit": random.randrange(0, 30),
# #                 "battery_alarm": random.randrange(10, 100)
# #             }
# #         }
# #         response = client.post(url, json=data, headers=get_current_user_header())
# #         assert response.status_code == 200
#
# #
# # def test_create_Ipcam_device_defult():
# #     area_list = ["機房", "大廳", "電測區", "成品區"]
# #     url = URL + "/devices/device_model/2"
# #     for i in range(0, 1):
# #         data = {
# #             "name": "IP_cam" + str(i),
# #             "serial_number": random.randrange(100000, 999999),
# #             "area": random.choice(area_list),
# #             "info": {
# #                 "stream_name": "live1s1.sdp",
# #                 "ip": "192.168.45.64",
# #                 "port": "554",
# #                 "username": "root",
# #                 "password": "a1234567"
# #             }
# #         }
# #         response = client.post(url, json=data, headers=get_current_user_header())
# #         assert response.status_code == 200
# #
# #
# # def test_create_Ipcam_device_defult2():
# #     area_list = ["機房", "大廳", "電測區", "成品區"]
# #     url = URL + "/devices/device_model/2"
# #     data = {"name": "IP_cam2",
# #             "serial_number": random.randrange(100000, 999999),
# #             "area": random.choice(area_list),
# #             "info": {
# #                 "stream_name": "Sms=1.unicast",
# #                 "ip": "192.168.45.211",
# #                 "port": "554",
# #                 "username": "syno",
# #                 "password": "75d676b1ee75a1528641c5327483459d"
# #             }
# #             }
# #     response = client.post(url, json=data, headers=get_current_user_header())
# #     assert response.status_code == 200
# #
# #
# # def test_create_Ipcam_device_defult3():
# #     area_list = ["機房", "大廳", "電測區", "成品區"]
# #     url = URL + "/devices/device_model/2"
# #     data = {"name": "IP_cam3",
# #             "serial_number": random.randrange(100000, 999999),
# #             "area": random.choice(area_list),
# #             "info": {
# #                 "stream_name": "Sms=2.unicast",
# #                 "ip": "192.168.45.211",
# #                 "port": "554",
# #                 "username": "syno",
# #                 "password": "8b34e64788900e8bec13a206c6ab6df5"
# #             }
# #             }
# #     response = client.post(url, json=data, headers=get_current_user_header())
# #     assert response.status_code == 200
#
#
# ##########################################(11/30 - 3)#################################################
# def test_create_fasteyes_observation():
#     url = URL + "/fasteyes_devices/1/observation"
#     now = datetime.datetime.now()
#     # 幾天上下班
#     for few_day_ago in range(work_day, 0, -1):
#         few_days_ago = str(datetime.datetime.date(now) + datetime.timedelta(days=-few_day_ago))
#         # 休息幾次
#         for i in range(1, 5):
#             staff_id = list(range(2, staff + 3))
#             # 總共幾人
#             for j in range(1, staff + 2):
#                 # 上下班時間
#                 random_sec = str(random.randrange(1, 59))
#                 start_work_on_time = few_days_ago + " 08:" + str(random.randrange(30, 59)) + ":" + random_sec
#                 start_work_delay = few_days_ago + " 09:" + str(random.randrange(1, 30)) + ":" + random_sec
#                 start_work_time = [start_work_on_time] * 10 + [start_work_delay]
#                 take_rest_time = few_days_ago + " " + str(random.randrange(10, 17)) + ":" + str(
#                     random.randrange(1, 59)) + ":" + random_sec
#                 get_off = few_days_ago + " 17:" + str(random.randrange(1, 30)) + ":" + str(random.randrange(1, 59))
#                 if i == 1:
#                     commuter_time = random.choice(start_work_time)
#                 elif i == 4:
#                     commuter_time = get_off
#                 else:
#                     commuter_time = take_rest_time
#                 random_staff_id = random.choice(staff_id)
#                 data = {
#                     "phenomenon_time": commuter_time,
#                     "result": False,
#                     "image_name": "image_name" + str(random_staff_id),
#                     "staff_id": random_staff_id,
#                     "info": {
#                         "wear_mask": random.randint(0, 1),
#                         "temperature": round(random.uniform(35.7, 38), 1),
#                         "threshold_temperature": 37.5,
#                         "compensate_temperature": 0,
#                     }
#
#                 }
#                 staff_id.remove(random_staff_id)
#                 response = client.post(url, json=data, headers=get_current_user_header())
#                 assert response.status_code == 200
#
# ##########################################(11/30 - 3)#################################################
#
#
# # def test_upload_TH_Observation():
# #     for i in range(20):
# #         for j in range(1, 9):
# #             url = URL + "/devices/" + str(j) + "/observation"
# #             temperature = round(random.uniform(0, 100), 1)
# #             humidity = round(random.uniform(0, 100), 1)
# #             if temperature >= 70 or temperature <= 30:
# #                 alarm_temperature = False
# #             else:
# #                 alarm_temperature = True
# #
# #             if humidity >= 77 or humidity <= 20:
# #                 alarm_humidity = False
# #             else:
# #                 alarm_humidity = True
# #
# #             data = {
# #                 "temperature": temperature,
# #                 "humidity": humidity,
# #                 "index": 432,
# #                 "alarm_temperature": alarm_temperature,
# #                 "alarm_humidity": alarm_humidity,
# #                 "battery": random.randrange(1, 101),
# #                 "status": 0
# #             }
# #             response = client.post(url, json=data, headers=get_current_user_header())
# #             print(response.json())
# #             assert response.status_code == 200
# #
#
# # def test_upload_TH_Observation():
# #     for i in range(20):
# #         url = URL + "/devices/device_model/1"
# #         response = client.get(url, headers=get_current_user_header())
# #         for device in response.json():
# #             id = device["id"]
# #             alarm_temperature_upper_limit = device["info"]["alarm_temperature_upper_limit"]
# #             alarm_temperature_lower_limit = device["info"]["alarm_temperature_lower_limit"]
# #             alarm_humidity_upper_limit = device["info"]["alarm_humidity_upper_limit"]
# #             alarm_humidity_lower_limit = device["info"]["alarm_humidity_lower_limit"]
# #
# #             temperature = random.randrange(0, 100)
# #             humidity = random.randrange(0, 100)
# #
# #             if temperature >= alarm_temperature_upper_limit or temperature <= alarm_temperature_lower_limit:
# #                 alarm_temperature = True
# #             else:
# #                 alarm_temperature = False
# #
# #             if humidity >= alarm_humidity_upper_limit or humidity <= alarm_humidity_lower_limit:
# #                 alarm_humidity = True
# #             else:
# #                 alarm_humidity = False
# #
# #             data = {
# #                 "temperature": temperature,
# #                 "humidity": humidity,
# #                 "index": 432,
# #                 "alarm_temperature": alarm_temperature,
# #                 "alarm_humidity": alarm_humidity,
# #                 "battery": random.randrange(1, 101),
# #                 "status": 0
# #             }
# #
# #             url = URL + "/devices/" + str(id) + "/observation"
# #             response = client.post(url, json=data, headers=get_current_user_header())
# #             print(response.json())
# #             assert response.status_code == 200
#
# ###############################################
# # def test_default():
# #     clear_all_data_no_auth()
# #     add_RD()
# #     add_AdminUser()
# #     Login_RD()
# #     create_Fasteyes_UUID()
# #     refresh_1_Fasteyes_device()
# #     regist_device()
# #     create_device_model()
# #     Login_admin()
# #     create_device()
# #     invite_HR_user()
# #     create_HR_user()
# #     invite_noarmal_user()
# #     create_normal_user()
# #     create_department()
# #     create_staff()
# #     create_20_staff()
# #     StaffFaceImages()
# #     StaffFaceFeature()
# #     create_fasteyes_observation()
# #     upload_Observation()
#
#
# #########################################################
