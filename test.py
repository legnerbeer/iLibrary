from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library, User
from os.path import dirname

#load ENV file and get the Connection Settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")


if __name__ == "__main__":
    from os.path import dirname
    try:
        with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=True) as u:
            # data = u.getSingleUserInformation(username=f"{DB_USER}")
            # print(data)
            data = u.send_message_to_user(f"{DB_USER}", 'Test with JSON')
            print(data)
    except Exception as e:
        print(f"An error occurred: {e}")