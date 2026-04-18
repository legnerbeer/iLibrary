import pyodbc
from ..util_functions.helper import create_success_envelope, create_error_envelope

class getIFSClass():
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
    def readIFS(self, path_to_read:str, subtrees:bool=True) -> dict[str, str]:
        pSubtree = 'NO'
        if subtrees:
            pSubtree = 'YES'

        sql_query = f"""
                    SELECT * FROM TABLE (
                            QSYS2.IFS_OBJECT_STATISTICS(
                                    START_PATH_NAME => '{path_to_read}',
                                    SUBTREE_DIRECTORIES => '{pSubtree}'
                                    )
                                )"""


        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                if self.mapepire:
                    data = rows.get('data', []) if isinstance(rows, dict) else rows
                    return create_success_envelope(data)
                if not rows:
                    error_msg = f"No Path found for {path_to_read}"
                    return create_error_envelope(error_msg, func_name="readIFS")

                # Get column names
                columns = [column[0] for column in cursor.description]


                results = [dict(zip(columns, r)) for r in rows]
                return create_success_envelope(results)



        except Exception as e:
            return create_error_envelope(error_msg=str(e), func_name="readIFS")