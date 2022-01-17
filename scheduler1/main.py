import os
import json
import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import FASTEYES_OUTPUT_PATH
from app.db.database import SessionLocal
from app.models.domain.group import group
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.models.domain.staff import staff

path = os.getcwd() + "/scheduler1/file/"
app = FastAPI()
session = SessionLocal()
scheduler = BackgroundScheduler()


def job():
    """在已設定之時間上傳資料"""
    all_group = session.query(group).all()
    for each_group in all_group:
        path_2 = FASTEYES_OUTPUT_PATH + str(each_group.id) + "/output_form.json"
        with open(path_2, "r") as file:
            data = json.load(file)
        output_time_list = data['output_time']
        now = datetime.datetime.now()
        now_time = now.replace(second=0, microsecond=0)
        output = False

        for each_time in output_time_list:
            each_time_hour = int(each_time.split(":")[0])
            each_time_min = int(each_time.split(":")[1])
            output_time = now.replace(hour=each_time_hour, minute=each_time_min, second=0, microsecond=0)
            print(output_time)
            if now_time == output_time:
                output = True
                all_observation = session.query(fasteyes_observation, staff.serial_number).filter(
                    fasteyes_observation.phenomenon_time >= datetime.datetime.now() + datetime.timedelta(days=-7),
                    fasteyes_observation.staff_id == staff.id).all()
                with open(path + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ".txt", "a") as file:
                    for observation in all_observation:
                        _time = observation[0].phenomenon_time.strftime("%Y%m%d%H%M%S")
                        serial_number = observation[1]
                        file.write(_time + serial_number + "\n")

        if output:
            print("時間：", now_time, " Group_id:", each_group.id, "資料已上傳")
        else:
            print("時間：", now_time, " Group_id:", each_group.id, "此時段無需上傳""")


@app.on_event("startup")
def start_upload():
    # scheduler.add_job(func=job, trigger="interval", seconds=10)
    scheduler.add_job(func=job, trigger="interval", minutes=10)
    scheduler.start()

# uvicorn scheduler1.main:app --reload --port 8001