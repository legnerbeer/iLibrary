from util_functions.helper import create_success_envelope, create_error_envelope
from datetime import datetime, date, timezone
from decimal import Decimal


class getInfoForLibrary:
    def __init__(self, connection, mapepire=False):
        self.conn = connection
        self.mapepire = mapepire

    def _convert_to_json_ready(self, row, description):
        """Interne Hilfsmethode zur Typ-Konvertierung und Bereinigung."""
        row_dict = {}
        titles = [col[0] for col in description]

        for i, value in enumerate(row):
            key = titles[i]
            # Typ-Prüfung für JSON-Serialisierung
            if isinstance(value, (datetime, date)):
                row_dict[key] = value.isoformat()
            elif isinstance(value, Decimal):
                row_dict[key] = float(value)
            elif isinstance(value, bytes):
                row_dict[key] = value.decode('utf-8', errors='replace')
            elif value is None:
                row_dict[key] = None
            else:
                # Entfernt unnötige Leerzeichen von CHAR-Feldern
                row_dict[key] = str(value).strip()
        return row_dict

    def getLibraryInfo(self, library: str):
        if not library or len(library) > 10:
            # This will be caught by the 'except' block below
            return create_error_envelope('Invalid library name (max. 10 characters).', 'getLibraryInfo')


        sql_query = f"SELECT * FROM TABLE(QSYS2.LIBRARY_INFO(upper('{library}')))"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)

                # Handle Mapepire special case
                if self.mapepire:
                    result_raw = cursor.fetchall()
                    # If Mapepire returns a dict with a 'data' key:
                    data = result_raw.get('data', []) if isinstance(result_raw, dict) else result_raw
                    return create_success_envelope(data)

                # Standard Cursor Handling
                rows = cursor.fetchall()

                if not rows:
                    # Return 200 but with empty data - this is standard for "No results"
                    return create_success_envelope([], message="No data found")

                # Get column names and format results
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, r)) for r in rows]

                return create_success_envelope(results)

        except Exception as e:
            return create_error_envelope(str(e), 'getLibraryInfo')



    def getFileInfo(self, library: str, qFiles: bool = False) -> str:
        if not library:
            return create_error_envelope('Required a library name', 'getFileInfo')

        if qFiles:
            sql = f"SELECT * FROM QSYS2.SYSMEMBERSTAT WHERE SYSTEM_TABLE_SCHEMA = '{library.upper()}' AND SOURCE_TYPE IS NOT NULL ORDER BY SYSTEM_TABLE_MEMBER"
        else:
            sql = f"SELECT * FROM TABLE(QSYS2.OBJECT_STATISTICS('{library.upper()}', '*ALL')) AS X"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)

                # Mapepire often returns a dict with a 'data' key; standard DB-API returns a list of tuples.
                rows = cursor.fetchall()

                # 1. Standardize data extraction
                data_payload = rows['data'] if isinstance(rows, dict) else rows

                # 2. Check if data is None or empty
                if not data_payload:
                    return create_error_envelope(f'No Files Found in Library: {library}', 'getFileInfo')

                # 3. Handle Mapepire direct return
                if self.mapepire:
                    return create_success_envelope(data_payload)

                # 4. Process standard DB-API results (List of Tuples -> List of Dicts)
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, r)) for r in data_payload]

                # Explicit commit to release any read-locks depending on isolation level
                self.conn.commit()
                return create_success_envelope(results)

        except Exception as e:
            # Safely rollback if the connection exists and supports it
            if hasattr(self, 'conn') and self.conn:
                self.conn.rollback()
            return create_error_envelope(str(e), 'getFileInfo')

    def getAllLibraries(self):
        sql = "SELECT * FROM TABLE(QSYS2.OBJECT_STATISTICS('*ALL', '*LIB')) AS X"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)

                # Mapepire often returns a dict with a 'data' key; standard DB-API returns a list of tuples.
                rows = cursor.fetchall()

                # Standardize data extraction
                data_payload = rows['data'] if isinstance(rows, dict) else rows

                # Check if data is None or empty
                if not data_payload:
                    return create_error_envelope(f'NoLibrary found', 'getAllLibraries')

                # Handle Mapepire direct return
                if self.mapepire:
                    return create_success_envelope(data_payload)

                # Process standard DB-API results (List of Tuples -> List of Dicts)
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, r)) for r in data_payload]

                # Explicit commit to release any read-locks depending on isolation level
                self.conn.commit()
                return create_success_envelope(results)

        except Exception as e:
            # Safely rollback if the connection exists and supports it
            if hasattr(self, 'conn') and self.conn:
                self.conn.rollback()
            return create_error_envelope(str(e), 'getAllLibraries')




    # #--------------------------------------------
    # # Helper Functions to get better Error Mails
    # # --------------------------------------------
    # def __create_success_envelope(self, data, message="successful"):
    #     timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    #     return json.dumps({
    #         "success": True,
    #         "code": 200,
    #         "message": message,
    #         "metadata": {
    #             "timestamp": timestamp,
    #             "count": len(data)
    #         },
    #         "data": data,
    #         "error": None
    #     }, indent=4, default=str)
    #
    # def __create_error_envelope(self, error_msg:str, func_name:str):
    #     timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    #     return json.dumps({
    #         "success": False,
    #         "code": 500,
    #         "message": f"An error occurred in {func_name}",
    #         "metadata": {
    #             "timestamp": timestamp,
    #             "count": 0
    #         },
    #         "data": [],
    #         "error": {"details": error_msg}
    #     }, indent=4, default=str)