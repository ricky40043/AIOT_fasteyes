import datetime
import json
import time

from app.core.config import FASTEYES_OUTPUT_PATH
from app.db.database import get_db
from app.server.fasteyes_observation import output_interval_data_csv
from app.server.group.crud import get_All_groups


def task(db, group_id):
    csv_file = output_interval_data_csv(db, group_id, None, None)
    print(csv_file)
    print("Job Completed!")


while True:
    now = datetime.datetime.now()
    db = next(get_db())
    for each_group in get_All_groups(db):
        path = FASTEYES_OUTPUT_PATH + str(each_group.id) + "/output_form.json"
        # Opening JSON file
        f = open(path)
        # returns JSON object as
        # a dictionary
        data = json.load(f)
        # Closing file
        f.close()

        output_time = data["output_time"]
        for each_output_time in output_time:
            print(each_output_time)
            if now.strftime("%H:%M") == each_output_time or True:
                task(db, each_group.id)
            else:
                print(now)

    # sleep for 1 min
    time.sleep(1 * 1 * 1 * 60)

