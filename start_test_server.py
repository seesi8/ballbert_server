import os
from Config import Config

config = Config()
db_name = config["DB_NAME"]

config["DB_NAME"] = "Testing"

try:

    os.system("python server.py")
    while True:
        break
except Exception as e:
    config["DB_NAME"] = db_name