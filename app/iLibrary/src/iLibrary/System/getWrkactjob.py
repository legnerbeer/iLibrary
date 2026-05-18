from ..util_functions.helper import create_success_envelope, create_error_envelope

class GetWrkActJob:
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
    def get_active_jobs(self) -> dict[str, str]:
        """
        Retrieves information about active jobs from the system.

        This method queries the database for active job information using the
        QSYS2.ACTIVE_JOB_INFO() table function. It processes the retrieved data and
        returns it in a formatted envelope. If no active jobs are found, or an error
        occurs, an appropriate error envelope is returned.

        Returns:
            dict[str, str]: A dictionary representing a success or error envelope.

        Raises:
            Exception: If an error occurs during the database query or data processing.
        """
        sql_query = "SELECT * FROM TABLE(QSYS2.ACTIVE_JOB_INFO())"


        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                if self.mapepire:
                    data = rows.get('data', []) if isinstance(rows, dict) else rows
                    return create_success_envelope(data)
                if not rows:
                    error_msg = f"No active jobs found"
                    return create_error_envelope(error_msg, func_name="getwrkactjob")

                # Get column names
                columns = [column[0] for column in cursor.description]


                results = [dict(zip(columns, r)) for r in rows]
                return create_success_envelope(results)



        except Exception as e:
            return create_error_envelope(error_msg=str(e), func_name="getwrkactjob")

    def get_active_jobs_filter_by_subsystem(self, subsystem:str) -> dict[str, str]:
        """
        Retrieves information about active jobs from the system.
        This method queries the database for active job information using the
        """

        if not isinstance(subsystem, str):
            raise TypeError(f"Parameter 'subsystem' must be a str, got '{type(subsystem).__name__}'")

        sql_query = f"""
                    SELECT *
                    FROM TABLE(QSYS2.ACTIVE_JOB_INFO(SUBSYSTEM_LIST_FILTER => ?)) 
                    """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query, (f'{subsystem}',))
                rows = cursor.fetchall()
                if self.mapepire:
                    data = rows.get('data', []) if isinstance(rows, dict) else rows
                    return create_success_envelope(data)
                if not rows:
                    error_msg = f"No active jobs found"
                    return create_error_envelope(error_msg, func_name="get_ActiveJob_filter_by_subsystem")

                # Get column names
                columns = [column[0] for column in cursor.description]


                results = [dict(zip(columns, r)) for r in rows]
                return create_success_envelope(results)



        except Exception as e:
            return create_error_envelope(error_msg=str(e), func_name="get_ActiveJob_filter_by_subsystem")

