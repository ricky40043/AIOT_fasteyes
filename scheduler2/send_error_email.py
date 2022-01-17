# # from app.server.send_email import send_email_device_alert
# from .main import app
#
# def send_email(email, device_name, serial_number, area, id,
#                temperature, temp_lower_limit, temp_upper_limit,
#                humidity, hum_lower_limit, hum_upper_limit, battery):
#     data = {
#         "email": email,
#         "title": "溫濕度裝置異常",
#         "template": f"""
#                        <html>
#                            <body>
#                                  <h1>
#                                     裝置名稱: {device_name}
#                                  </h1>
#                                  <h2>
#                                     裝置編號: {serial_number}
#                                  </h2>
#                                  <h2>
#                                     裝置位置: {area}
#                                  </h2>
#                                  <h2>
#                                     觀測結果ID: {id}
#                                  </h2>
#                                  <h2>
#                                     溫度:{temperature}
#                                  </h2>
#                                  <h4>
#                                     溫度正常範圍:
#                                     {temp_lower_limit}°C～
#                                     {temp_upper_limit}°C
#                                  </h4>
#                                  <h2>
#                                     濕度:{humidity}
#                                  </h2>
#                                  <h4>
#                                     濕度正常範圍:
#                                     {hum_lower_limit}％～
#                                     {hum_upper_limit}％
#                                  </h4>
#                                  <h2>
#                                     電池電量:{battery}
#                                  </h2>
#                            </body>
#                        </html>
#                    """
#     }
#     send_email_device_alert(background_tasks=app.background_tasks,
#                             email="dave@fastwise", observation_db=observation_db, device_db=device_db)