import csv
import datetime
import json
import os
import time

# from app.core.config import FASTEYES_OUTPUT_PATH
# from app.db.database import get_db
# from app.server.fasteyes_observation import output_interval_data_csv
# from app.server.group.crud import get_All_groups
from dotenv import load_dotenv

load_dotenv('.env')
FASTEYES_OUTPUT_PATH = os.getenv('FASTEYES_OUTPUT_PATH')

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import class_mapper
from datetime import datetime, timedelta

import os

# config_path = os.path.abspath(os.path.dirname(__file__))
# print(config_path)
# SQLALCHEMY_DATABASE_URL = "sqlite:///"+ os.path.join(config_path, 'sql_app_20210304.db')
SQLALCHEMY_DATABASE_URL = "sqlite:///sql_app_20211130.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:88888888@192.168.45.51/fastapi_db_20210924"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine, )
Base = declarative_base()

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON


class fasteyes_observation(Base):
    __tablename__ = "fasteyes_observations"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    fasteyes_device_id = Column(Integer, ForeignKey("fasteyes_devices.id"))
    phenomenon_time = Column(DateTime, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    result = Column(Boolean, index=True)
    image_name = Column(String, index=True)
    info = Column(JSON, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"))

    def __init__(self, group_id, fasteyes_device_id, phenomenon_time, info, result, image_name, staff_id, **kwargs):
        self.group_id = group_id
        self.fasteyes_device_id = fasteyes_device_id
        self.phenomenon_time = phenomenon_time
        self.info = info
        self.result = result
        self.image_name = image_name
        self.staff_id = staff_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class staff(Base):
    __tablename__ = "staffs"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    status = Column(Integer, index=True, default=True)
    serial_number = Column(String, index=True)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    info = Column(JSON, index=True)

    def __init__(self, department_id, group_id, status, serial_number, info, start_date, **kwargs):
        self.department_id = department_id
        self.group_id = group_id
        self.status = status
        self.serial_number = serial_number
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.start_date = start_date


class group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, name, **kwargs):
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_All_groups(db: Session):
    return db.query(group).all()


def output_observations_by_group(db: Session, group_id: int, start_timestamp: datetime, end_timestamp: datetime,
                                 resign_staff_output: bool, output_fasteyes_list: list):
    if start_timestamp is None:
        start_timestamp = datetime.now() - timedelta(days=100)
    if end_timestamp is None:
        end_timestamp = datetime.now()

    if resign_staff_output:
        output_db = db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id,
                                                          fasteyes_observation.fasteyes_device_id.in_(
                                                              output_fasteyes_list)).filter(
            fasteyes_observation.phenomenon_time >= start_timestamp,
            fasteyes_observation.phenomenon_time <= end_timestamp).filter(
            staff.id == fasteyes_observation.staff_id, ).all()
    else:
        output_db = db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id,
                                                          fasteyes_observation.fasteyes_device_id.in_(
                                                              output_fasteyes_list)).filter(
            fasteyes_observation.phenomenon_time >= start_timestamp,
            fasteyes_observation.phenomenon_time <= end_timestamp).filter(
            staff.status == 1, staff.id == fasteyes_observation.staff_id).all()
    return output_db


def output_interval_data_csv(db, group_id, start_timestamp, end_timestamp):
    path = FASTEYES_OUTPUT_PATH + str(group_id) + "/output_form.json"
    f = open(path)
    data = json.load(f)
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
        each_data = []
        for each_item in name_list:
            if each_item in observation_dict.keys():
                each_data.append(observation_dict[each_item])
            elif each_item in observation_dict["info"].keys():
                each_data.append(observation_dict["info"][each_item])

        observation_list.append(each_data)
    now = datetime.now()
    file_location = FASTEYES_OUTPUT_PATH + str(group_id) + '/'+now.strftime("%Y-%m-%dT%H:%M:%S")+'Fasteyes觀測結果.csv'
    with open(file_location, 'w') as f:
        w = csv.writer(f)
        for eachdata in observation_list:
            w.writerow(eachdata)

    return file_location


def task(db, group_id):
    csv_file = output_interval_data_csv(db, group_id, None, None)
    print(csv_file)
    print("Job Completed!")


while True:
    now = datetime.now()
    db = next(get_db())
    for each_group in get_All_groups(db):
        path = FASTEYES_OUTPUT_PATH + str(each_group.id) + "/output_form.json"
        f = open(path)
        data = json.load(f)  # returns JSON object as
        f.close()

        output_time = data["output_time"]
        for each_output_time in output_time:
            print(each_output_time)
            if now.strftime("%H:%M") == each_output_time:
                task(db, each_group.id)
            else:
                print(now)

    # sleep for 1 min
    time.sleep(1 * 1 * 1 * 60)

# import schedule
# import time
#
# def task():
#     print("Job Executing!")
#
# # for every n minutes
# schedule.every(10).seconds.do(task)
#
# # every hour
# schedule.every().hour.do(task)
#
# # every daya at specific time
# schedule.every().day.at("10:30").do(task)
#
# # schedule by name of day
# schedule.every().monday.do(task)
#
# # name of day with time
# schedule.every().wednesday.at("13:15").do(task)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

# import sched, time
#
# s = sched.scheduler(time.time, time.sleep)
#
#
# def print_time(a='default'):
#     print("From print_time", time.time(), a)
#
#
# def print_some_times():
#     print(time.time())
#     s.enter(10, 1, print_time)
#     s.enter(5, 2, print_time, argument=('positional',))
#     s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
#     s.run()
#     print(time.time())
#
#
# while True:
#     print_some_times()
