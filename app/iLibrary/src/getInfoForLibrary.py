import json
from datetime import datetime, date
from decimal import Decimal


class getInfoForLibrary:
    def __init__(self, connection):
        self.conn = connection

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
                row = cursor.fetchone()

                if not row:
                    error_msg = {"error": f"No data found for library: {library}"}
                    return json.dumps(error_msg, indent=4) if wantJson else ("error", error_msg["error"])

                if wantJson:
                    return json.dumps(self._convert_to_json_ready(row, cursor.description), indent=4)

                return row
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

                if not rows:
                    return json.dumps([{"error": f"No Files Found in Library: {library}"}])

                result_list = [self._convert_to_json_ready(row, cursor.description) for row in rows]
                self.conn.commit()
                return json.dumps(result_list, indent=4)
        except Exception as e:
            if self.conn: self.conn.rollback()
            return json.dumps([{"error": f"Database Error: {str(e)}"}])

    def getAllLibraries(self):
        # Hier nutzen wir nun auch die dynamische Spaltenerkennung statt der harten Liste
        sql = "SELECT * FROM TABLE(QSYS2.OBJECT_STATISTICS('*ALL', '*LIB')) AS X"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()

                if not rows:
                    return json.dumps([{"error": "No Libraries found"}])

                result_list = [self._convert_to_json_ready(row, cursor.description) for row in rows]
                self.conn.commit()
                return json.dumps(result_list, indent=4)
        except Exception as e:
            print(f"Fehler bei getAllLibraries: {e}")
            if self.conn: self.conn.rollback()
            return False