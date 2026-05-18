import json
from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library, User, IFS, System
from os.path import dirname

#load ENV file and get the Connection Settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")

def getSingleLibraryInfo():
    USE_MAPEPIRE = False

    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures the connection is properly opened and closed
        with System(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as u:

            # Call the method to retrieve all users from the system
            # The result is returned as a JSON string
            raw_result = u.get_active_jobs()

            # Parse the JSON string into a Python object (list/dictionary)
            data = json.loads(raw_result)
            counter = data['metadata'].get('count')

            # Pretty-print the parsed data with indentation for readability
            print(json.dumps(data, indent=4))
            print(counter)
    # Handle any exceptions that occur during connection or data retrieval
    except Exception as e:
        # Print the error message for debugging
        print(e)

if __name__ == "__main__":
    getSingleLibraryInfo()


