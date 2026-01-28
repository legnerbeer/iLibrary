from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal

class getUserInfoForUser():
    """
    Handles user information retrieval and messaging functionalities.

    This class provides methods to interact with the database for retrieving user information
    and to send messages to specified users. It supports data retrieval in different formats
    (e.g., JSON or tuple), and it enables system messaging with configurable options.

    :ivar conn: Database connection object used for executing queries.
    :type conn: Any
    """
    def getAllUsers(self, wantJson: bool = False):
        """
        Fetches all user information from the database.

        This function queries the database to retrieve user information and returns the results
        either as a list of tuples or as a JSON-formatted string, depending on the value
        of the `wantJson` parameter. If no data is found, an error message is returned instead.

        :param wantJson: Determines the format of the output. If True, the result
                         will be returned as a JSON-formatted string. If False, the
                         result will be returned as a list of tuples.
        :type wantJson: bool
        :return: The user information retrieved from the database. The format of
                 the result depends on the value of the `wantJson` parameter. If
                 no data is found, an error message is returned instead.
        :rtype: Union[list[tuple], str, None]
        """
        sql_query = "SELECT * FROM qsys2.user_info"

        def json_serial(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()

                if not rows:
                    error_msg = {'error': 'No data found'}
                    return json.dumps(error_msg, indent=4) if wantJson else [("error", "No data found")]

                # Get column names
                columns = [column[0] for column in cursor.description]

                if wantJson:
                    # Create a LIST of dictionaries
                    results = [dict(zip(columns, r)) for r in rows]
                    return json.dumps(results, indent=4, default=json_serial)

                return rows  # Returns the list of tuples

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def getSingleUserInformation(self, username: str, wantJson: bool = False):
        """
        Retrieve information for a single user based on their username.

        This function queries the database to fetch information for a specific user,
        identified by their username. The result can be returned either as a tuple
        or as a JSON-formatted string depending on the `wantJson` parameter.

        :param username: The username for which the user information needs to be retrieved.
        :type username: str
        :param wantJson: Flag indicating whether the result should be returned in JSON format
            (default is False).
        :type wantJson: bool
        :return: A dictionary representing user information as a JSON-formatted string
            if `wantJson` is True, or a tuple representing the user's row from the database
            if `wantJson` is False. Returns None if an error occurs or no user information
            is found.
        :rtype: Union[str, tuple, None]
        :raises ValueError: If the `username` parameter is not provided.
        """
        if not username:
          raise ValueError("A username is required.")

        sql_query = f"SELECT * FROM qsys2.user_info WHERE AUTHORIZATION_NAME = upper('{username}')"

        def json_serial(obj):
            # Handle datetime and Decimal (common in DB2)
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                row = cursor.fetchone()  # Since you only expect one user

                if not row:
                    error_msg = {'error': 'No data found for User: ' + username}
                    return json.dumps(error_msg, indent=4) if wantJson else ("error", error_msg['error'])

                # DYNAMICALLY get column names from the database itself
                columns = [column[0] for column in cursor.description]
                row_dict = dict(zip(columns, row))

                if wantJson:
                    return json.dumps(row_dict, indent=4, default=json_serial)
                return row  # Returns the tuple

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
