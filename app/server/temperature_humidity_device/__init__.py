import asyncio
from datetime import datetime, timedelta
from typing import Dict, Tuple

from app.core.config import HOST_NAME
from app.db.database import get_db
from app.server.device.crud import get_device_by_group_id_and_device_model_id
from app.server.device_model import DeviceType
from app.server.group.crud import get_All_groups
from app.server.observation.crud import Create_temperature_humidity_Observation, \
    get_Observations_by_group_and_device_model_id_and_timespan
from app.server.send_email import send_email_device_alert, send_email_async, conf
from app.server.temperature_humidity_device.crud import create_temperature_humidity_devices, \
    get_temperature_humidity_devices_by_serial_number

from starlette.background import BackgroundTasks

from app.server.user.crud import get_user_by_id, get_user_by_id_no_db

alarm_data_list = []


# data_list = []


class MyUDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        # print("讀取原始資料:", data)
        data_to_int_list = list(bytes(data))
        data_to_hex_list = [hex(number) for number in data_to_int_list]
        byte_lst = [(bytes([data_to_int])).decode("utf-8", "replace") for data_to_int in data_to_int_list]
        Barcode = "".join(byte_lst[3:16])
        # bin16_symbol = (bin(data_to_int_list[16]))[2]
        # bin16_number = (bin(data_to_int_list[16]))[3:]
        # if bin16_number:
        #     if bin16_symbol == 1:
        #         Heigh_part_number = int(bin16_number, 2) * 16
        #     else:
        #         Heigh_part_number = - int(bin16_number, 2) * 16
        # else:
        #     Heigh_part_number = 0
        # Low_part_number = data_to_int_list[17]
        # THTL = (Heigh_part_number + Low_part_number) / 10.0
        #
        # bin18_symbol = (bin(data_to_int_list[18]))[2]
        # bin18_number = (bin(data_to_int_list[18]))[3:]
        # if bin18_number:
        #     if bin18_symbol == 1:
        #         Heigh_part_number = int(bin18_number, 2) * 16
        #     else:
        #         Heigh_part_number = - int(bin18_number, 2) * 16
        # else:
        #     Heigh_part_number = 0
        # Low_part_number = data_to_int_list[19]
        # HHTL = (Heigh_part_number + Low_part_number) / 10.0
        Time = data_to_int_list[20] * 16 + data_to_int_list[21]
        Index = data_to_int_list[22] * 16 + data_to_int_list[23]
        Status = data_to_int_list[24]
        Battery = data_to_int_list[25]

        # 取得Data
        Temperature_TH = data_to_int_list[16]
        Temperature_TL = data_to_int_list[17]
        Humidity_TH = data_to_int_list[18]
        Humidity_TL = data_to_int_list[19]

        # 解碼
        if Temperature_TH != 128:
            Temperature = (int(format(Temperature_TH, "b") + "00000000", 2) + Temperature_TL) / 10
        else:
            Temperature = (-1) * Temperature_TL / 10

        if Humidity_TH != 128:
            Humidity = (int(format(Humidity_TH, "b") + "00000000", 2) + Humidity_TL) / 10
        else:
            Humidity = "error"

        # print("Barcode:", Barcode)
        # print("THTL:", Temperature)
        # print("HHTL:", Humidity)
        # print("Time:", Time)
        # print("Index:", Index)
        # print("Status:", Status)
        # print("Battery:", Battery)
        name = Barcode.lstrip("0")
        print("tempera ture_humidity device ID:", name + " Get data")

        # 資料存入
        device_db = get_temperature_humidity_devices_by_serial_number(name)

        if not device_db:
            return name + "不存在"

        alarm_temperature_upper_limit = device_db.info["alarm_temperature_upper_limit"]
        alarm_temperature_lower_limit = device_db.info["alarm_temperature_lower_limit"]
        alarm_humidity_upper_limit = device_db.info["alarm_humidity_upper_limit"]
        alarm_humidity_lower_limit = device_db.info["alarm_humidity_lower_limit"]

        # 判斷alarm
        if Temperature >= alarm_temperature_upper_limit or Temperature <= alarm_temperature_lower_limit:
            alarm_temperature = True
        else:
            alarm_temperature = False

        if Humidity == "error":
            pass
        elif Humidity >= alarm_humidity_upper_limit or Humidity <= alarm_humidity_lower_limit:
            alarm_humidity = True
        else:
            alarm_humidity = False

        observation_in = {"temperature": Temperature, "humidity": Humidity, "index": Index,
                          "alarm_temperature": alarm_temperature, "alarm_humidity": alarm_humidity,
                          "battery": Battery, "status": Status}
        observation_db = Create_temperature_humidity_Observation(observation_in, device_db.group_id, device_db.id)

        current_user = get_user_by_id_no_db(device_db.user_id)

        if current_user.info["device_email_alert"] and (alarm_temperature or alarm_humidity or Battery<90):  # 寄信
            data = {
                "email": current_user.email,
                "title": "溫濕度裝置異常",
                "template": f"""
                               <html>
                                   <body>
                                         <h1>
                                            裝置名稱: {device_db.name}
                                         </h1>
                                         <h2>
                                            裝置編號: {device_db.serial_number}
                                         </h2>
                                         <h2>
                                            裝置位置: {device_db.area}
                                         </h2>
                                         <h2>
                                            觀測結果ID: {observation_db.id}
                                         </h2>
                                         <h2>
                                            溫度:{observation_db.info["temperature"]}
                                         </h2>
                                         <h4>
                                            溫度正常範圍: 
                                            {device_db.info["alarm_temperature_lower_limit"]}°C～
                                            {device_db.info["alarm_temperature_upper_limit"]}°C
                                         </h4>
                                         <h2>
                                            濕度:{observation_db.info["humidity"]}
                                         </h2>
                                         <h4>
                                            濕度正常範圍: 
                                            {device_db.info["alarm_humidity_lower_limit"]}％～
                                            {device_db.info["alarm_humidity_upper_limit"]}％
                                         </h4>
                                         <h2>
                                            電池電量:{observation_db.info["battery"]}
                                         </h2>
                                   </body>
                               </html>
                           """
            }
            alarm_data_list.append(data)
            # print(str(observation_in["index"]) + "in")
            # print(background_tasks.tasks)
            # send_email_device_alert(background_tasks=background_tasks,
            #                         email=current_user.email, observation_db=observation_db, device_db=device_db)
            # print(str(observation_in["index"]) + "out")
            # print(background_tasks.tasks)

        # data_list.append(observation_db)


import time
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib


def createSendMailTimer():
    t = threading.Timer(60, repeat)
    t.start()


def repeat():
    # Time = 'Now:', time.strftime('%H:%M:%S', time.localtime())
    # print(Time)
    for idx, each_data in enumerate(alarm_data_list):
        with smtplib.SMTP(host=conf.MAIL_SERVER, port=conf.MAIL_PORT) as smtp:  # 設定SMTP伺服器
            try:
                smtp.ehlo()  # 驗證SMTP伺服器
                smtp.starttls()  # 建立加密傳輸
                smtp.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)  # 登入寄件者gmail
                content = MIMEMultipart()  # 建立MIMEMultipart物件
                content["subject"] = each_data["title"]  # 郵件標題
                content["from"] = conf.MAIL_USERNAME  # 寄件者
                content["to"] = each_data["email"]  # 收件者
                content.attach(MIMEText(each_data["template"], 'html'))  # 郵件純文字內容
                smtp.send_message(content)  # 寄送郵件
                print(str(idx) + "Send Alarm Mail Complete!")
                print("alarm_data_list count:"+str(len(alarm_data_list)))
                alarm_data_list.remove(each_data)
            except Exception as e:
                print("Error message: ", e)
    # 取得所有 group
    db = next(get_db())
    group_db_list = get_All_groups(db)

    for group_db in group_db_list:
        # 取得group 內所有裝置
        device_db_list = get_device_by_group_id_and_device_model_id(db, group_db.id,
                                                                    DeviceType.temperature_humidity.value)
        if len(device_db_list) > 0:
            start_timestamp = datetime.now() - timedelta(minutes=2)
            end_timestamp = datetime.now()
            # 取得時間內所有觀測結果
            data_list = get_Observations_by_group_and_device_model_id_and_timespan(db, group_db.id,
                                                                                   DeviceType.temperature_humidity.value,
                                                                                   -1, start_timestamp, end_timestamp,-1)

            # 整理所有list
            device_list = [device.id for device in device_db_list]
            observation_list = [data.device_id for data in data_list]
            print(device_list)
            print(observation_list)
            current_user = get_user_by_id_no_db(device_db_list[0].user_id)

            if not current_user.info["device_email_alert"]:
                data_list.clear()
                createSendMailTimer()
                return

            message = ""
            send_mail = False
            # 檢查每個裝置是否都有資料
            for idx, each_device_id in enumerate(device_list):
                if each_device_id not in observation_list:
                    message += "裝置名稱:" + device_db_list[idx].name
                    message += "裝置編號:" + device_db_list[idx].serial_number + "\r\n"
                    send_mail = True

            if send_mail:
                with smtplib.SMTP(host=conf.MAIL_SERVER, port=conf.MAIL_PORT) as smtp:  # 設定SMTP伺服器
                    try:
                        smtp.ehlo()  # 驗證SMTP伺服器
                        smtp.starttls()  # 建立加密傳輸
                        smtp.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)  # 登入寄件者gmail
                        content = MIMEMultipart()  # 建立MIMEMultipart物件
                        content["subject"] = "溫濕度裝置資料遺失"  # 郵件標題
                        content["from"] = conf.MAIL_USERNAME  # 寄件者
                        content["to"] = current_user.email  # 收件者
                        content.attach(MIMEText(message))  # 郵件純文字內容
                        smtp.send_message(content)  # 寄送郵件
                        print("Send Observation Miss Mail Complete!")

                    except Exception as e:
                        print("Error message: ", e)
    data_list.clear()

    createSendMailTimer()


createSendMailTimer()
