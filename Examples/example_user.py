import json
from os.path import join
import os
from dotenv import load_dotenv
from iLibrary import User

#load ENV file and get the Connection Settings
dotenv_path = join('..', '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")

if __name__ == "__main__":

# ----------------------------------------------------
# Get all Users information from IBM i Server using
# iLibrary
# ----------------------------------------------------


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


#TODO ---------------------------------------------
#TODO Write the SendMessage Function to here