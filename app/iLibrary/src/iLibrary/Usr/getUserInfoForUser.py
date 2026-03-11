import pyodbc
from ..util_functions.helper import create_success_envelope, create_error_envelope

class getUserInfoForUser():
    def __init__(self, connection, mapepire=False):
        self.conn = connection
        self.mapepire = mapepire
    """
    Handles user information retrieval and messaging functionalities.

    This class provides methods to interact with the database for retrieving user information
    and to send messages to specified users. It supports data retrieval in different formats
    (e.g., JSON or tuple), and it enables system messaging with configurable options.

    :ivar conn: Database connection object used for executing queries.
    :type conn: Any
    """
    def getAllUsers(self) -> dict[str, str]:
        """
        Retrieves all user information from the database. Optionally returns the data in
        JSON format depending on the provided parameter.

        Retrieves a list of users stored in the database and can output the data either as
        a list of tuples or in JSON format. The query fetches all fields available in the
        user information database table and handles cases where no data is found.

        :param wantJson: Boolean flag to indicate whether the result should be returned
            in JSON format. If set to False, the result will be a list of tuples. Default
            is False.
        :return: The data fetched from the database. When `wantJson` is True, returns a
            JSON object as a string. Otherwise, returns a list of tuples.
        """
        sql_query = "SELECT * FROM qsys2.user_info"


        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                if self.mapepire:
                    data = rows.get('data', []) if isinstance(rows, dict) else rows
                    return create_success_envelope(data)
                if not rows:
                    error_msg = f"No User found"
                    return create_error_envelope(error_msg, func_name="getAllUsers")

                # Get column names
                columns = [column[0] for column in cursor.description]


                results = [dict(zip(columns, r)) for r in rows]
                return create_success_envelope(results)



        except Exception as e:
            return create_error_envelope(error_msg=str(e), func_name="getAllUsers")

    def getSingleUserInformation(self, username: str) -> dict[str, str]:
        """
        Retrieves information about a specific user from the database based on their username. The function supports
        returning data either as a JSON-formatted string or as a tuple with corresponding database fields.

        :param username: The username of the database user whose information is to be retrieved. Must not be empty.
        :type username: str
        :param wantJson: Indicates whether the output should be formatted as JSON. Defaults to False.
        :type wantJson: bool
        :return: A tuple containing database fields if `wantJson` is False, or a JSON-formatted string if `wantJson` is True.
                 If no user is found, returns either a JSON-formatted error message or a tuple with error details, based on the
                 value of `wantJson`. Returns None if an exception occurs.
        :rtype: Union[tuple, str, None]
        :raises ValueError: If the `username` input is empty or None.
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
                row = cursor.fetchone()
                if self.mapepire:
                    #check if row empty or not
                    if not row['data']:
                        error_msg = 'No data found for User: ' + username
                        return create_error_envelope(error_msg, func_name="getSingleUserInformation")
                    return create_success_envelope(row['data'])
                if not row :
                    error_msg = 'No data found for User: ' + username
                    return create_error_envelope(error_msg, func_name="getSingleUserInformation")

                # DYNAMICALLY get column names from the database itself
                columns = [column[0] for column in cursor.description]
                row_dict = dict(zip(columns, row))

                return create_success_envelope(row_dict)

        except Exception as e:
            print(f"An error occurred: {e}")
            return create_error_envelope(error_msg=str(e), func_name="getSingleUserInformation")
