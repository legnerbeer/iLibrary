import json
from os.path import join
import os
from dotenv import load_dotenv
from iLibrary import IFS

#load ENV file and get the Connection Settings
dotenv_path = join('..', '.env')
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