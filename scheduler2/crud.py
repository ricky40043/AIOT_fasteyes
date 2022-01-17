import random
from app.models.domain.device import device
from app.db.database import SessionLocal
from app.models.domain.group import group
from app.server.observation.crud import Create_temperature_humidity_Observation


class DictList(dict):
    def __setitem__(self, key, value):
        try:
            # Assumes there is a list on the key
            self[key].append(value)
        except KeyError: # If it fails, because there is no key
            super(DictList, self).__setitem__(key, value)
        except AttributeError: # If it fails because it is not a list
            super(DictList, self).__setitem__(key, [self[key], value])


all_data_dict = DictList()
session = SessionLocal()



def decode(data):
    """解碼"""
    data_to_int_list = list(bytes(data))
    # print(data_to_int_list)
    byte_lst = [(bytes([data_to_int])).decode("utf-8", "replace") for data_to_int in data_to_int_list]
    # 取得資料
    try:
        serial_number = "".join(byte_lst[3:16]).lstrip("0")
        Temperature_TH = data_to_int_list[16]
        Temperature_TL = data_to_int_list[17]
        Humidity_TH = data_to_int_list[18]
        Humidity_TL = data_to_int_list[19]
        Time = data_to_int_list[20] * 16 + data_to_int_list[21]
        Index = data_to_int_list[22] * 16 + data_to_int_list[23]
        Status = data_to_int_list[24]
        Battery = data_to_int_list[25]
        # print("tempera ture_humidity device ID:", serial_number + " Get data")

        # 將TH及TL轉成溫、濕度
        if Temperature_TH != 128:
            Temperature = (int(format(Temperature_TH, "b") + "00000000", 2) + Temperature_TL) / 10
        else:
            Temperature = (-1) * Temperature_TL / 10

        if Humidity_TH != 128:
            Humidity = (int(format(Humidity_TH, "b") + "00000000", 2) + Humidity_TL) / 10
        else:
            Humidity = "error"

        all_data_dict[serial_number] = {"temperature": Temperature, "humidity": Humidity, "time": Time, "index": Index, "battery": Battery, "status": Status}
        # print(all_data_dict)
    except Exception as e:
        print("解碼錯誤")
        print(data_to_int_list)


def sendemail():
    pass


def activity():
    """將group內的所有device取出，並進行比對"""
    group_list = session.query(group).all()
    for each_group in group_list:
        group_index = each_group.id
        all_device_in_group = session.query(device).filter(device.group_id == group_index).all()
        all_serial_number_in_group = [each_device.serial_number for each_device in all_device_in_group]

        for each_serial_num in all_serial_number_in_group:
            device_db = session.query(device).filter(device.serial_number == each_serial_num).first()

            # 補償溫、濕度
            compensate_temperature = device_db.info["compensate_temperature"]
            compensate_humidity = device_db.info["compensate_humidity"]

            # 從DB取得device的溫、濕度極限值
            alarm_temperature_upper_limit = device_db.info["alarm_temperature_upper_limit"]
            alarm_temperature_lower_limit = device_db.info["alarm_temperature_lower_limit"]
            alarm_humidity_upper_limit = device_db.info["alarm_humidity_upper_limit"]
            alarm_humidity_lower_limit = device_db.info["alarm_humidity_lower_limit"]

            name = device_db.name
            area = device_db.area
            #判斷此device是否在此次結果
            if each_serial_num in all_data_dict:
                #隨機拿取此device的一個結果
                #觀測結果數量 =1 為dict，>1 為list
                if isinstance(all_data_dict[each_serial_num], list) :
                    pick_one = random.choice(all_data_dict[each_serial_num])
                else:
                    pick_one = all_data_dict[each_serial_num]
                print(pick_one)
                temperature = pick_one["temperature"]
                humidity = pick_one["humidity"]
                time = pick_one["time"]
                index = pick_one["index"]
                battery = pick_one["battery"]
                status = pick_one["status"]

                # 補償後溫、濕度
                temperature = temperature + compensate_temperature
                humidity = humidity + compensate_humidity

                # 判斷alarm
                if temperature >= alarm_temperature_upper_limit or temperature <= alarm_temperature_lower_limit:
                    alarm_temperature = True
                else:
                    alarm_temperature = False

                if humidity >= alarm_humidity_upper_limit or humidity <= alarm_humidity_lower_limit:
                    alarm_humidity = True
                else:
                    alarm_humidity = False

                #寄信判斷
                if battery < device_db.info["battery_alarm"]:
                    sendemail()
                    print("已寄送電池異常email")
                    pass
                if status == 1:
                    sendemail()
                    print("已寄送溫濕度感應器狀態異常email")
                    pass
                if alarm_humidity:
                    sendemail()
                    print("已寄送濕度異常email")
                    pass
                if not alarm_temperature:
                    pass
                else:
                    sendemail()
                    print("已寄送溫度異常email")
                    pass

                observation_in = {"temperature": temperature, "humidity": humidity, "index": index,
                                  "alarm_temperature" : alarm_temperature, "alarm_humidity": alarm_humidity,
                                  "battery": battery, "status": status,
                                  "compensate_temperature" : compensate_temperature, "compensate_humidity" : compensate_humidity,
                                  "name":name, "area":area, "serial_number": each_serial_num}
                print(observation_in)
                Create_temperature_humidity_Observation(observation_in=observation_in, group_id=group_index, device_id=device_db.id)
            else:
                sendemail()
                print("已寄送裝置：", each_serial_num, "資料遺失結果")
                observation_in = {"temperature": -255, "humidity" : -255, "index" : -1,
                                  "alarm_temperature": True, "alarm_humidity": True,
                                  "battery": -1, "status": 2,
                                  "compensate_temperature" : 0, "compensate_humidity" : 0,
                                  "name": name, "area": area, "serial_number": each_serial_num}
                Create_temperature_humidity_Observation(observation_in=observation_in, group_id=group_index, device_id=device_db.id)
    #     send_email(email=current_user.email, device_name=device_db.name, serial_number=device_db.serial_number,
    #                area=device_db.area, id=observation_db.id,
    #                temperature=observation_db.info["temperature"],
    #                temp_lower_limit=device_db.info["alarm_temperature_lower_limit"],
    #                temp_upper_limit=device_db.info["alarm_temperature_upper_limit"],
    #                humidity=observation_db.info["humidity"],
    #                hum_lower_limit=device_db.info["alarm_humidity_lower_limit"],
    #                hum_upper_limit=device_db.info["alarm_humidity_upper_limit"],
    #                battery=observation_db.info["battery"])
    all_data_dict.clear()
