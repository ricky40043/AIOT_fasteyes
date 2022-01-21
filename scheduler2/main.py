import asyncio
import os
import time
from queue import Queue
from typing import Tuple
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from scheduler2.crud import activity, temperature_humidity_decode
from dotenv import load_dotenv

scheduler = BackgroundScheduler()
load_dotenv('.env')
app = FastAPI()
q = Queue()
HOST_IP = os.getenv('HOST_IP')
PORT = os.getenv('UDP_PORT')
TIME_INTERVAL = int(os.getenv('TIME_INTERVAL'))


class MyUDPProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        print(data)
        q.put(data)


@app.on_event("startup")
async def start_receive():
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(lambda: MyUDPProtocol(), local_addr=(HOST_IP, PORT))


@app.on_event("startup")
async def start_deal_with_data():
    while True:
        await asyncio.sleep(TIME_INTERVAL)
        for i in range(q.qsize()):
            temperature_humidity_decode(q.get())
        activity()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    app.state.udp_transport.close()

# uvicorn scheduler2.main:app --reload --host 192.168.45.75 --port 8000
