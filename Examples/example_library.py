import json
from os.path import join
import os
from dotenv import load_dotenv
from iLibrary import Library

#load ENV file and get the Connection Settings
dotenv_path = join('.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")




# ----------------------------------------------------
# make a Savefile from a library
# ----------------------------------------------------
def getSaveFile():

    # Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE = False


    PORT = 22 #for the Pub400.com use the Port 2222
    LIBRARY = '<LIBRARY_TO_SAVE>'
    SAVE_FILE_NAME = 'FOO'
    LOCAL_PATH = 'YOUR_LOCAL_PATH'
    DESCRIPTION = 'Saved from iLibrary'
    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures the connection is properly opened and closed
        with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as l:

            # Call the method to save the Library
            # The result is returned as a JSON string
            raw_result = l.saveLibrary(
                library=LIBRARY,
                saveFileName=SAVE_FILE_NAME,
                description=DESCRIPTION,
                localPath=LOCAL_PATH,
                port=PORT
            )

            # Parse the JSON string into a Python object (list/dictionary)
            data = json.loads(raw_result)

            # Pretty-print the parsed data with indentation for readability
            print(json.dumps(data, indent=4))

    # Handle any exceptions that occur during connection or data retrieval
    except Exception as e:
        # Print the error message for debugging
        print(e)



# ----------------------------------------------------
# Get library information about all libraries from
# IBM i Server using iLibrary
# ----------------------------------------------------
def getAllLibraries():
    # Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE = False

    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures the connection is properly opened and closed
        with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as l:

            # Call the method to get all libraries on the system
            # The result is returned as a JSON string
            raw_result = l.getAllLibraries()

            # Parse the JSON string into a Python object (list/dictionary)
            data = json.loads(raw_result)

            # Pretty-print the parsed data with indentation for readability
            print(json.dumps(data, indent=4))

    # Handle any exceptions that occur during connection or data retrieval
    except Exception as e:
        # Print the error message for debugging
        print(e)




# ----------------------------------------------------
# Get single library information from IBM i Server
# using iLibrary
# ----------------------------------------------------
def getSingleLibraryInfo():
    # Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE = False
    LIBRARY = '<LIBRARY>'
    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures the connection is properly opened and closed
        with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as l:

            # Call the method to show singe information about the Library
            # The result is returned as a JSON string
            raw_result = l.getLibraryInfo(
                library=LIBRARY
            )

            # Parse the JSON string into a Python object (list/dictionary)
            data = json.loads(raw_result)

            # Pretty-print the parsed data with indentation for readability
            print(json.dumps(data, indent=4))

    # Handle any exceptions that occur during connection or data retrieval
    except Exception as e:
        # Print the error message for debugging
        print(e)

if __name__ == '__main__':
    getSaveFile()
    getAllLibraries()
    getSingleLibraryInfo()