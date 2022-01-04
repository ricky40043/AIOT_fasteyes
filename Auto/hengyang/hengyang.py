import datetime
import json, random
from Auto import *
from app.db.database import SessionLocal
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.models.domain.staff import staff

sessionlocal = SessionLocal()


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


def test_add_AdminUser():
    url = URL + "/users/admin"
    adminusers_data = get_user_data("Admin")
    adminusers_data["email"] = "sumi@conductor.com.tw"
    adminusers_data["password"] = "Conductor@1030"
    adminusers_data["name"] = "Hung Yang"
    response = client.post(url, json=adminusers_data)
    assert response.status_code == 200


def test_Login_RD():
    url = URL + "/auth/login"
    login_data = {
        "email": "Test_RD@fastwise.net",
        "password": "test"
    }
    response = client.post(url, json=login_data)
    with open(path + 'Default/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)
    assert response.status_code == 200


def test_Login_admin():
    url = URL + "/auth/login"
    login_data = {
        "email": "sumi@conductor.com.tw",
        "password": "Conductor@1030"
    }
    response = client.post(url, json=login_data)
    with open(path + 'Default/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)
    assert response.status_code == 200


def test_create_department():
    url = URL + "/department"
    global job
    job = ["測試", "離職", "SMT", "品保", "資材", "DIP", "組裝", "管理", "包裝", "博赫香", "工程", "製造"]
    for i in job:
        department_data = {
            "name": i
        }
        response = client.post(url, json=department_data, headers=get_current_user_header())
        assert response.status_code == 200


def test_create_staff():
    url = URL + "/staffs"
    global serial_number_list, staff_name_list, file_name_list, \
        gender_list, department_id_list, status_list, start_date_list
    serial_number_list = []
    staff_name_list = []
    file_name_list = []
    gender_list = []
    department_id_list = []
    status_list = []
    start_date_list = []

    with open(os.getcwd() + "/Auto/hengyang/hengyang_staff_info.txt", "r", encoding="utf-8") as file:
        file_data = file.read()
        staff_info = eval(file_data)
    # 整理舊資料
    for info in staff_info:
        serial_number_list.append(info["SerialNumber"])
        staff_name_list.append(info["Name"])
        file_name_list.append(str(info["Id"]) + "_EMP_" + str(info["SerialNumber"]))
        department_id_list.append(int(job.index(info["Department"]) + 1))
        start_date_list.append(info["CreatedAt"])
        if info["Gender"] == "女" or info["Gender"] =="Female":
            gender_list.append(2)
        else:
            gender_list.append(1)
        if info["Status"] == "在職中":
            status_list.append(1)
        elif info["Status"] == "離職":
            status_list.append(3)
        else:
            status_list.append(2)
    # 填入新資料
    for department_id, serial_number, staff_name, gender, start_date, status in zip(
            department_id_list, serial_number_list, staff_name_list, gender_list, start_date_list, status_list):
        staff_data = {
            "department_id": department_id,
            "serial_number": serial_number,
            "info": {
                "name": staff_name,
                "card_number": "00000000",
                "email": "hengyang_staff@fastwise.net",
                "gender": gender,
                "national_id_number": "00000000",
                "birthday": "0750101",
                "telephone_number": "0912345678"
            },
            "start_date": start_date,
            "status": status
        }
        response = client.post(url, json=staff_data, headers=get_current_user_header())
        print(response.json())
        assert response.status_code == 200

    # for department_id, serial_number, staff_name, gender, start_date, status, k in zip(
    #                 department_id_list, serial_number_list, staff_name_list, gender_list, start_date_list, status_list, range(1, 170)):
    #     data = staff(
    #     department_id = department_id,
    #     group_id = 2,
    #     status = status,
    #     serial_number = serial_number,
    #     start_date = start_date,
    #     end_date = start_date,
    #     created_at = start_date,
    #     updated_at = start_date,
    #     info ={})

    # data = staff(department_id = 2,
    # group_id = 2,
    # status = 1,
    # serial_number = 111,
    # start_date = datetime.datetime.now(),
    # # end_date = start_date,
    # # created_at = start_date,
    # # updated_at = start_date,
    # info ={"":""})
    #
    # sessionlocal.add(data)
    # sessionlocal.commit()


def test_StaffFaceImages():
    for i, file_name, name in zip(range(1, len(file_name_list) + 1), file_name_list, staff_name_list):
        url = URL + "/staffs/" + str(i) + "/faces"
        face_path = os.getcwd() + "/Auto/hengyang/hengyang_staff/" + str(file_name) + "/" + str(name) + ".jpg"
        files = {'Image_file': open(face_path, 'rb')}
        response = client.post(url, files=files, headers=get_current_user_header())
        print(response.json())
        assert response.status_code == 200


def test_StaffFaceFeature():
    for i, basename in zip(range(1, len(file_name_list) + 1), file_name_list):
        url = URL + "/staffs/" + str(i) + "/raw_face_features"
        feature_path = os.getcwd() + "/Auto/hengyang/hengyang_staff/" + str(basename) + "/" + "feature.txt"
        with open(feature_path, 'rb') as feature:
            raw_face_feature = feature.read()
        face_data = {
            "feature": raw_face_feature
        }
        response = client.post(url, params=face_data, headers=get_current_user_header())
        print(response.json())

        assert response.status_code == 200


def test_create_3_fasteyes_device():
    for i in range(3):
        test_Login_RD()

        url = URL + "/fasteyes_uuid"
        para = {
            "creator": "Test",
            "product_number": "000" + str(i + 1)
        }
        device_response = client.post(url, json=para, headers=get_current_user_header())
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
        assert device_response.status_code == 200

        test_Login_admin()

        url = URL + "/fasteyes_device"
        device_uuid = device_response.json()["uuid"]
        device_data = {
            "name": "Test_" + str(i + 1),
            "description": "string",
            "device_uuid": device_uuid
        }

        response = client.post(url, json=device_data, headers=get_current_user_header())
        assert response.status_code == 200


def test_create_fasteyes_observation():
    url = URL + "/fasteyes_devices/1/observation"
    with open(os.getcwd() + "/Auto/hengyang/test.txt", "r", encoding="utf-8") as file:
        file_data = file.read()
    all_observation = eval(file_data)
    observartion = []
    for i in all_observation:
        if "Parameters" in i:
            if i["Result"] not in serial_number_list:
                if i["PhenomenonTime"] not in observartion:
                    observartion.append(i)
    for j in observartion:
        result = sessionlocal.query(staff.id).filter(staff.serial_number == j["Result"]).first()
        result = str(result).replace("(", "")
        result = str(result).replace(",", "")
        result = str(result).replace(")", "")
        staff_id = result

        data = {
            "phenomenon_time": j["PhenomenonTime"],
            "result": False,
            "image_name": "",
            "staff_id": staff_id,
            "info": {
                "wear_mask": 1,
                "temperature": round(random.uniform(35.7, 36.5), 1),
                "threshold_temperature": 37.5,
                "compensate_temperature": 0,
            }

        }
        response = client.post(url, json=data, headers=get_current_user_header())
        print(response.json())
        assert response.status_code == 200
