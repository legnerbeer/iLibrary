import json
from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library, User, IFS
from os.path import dirname

#load ENV file and get the Connection Settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")


if __name__ == "__main__":
    try:
        #try to get a connection to the Servcer
        with IFS(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False) as i:

            path = '/home/ALBEER/'
            raw_result = i.readIFS(path_to_read=path, subtrees=False)
            data = json.loads(raw_result)
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")

    #
    # try:
    #     with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False) as i:
    #         path = '/a'
    #         data = i.getSingleUserInformation('Test')
    #         # print(data)
    #
    #         print(data)
    # except Exception as e:
    #     print(f"An error occurred: {e}")