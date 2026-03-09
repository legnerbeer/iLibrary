import json
from datetime import datetime, date
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

    def getLibraryInfo(self, library: str, wantJson=True):
        if not library or len(library) > 10:
            raise ValueError("Ungültiger Bibliotheksname (max. 10 Zeichen).")

        sql_query = f"SELECT * FROM TABLE(QSYS2.LIBRARY_INFO(upper('{library}')))"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                if self.mapepire:
                    return json.dumps(rows['data'], indent=4)
                if not rows:
                    error_msg = {'error': 'No data found'}
                    return json.dumps(error_msg, indent=4) if wantJson else [("error", "No data found")]

                # Get column names
                columns = [column[0] for column in cursor.description]

                if wantJson:
                    # Create a LIST of dictionaries
                    results = [dict(zip(columns, r)) for r in rows]
                    return json.dumps(results, indent=4)

                return rows
        except Exception as e:
            print(f"Fehler bei getLibraryInfo: {e}")
            return None

    def getFileInfo(self, library: str, qFiles: bool = False) -> str:
        if not library:
            return json.dumps([{"error": "A library name is required."}])

        if qFiles:
            sql = f"SELECT * FROM QSYS2.SYSMEMBERSTAT WHERE SYSTEM_TABLE_SCHEMA = '{library.upper()}' AND SOURCE_TYPE IS NOT NULL ORDER BY SYSTEM_TABLE_MEMBER"
        else:
            sql = f"SELECT * FROM TABLE(QSYS2.OBJECT_STATISTICS('{library.upper()}', '*ALL')) AS X"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                if self.mapepire:
                    return json.dumps(rows['data'], indent=4)
                if not rows:
                    return json.dumps([{"error": f"No Files Found in Library: {library}"}])

                result_list = [self._convert_to_json_ready(row, cursor.description) for row in rows]
                self.conn.commit()
                return json.dumps(result_list, indent=4)
        except Exception as e:
            if self.conn: self.conn.rollback()
            return json.dumps([{"error": f"Database Error: {str(e)}"}])

    def getAllLibraries(self):
        sql = "SELECT * FROM TABLE(QSYS2.OBJECT_STATISTICS('*ALL', '*LIB')) AS X"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                if self.mapepire:
                    return json.dumps(rows['data'], indent=4)

                # Robust check for Mapepire/ODBC metadata
                if cursor.description is None:
                    return json.dumps([{"error": "Database Error: Metadata (description) is missing"}])

                if not rows:
                    return json.dumps([{"error": "No Libraries found"}])

                result_list = [self._convert_to_json_ready(row, cursor.description) for row in rows]

                # Only commit if we aren't using Mapepire (which usually handles this differently)
                if not self.mapepire:
                    self.conn.commit()

                return json.dumps(result_list, indent=4)
        except Exception as e:
            return json.dumps([{"error": f"Database Error: {str(e)}"}])