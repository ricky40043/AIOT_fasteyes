import os

from fastapi.testclient import TestClient

from app.main import app

URL = "http://localhost:8000"

path = os.getcwd() + "/Auto/"

client = TestClient(app)

# /Users/judhaha/AIOT_fasteyes-4/app/api/routes/user.py
# /Users/judhaha/AIOT_fasteyes-4/app/server/send_email.py
# /Users/judhaha/AIOT_fasteyes-4/app/api/routes/authentication.py
# /Users/judhaha/AIOT_fasteyes-4/app/server/authentication/crud.py
# /Users/judhaha/AIOT_fasteyes-4/app/models/schemas/temperature_humidity_device.py
# /Users/judhaha/AIOT_fasteyes-4/app/api/routes/observation.py
# /Users/judhaha/AIOT_fasteyes-4/app/server/observation/crud.py