## More Examples

**Library:**
```python
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
```

**User:**
```python

import json
from os.path import join
import os
from dotenv import load_dotenv
from iLibrary import User

#load ENV file and get the Connection Settings
dotenv_path = join('.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")

# ----------------------------------------------------
# Get all Users information from IBM i Server using
# iLibrary
# ----------------------------------------------------

def getAllUsers():
# Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE = False

    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures the connection is properly opened and closed
        with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as u:

            # Call the method to retrieve all users from the system
            # The result is returned as a JSON string
            raw_result = u.getAllUsers()

            # Parse the JSON string into a Python object (list/dictionary)
            data = json.loads(raw_result)

            # Pretty-print the parsed data with indentation for readability
            print(json.dumps(data, indent=4))

    # Handle any exceptions that occur during connection or data retrieval
    except Exception as e:
        # Print the error message for debugging
        print(e)



# ----------------------------------------------------
# Get single Users information from IBM i Server
# using iLibrary
# ----------------------------------------------------
def getSingleUser():
    # Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE = False

    # Username to search for in the IBM i system
    USERNAME_TO_SEARCH = '<USERNAME_TO_SEARCH>'

    try:
        # Establish a connection to the IBM i system using the User class
        # The context manager ensures proper connection handling (open/close)
        with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as u:

            # Retrieve detailed information for a single user
            # - username: the user profile to look up
            # Returns data as a JSON string
            raw_result = u.getSingleUserInformation(
                username=USERNAME_TO_SEARCH,
            )

            # Convert the JSON string into a Python object (dict or list)
            data = json.loads(raw_result)

            # Pretty-print the result for better readability
            print(json.dumps(data, indent=4))

    # Handle any exceptions that occur during execution
    except Exception as e:
        # Output the error message for debugging purposes
        print(e)

# ----------------------------------------------------
# Send a message to a IBM i User using iLibrary
# ----------------------------------------------------
def sendMessage():
        # Flag to enable/disable Mapepire connection mode
        USE_MAPEPIRE = False

        # Username to search for in the IBM i system
        USERNAME_TO_SEARCH = '<USERNAME>'
        MESSAGE_TO_SEND = 'From iLibrary'

        try:
            # Establish a connection to the IBM i system using the User class
            # The context manager ensures proper connection handling (open/close)
            with User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as u:

                # Retrieve detailed information for a single user
                # - username: the user profile to look up
                # Returns data as a JSON string
                raw_result = u.send_message_to_user(
                    username=USERNAME_TO_SEARCH,
                    message=MESSAGE_TO_SEND,
                )

                # Convert the JSON string into a Python object (dict or list)
                data = json.loads(raw_result)

                # Pretty-print the result for better readability
                print(json.dumps(data, indent=4))

        # Handle any exceptions that occur during execution
        except Exception as e:
            # Output the error message for debugging purposes
            print(e)


if __name__ == "__main__":
    getAllUsers()
    getSingleUser()
    sendMessage()
```
**Integrated File System (IFS):**
```python
import json
from os.path import join
import os
from dotenv import load_dotenv
from iLibrary import IFS

#load ENV file and get the Connection Settings
dotenv_path = join('.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")


if __name__ == "__main__":

# ----------------------------------------------------
# Read the IFS with iLibrary
# ----------------------------------------------------

    # Path in the IBM i Integrated File System (IFS) to read
    REMOTE_PATH_TO_READ: str = '/home/'

    # If True, reads all subdirectories recursively
    # If False, reads only the specified directory
    SUBTREE: bool = False

    # Flag to enable/disable Mapepire connection mode
    USE_MAPEPIRE: bool = False

    try:
        # Try to establish a connection to the IBM i server
        # The IFS class is used as a context manager to ensure proper cleanup
        with IFS(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=USE_MAPEPIRE) as i:

            # Call the readIFS method to retrieve file system data
            # - path_to_read: directory path in the IFS
            # - subtrees: whether to include subdirectories
            raw_result = i.readIFS(
                path_to_read=REMOTE_PATH_TO_READ,
                subtrees=SUBTREE
            )

            # Convert the returned JSON string into a Python object (dict/list)
            data = json.loads(raw_result)

            # Pretty-print the JSON data with indentation for readability
            print(json.dumps(data, indent=2))

    # Catch and handle any errors that occur during execution
    except Exception as e:
        # Print a simple error message for debugging purposes
        print(f"An error occurred: {e}")
```