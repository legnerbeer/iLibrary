from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library, User
from pathlib import Path
#load ENV file and get the Connection Settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")
DB_CREDENTIALS = {
    "db_user": DB_USER,
    "db_password": DB_PASSWORD,
    "db_host": DB_SYSTEM,
    "db_driver": DB_DRIVER
}

ok = 'Backup Completed Successfully'

if __name__ == "__main__":
    from os.path import dirname
    try:
        with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as us:
            data = us.send_message_to_user(username="ALEER", message="Hello From PyCharm")
            print(data)
    except Exception as e:
        print(f"An error occurred: {e}")