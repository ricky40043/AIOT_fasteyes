import random
import smtplib

from app.models.domain.area import area
from app.models.domain.area_user import area_user
from app.models.domain.device import device
from app.db.database import SessionLocal
from app.models.domain.group import group
from app.models.domain.user import user
from app.server.observation.crud import Create_temperature_humidity_Observation, Ceate_Nitrogen_Observation
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.server.send_email import conf
import modbus_client as modbus_client
import modbus_tk.modbus_tcp as mt
import modbus_tk.defines as md
import struct


class DictList(dict):
    def __setitem__(self, key, value):
        try:
            # Assumes there is a list on the key
            self[key].append(value)
        except KeyError:  # If it fails, because there is no key
            super(DictList, self).__setitem__(key, value)
        except AttributeError:  # If it fails because it is not a list
            super(DictList, self).__setitem__(key, [self[key], value])


all_data_dict = DictList()
session = SessionLocal()


def activity():
    """將group內的所有device取出，並進行比對"""
    group_list = session.query(group).all()
    for each_group in group_list:
        group_index = each_group.id

        # 溫濕度感應器
        get_temperature_humidity_observaion(group_index)
        # 氮氣機
        get_Nitrogen_observation(group_index)

    all_data_dict.clear()


def temperature_humidity_decode(data):
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

        all_data_dict[serial_number] = {"temperature": Temperature, "humidity": Humidity, "time": Time, "index": Index,
                                        "battery": Battery, "status": Status}
        # print(all_data_dict)
    except Exception as e:
        print("解碼錯誤")
        print(data_to_int_list)


def temperature_humidity_sendemail(device_db, data, title):
    area_name = data.info["area"]
    area_db = session.query(area).filter(area.name == area_name).first()
    if not area_db:
        return
    if not area_db.send_mail:
        print("此區域不用發警報信")
        return
    area_user_db_list = session.query(area_user).filter(area_user.area_id == area_db.id).all()
    area_user_id_list = [item.user_id for item in area_user_db_list]
    user_db_list = session.query(user).filter(user.id.in_(area_user_id_list)).all()
    user_email_list = [each_user.email for each_user in user_db_list]
    if len(user_email_list) == 0:
        print("此區域沒有負責人")
        return
    # 信件內容
    message = f"""
                   <html>
                       <body>
                             <h1>
                                裝置名稱: {data.info["name"]}
                             </h1>
                             <h2>
                                裝置編號: {data.info["serial_number"]}
                             </h2>
                             <h2>
                                裝置位置: {data.info["area"]}
                             </h2>
                             <h2>
                                觀測結果ID: {data.id}
                             </h2>
                             <h2>
                                溫度:{data.info["temperature"]}
                             </h2>
                             <h4>
                                溫度正常範圍:
                                {device_db.info["alarm_temperature_lower_limit"]}°C～
                                {device_db.info["alarm_temperature_upper_limit"]}°C
                             </h4>
                             <h2>
                                濕度:{data.info["humidity"]}
                             </h2>
                             <h4>
                                濕度正常範圍:
                                {device_db.info["alarm_humidity_lower_limit"]}％～
                                {device_db.info["alarm_humidity_upper_limit"]}％
                             </h4>
                             <h2>
                                電池電量:{data.info["battery"]}
                             </h2>
                       </body>
                   </html>
               """
    # 寄信
    with smtplib.SMTP(host=conf.MAIL_SERVER, port=conf.MAIL_PORT) as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)  # 登入寄件者gmail
            content = MIMEMultipart()  # 建立MIMEMultipart物件
            content["subject"] = title  # 郵件標題
            content["from"] = conf.MAIL_USERNAME  # 寄件者
            content["to"] = ','.join(user_email_list)
            content.attach(MIMEText(message, 'html'))  # 郵件純文字內容
            smtp.send_message(content)  # 寄送郵件
            print(device_db.name + title + " Send Observation Mail Complete!")

        except Exception as e:
            print("Error message: ", e)


def get_temperature_humidity_observaion(group_index):
    # 溫濕度感應器
    all_device_in_group = session.query(device).filter(device.group_id == group_index,
                                                       device.device_model_id == 1).all()
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
        # 判斷此device是否在此次結果
        if each_serial_num in all_data_dict:
            # 隨機拿取此device的一個結果
            # 觀測結果數量 =1 為dict，>1 為list
            if isinstance(all_data_dict[each_serial_num], list):
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
            if temperature > alarm_temperature_upper_limit or temperature < alarm_temperature_lower_limit:
                alarm_temperature = True
            else:
                alarm_temperature = False

            if humidity > alarm_humidity_upper_limit or humidity < alarm_humidity_lower_limit:
                alarm_humidity = True
            else:
                alarm_humidity = False

            observation_in = {"temperature": temperature, "humidity": humidity, "index": index,
                              "alarm_temperature": alarm_temperature, "alarm_humidity": alarm_humidity,
                              "battery": battery, "status": status,
                              "compensate_temperature": compensate_temperature,
                              "compensate_humidity": compensate_humidity,
                              "name": name, "area": area, "serial_number": each_serial_num}
            print(observation_in)
            observation_db = Create_temperature_humidity_Observation(observation_in=observation_in,
                                                                     group_id=group_index,
                                                                     device_id=device_db.id)

            # 寄信判斷
            if battery < device_db.info["battery_alarm"]:
                temperature_humidity_sendemail(device_db, observation_db, "電池異常")
                # print(device_db, "已寄送電池異常email")
            elif status == 1:
                temperature_humidity_sendemail(observation_db, "溫濕度感應器狀態異常")
                # print(device_db, "已寄送溫濕度感應器狀態異常email")
            elif alarm_humidity:
                temperature_humidity_sendemail(device_db, observation_db, "溫濕度感應器濕度異常")
                # print("已寄送濕度異常email")
            elif alarm_temperature:
                temperature_humidity_sendemail(device_db, observation_db, "溫濕度感應器濕度異常")
                # print("已寄送溫度異常email")
        else:

            observation_in = {"temperature": -255, "humidity": -255, "index": -1,
                              "alarm_temperature": True, "alarm_humidity": True,
                              "battery": -1, "status": 3,
                              "compensate_temperature": 0, "compensate_humidity": 0,
                              "name": name, "area": area, "serial_number": each_serial_num}
            observation_db = Create_temperature_humidity_Observation(observation_in=observation_in,
                                                                     group_id=group_index,
                                                                     device_id=device_db.id)

            temperature_humidity_sendemail(device_db, observation_db, "溫濕度感應器資料遺失")


def Nitrogen_decode(data_sam):
    data = data_sam
    # status_code_40001
    status_num_int = data[0]
    status_num_bin = bin(status_num_int).split("b")[1]
    # 若小於16位需補零
    while True:
        if len(status_num_bin) < 16:
            status_num_bin = str(0) + status_num_bin
        else:
            break
    status_num_bin_reversed = status_num_bin[len(status_num_bin)::-1]

    # every_status_40001( 16 bit )
    oxygen_height = status_num_bin_reversed[8]
    air_press_low = status_num_bin_reversed[9]
    freeze_drier = status_num_bin_reversed[10]
    air_system = status_num_bin_reversed[11]
    nitrogen_press_height = status_num_bin_reversed[12]
    nitrogen_press_low = status_num_bin_reversed[13]
    run_status = status_num_bin_reversed[14]
    stop_status = status_num_bin_reversed[15]
    standby_status = status_num_bin_reversed[0]
    maintain_status = status_num_bin_reversed[1]
    air_press = ReadFloat((data[5], data[4]))
    nitrogen_flowrate = ReadFloat((data[13], data[21]))
    nitrogen_pressure = ReadFloat((data[15], data[14]))
    oxygen_content = ReadFloat((data[19], data[18]))

    print("oxygen_height:", oxygen_height)
    print("air_press_low:", air_press_low)
    print("freeze_drier:", freeze_drier)
    print("air_system:", air_system)
    print("nitrogen_press_height:", nitrogen_press_height)
    print("nitrogen_press_low:", nitrogen_press_low)
    print("run_status:", run_status)
    print("stop_status:", stop_status)
    print("standby_status:", standby_status)
    print("maintain_status:", maintain_status)
    print("air_press:", air_press)
    print("nitrogen_flowrate:", nitrogen_flowrate)
    print("nitrogen_pressure:", nitrogen_pressure)
    print("oxygen_content:", oxygen_content)

    observation_in = {
        "nitrogen_pressure": nitrogen_pressure,
        "air_press": air_press,
        "nitrogen_flowrate": nitrogen_flowrate,
        "oxygen_content": oxygen_content,
        "oxygen_height": oxygen_height,
        "air_press_low": air_press_low,
        "freeze_drier": freeze_drier,
        "air_system": air_system,
        "nitrogen_press_height": nitrogen_press_height,
        "nitrogen_press_low": nitrogen_press_low,
        "run_status": run_status,
        "stop_status": stop_status,
        "standby_status": standby_status,
        "maintain_status": maintain_status
    }
    return observation_in


def ReadFloat(*args, reverse=False):
    for n, m in args:
        n, m = '%04x' % n, '%04x' % m
    if reverse:
        v = n + m
    else:
        v = m + n
    y_bytes = bytes.fromhex(v)
    y = struct.unpack('!f', y_bytes)[0]
    y = round(y, 6)
    return y


def Nitrogen_sendemail(device_db, data, title):
    area_name = data.info["area"]
    area_db = session.query(area).filter(area.name == area_name).first()
    if not area_db:
        return
    if not area_db.send_mail:
        print("此區域不用發警報信")
        return
    area_user_db_list = session.query(area_user).filter(area_user.area_id == area_db.id).all()
    area_user_id_list = [item.user_id for item in area_user_db_list]
    user_db_list = session.query(user).filter(user.id.in_(area_user_id_list)).all()
    user_email_list = [each_user.email for each_user in user_db_list]
    if len(user_email_list) == 0:
        print("此區域沒有負責人")
        return
    # 信件內容
    message = f"""
                   <html>
                       <body>
                             <h1>
                                裝置名稱: {data.info["name"]}
                             </h1>
                             <h2>
                                裝置編號: {data.info["serial_number"]}
                             </h2>
                             <h2>
                                裝置位置: {data.info["area"]}
                             </h2>
                             <h2>
                                觀測結果ID: {data.id}
                             </h2>
                             <h2>
                                氮氣壓力:{data.info["nitrogen_pressure"]}
                             </h2>
                             <h4>
                                氮氣壓力範圍:
                                {device_db.info["alarm_Oxygen_lower_limit"]}~
                                {device_db.info["alarm_Oxygen_upper_limit"]}
                             </h4>
                             <h2>
                                氧氣壓力:{data.info["air_press"]}
                             </h2>
                             <h4>
                                氧氣壓力範圍:
                                {device_db.info["alarm_Oxygen_lower_limit"]}％～
                                {device_db.info["alarm_Oxygen_upper_limit"]}％
                             </h4>
                             <h2>
                                氮氣流量:{data.info["nitrogen_flowrate"]}
                             </h2>
                             <h4>
                                氮氣流量範圍:
                                {device_db.info["Nitrogen_Flow_lower_limit"]}％～
                                {device_db.info["Nitrogen_Flow_upper_limit"]}％
                             </h4>
                             <h2>
                                氮氣含氧量:{data.info["oxygen_content"]}
                             </h2>
                             <h4>
                                氮氣含氧量範圍:
                                {device_db.info["Nitrogen_content_Oxygen_lower_limit"]}％～
                                {device_db.info["Nitrogen_content_Oxygen_upper_limit"]}％
                             </h4>
                       </body>
                   </html>
               """
    # 寄信
    with smtplib.SMTP(host=conf.MAIL_SERVER, port=conf.MAIL_PORT) as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)  # 登入寄件者gmail
            content = MIMEMultipart()  # 建立MIMEMultipart物件
            content["subject"] = title  # 郵件標題
            content["from"] = conf.MAIL_USERNAME  # 寄件者
            content["to"] = ','.join(user_email_list)
            content.attach(MIMEText(message, 'html'))  # 郵件純文字內容
            smtp.send_message(content)  # 寄送郵件
            print(device_db.name + title + " Send Observation Mail Complete!")

        except Exception as e:
            print("Error message: ", e)


def get_Nitrogen_observation(group_index):
    all_device_in_group = session.query(device).filter(device.group_id == group_index,
                                                       device.device_model_id == 4).all()

    for each_device in all_device_in_group:

        device_ip = each_device.info["ip"]
        device_port = each_device.info["port"]
        master = mt.TcpMaster(device_ip, port=device_port)
        master.set_timeout(5.0)
        try:
            data_sam = master.execute(1, md.READ_HOLDING_REGISTERS, 0, 22)
            # 解碼
            observation_in = Nitrogen_decode(data_sam)
            observation_in["name"] = each_device.name
            observation_in["area"] = each_device.area
            observation_in["serial_number"] = each_device.serial_number
            # 塞資料
            observation_db = Ceate_Nitrogen_Observation(observation_in=observation_in,
                                                        group_id=group_index,
                                                        device_id=each_device.id)
            # 寄信判斷
            if observation_db.info["freeze_drier"]:
                Nitrogen_sendemail(each_device, observation_db, "冷乾機故障")
            elif observation_db.info["air_system"]:
                Nitrogen_sendemail(each_device, observation_db, "空氣系统报警")
            elif observation_db.info["air_press_low"]:
                Nitrogen_sendemail(each_device, observation_db, "空氣壓力異常")
                # print(device_db, "已寄送電池異常email")
            elif observation_db.info["nitrogen_press_height"] or observation_db.info["nitrogen_press_height"]:
                Nitrogen_sendemail(observation_db, "氮氣壓力異常")
                # print(device_db, "已寄送溫濕度感應器狀態異常email")
            elif observation_db.info["oxygen_height"]:
                Nitrogen_sendemail(each_device, observation_db, "氮氣含氧量異常")
                # print("已寄送濕度異常email")

                # print("已寄送溫度異常email")
        except Exception as e:
            print("Error message: ", e)

            # Ricky 不要在這寫程式，這是暫時寫的
            observation_in = {
                "nitrogen_pressure": -1,
                "air_press": -1,
                "nitrogen_flowrate": -1,
                "oxygen_content": -1,
                "oxygen_height": -1,
                "air_press_low": -1,
                "freeze_drier": -1,
                "air_system": -1,
                "nitrogen_press_height": -1,
                "nitrogen_press_low": -1,
                "run_status": -1,
                "stop_status": -1,
                "standby_status": -1,
                "maintain_status": -1
            }
            observation_in["name"] = each_device.name
            observation_in["area"] = each_device.area
            observation_in["serial_number"] = each_device.serial_number
            observation_db = Ceate_Nitrogen_Observation(observation_in=observation_in,
                                                        group_id=group_index,
                                                        device_id=each_device.id)

            Nitrogen_sendemail(each_device, observation_db, "氮氣機資料遺失")



