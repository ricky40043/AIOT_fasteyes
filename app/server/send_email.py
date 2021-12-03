import os
from datetime import timedelta
from typing import List

import jwt
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.config import HOST_IP
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.server.authentication import SECRET_KEY, create_access_token
from app.server.staff.crud import get_staff_by_id

load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='./templates'
)


async def send_email_async(subject: str, email_to: str, body: dict):
    print(subject)
    print(email_to)
    print(body)
    verify_code = body["verify_code"]

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        subtype="html",
        body=verify_code
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')


#
# def send_email_background(subject: str, email_to: str, body: dict,background_tasks: BackgroundTasks):
#     template = f"""
#            <html>
#                <body>
#                      <h1>
#                         員工編號: {body["serial_number"]}
#                      </h1>
#                      <h2>
#                         員工姓名: {body["name"]}
#                      </h2>
#                      <h2>
#                         員工溫度:{body["observation"]["info"]["temperature"]}
#                      </h2>
#                      <h2>
#                         員工觀測結果:{body["observation"]["id"]}
#                      </h2>
#                     <a href="{HOST_IP}/Files/download/image/device/2/file_name/{body["observation"]["image_name"]}" />
#             </body>
#            </html>
#        """
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         subtype="html",
#         html=template
#     )
#
#     fm = FastMail(conf)
#     background_tasks.add_task(
#         fm.send_message, message)


def send_Verfiy_code_email_async(email: str, verify_code: str, background_tasks: BackgroundTasks):
    title = "fasteyes verify Code"
    template = f"""
           <html>
               <body>
                     <h1>
                        認證碼：{verify_code}
                     </h1>
               </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        body=template
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return verify_code


def SendEmailVerficationEmail(email: str, background_tasks: BackgroundTasks):
    token_data = {
        "username": email
    }

    token = create_access_token(token_data)

    template = f"""
        <html>
            <body">
                  <a href="{HOST_IP}/auth/verify_email?token={token}">
                  啟用帳號
                  </a>
            </body>
        </html>
    """
    message = MessageSchema(
        subject="Email verification",
        recipients=[email],
        html=template
    )

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return token


def SendForgetPasswordEmail(email: str, password: str, background_tasks: BackgroundTasks):
    template = f"""
        <html>
            <body>
                <h1>
                    新密碼：{password}
                </h1>
            </body>
        </html>        
    """

    message = MessageSchema(
        subject="forget password",
        recipients=[email],
        html=template
    )

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)


def send_email_temperature_alert(background_tasks: BackgroundTasks, db: Session, email: str,
                                 observation_db: fasteyes_observation):
    title = "溫度異常"
    staff_db = get_staff_by_id(db, observation_db.staff_id)
    if staff_db:
        name = staff_db.info["name"]
        serial_number = staff_db.serial_number
    else:
        name = "Unknow"
        serial_number = "None"

    # send_email_background(title, email,
    #                       {'title': title, 'name': name, 'observation': observation_db.to_dict(),
    #                        'serial_number': serial_number},background_tasks)

    template = f"""
           <html>
               <body>
                     <h1>
                        員工編號: {serial_number}
                     </h1>
                     <h2>
                        員工姓名: {name}
                     </h2>
                     <h2>
                        員工溫度:{observation_db.info["temperature"]}
                     </h2>
                     <h2>
                        員工觀測結果:{observation_db.id}
                     </h2>
                    <a href="{HOST_IP}/Files/download/image/device/{observation_db.fasteyes_device_id}/file_name/{observation_db.image_name}">
                    觀測結果圖片
                    </a>
            </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        html=template
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)


def send_invite_mail(email: str, level: int, group_id : int, background_tasks: BackgroundTasks):
    token_data = {
        "email": email,
        "level": level,
        "group_id": group_id
    }

    token = create_access_token(token_data,expires_delta=timedelta(minutes=999999999))

    title = "fasteyes user 認證信"
    template = f"""
           <html>
               <body>
                     <h1>
                        認證信
                     </h1>
                     <a href="{HOST_IP}/users/verify/{token}">
                    點此連結完成認證
                    </a>
               </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        html=template
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return token