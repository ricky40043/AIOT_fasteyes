import asyncio
from typing import Dict, Tuple

from app.models.schemas.temperature_humidity_observation import temperature_humidity_ObservationPostModel
from app.server.observation.crud import Create_temperature_humidity_Observation
from app.server.temperature_humidity_device.crud import  create_temperature_humidity_devices, \
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
        bin16_symbol = (bin(data_to_int_list[16]))[2]
        bin16_number = (bin(data_to_int_list[16]))[3:]
        if bin16_number:
            if bin16_symbol == 1:
                Heigh_part_number = int(bin16_number, 2) * 16
            else:
                Heigh_part_number = - int(bin16_number, 2) * 16
        else:
            Heigh_part_number = 0
        Low_part_number = data_to_int_list[17]
        THTL = (Heigh_part_number + Low_part_number) / 10.0

        bin18_symbol = (bin(data_to_int_list[18]))[2]
        bin18_number = (bin(data_to_int_list[18]))[3:]
        if bin18_number:
            if bin18_symbol == 1:
                Heigh_part_number = int(bin18_number, 2) * 16
            else:
                Heigh_part_number = - int(bin18_number, 2) * 16
        else:
            Heigh_part_number = 0
        Low_part_number = data_to_int_list[19]
        HHTL = (Heigh_part_number + Low_part_number) / 10.0
        Time = data_to_int_list[20] * 16 + data_to_int_list[21]
        Index = data_to_int_list[22] * 16 + data_to_int_list[23]
        Status = data_to_int_list[24]
        Battery = data_to_int_list[25]

        # print("Barcode:", Barcode)
        # print("THTL:", THTL)
        # print("HHTL:", HHTL)
        # print("Time:", Time)
        # print("Index:", Index)
        # print("Status:", Status)
        # print("Battery:", Battery)
        name = Barcode.lstrip("0")
        print("temperature_humidity device ID:", name+" Get data")

        # 資料存入
        device_db = get_temperature_humidity_devices_by_serial_number(name)

        if not device_db:
            return name+"不存在"

        observation_in = {"temperature": THTL, "humidity": HHTL, "index": Index, "alarm_temperature": True,
                          "alarm_humidity": False, "battery": Battery, "status": Status}
        Create_temperature_humidity_Observation(observation_in, device_db.group_id, device_db.id)
