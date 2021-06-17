import requests
import logging
import os 
from src.io import files
logger = logging.getLogger(__name__)

headers = {"Content-Type" : "application/json",
           "Accept-Language" : "en_US"}

def get_missions(data_path, base_url, start_date):
    #"missions/?mission_status=SUCCEEDED&mission_status=CANCELLED&ordering=created&format=csv&execution_start_gte=2021-06-11T04:00:00.000Z"
    mission_headers = {"Content-Type" : "text/csv",
                        "Accept-Language" : "en_US"}
    endpoint = base_url + f"missions/?mission_status=SUCCEEDED&mission_status=CANCELLED&ordering=created&format=csv&execution_start_gte={start_date}T00:00:00.000Z"
    response = requests.get(endpoint, headers=headers, verify=False)
    logger.info(f"GET Request to : {endpoint} => {response.status_code}")
    files.write_text(os.path.join(data_path, "missions.csv"), response.text)
