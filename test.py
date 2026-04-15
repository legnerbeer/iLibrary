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
