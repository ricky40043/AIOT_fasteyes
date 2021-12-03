import asyncio
from typing import Dict, Tuple

from app.models.schemas.temperature_humidity_observation import temperature_humidity_ObservationPostModel
from app.server.observation.crud import Create_temperature_humidity_Observation
from app.server.temperature_humidity_device.crud import create_temperature_humidity_devices, \
    get_temperature_humidity_devices_by_serial_number


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
        # print("temperature_humidity device ID:", name + " Get data")

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
        Create_temperature_humidity_Observation(observation_in, device_db.group_id, device_db.id)
