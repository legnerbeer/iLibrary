from mapepire_python import connect
import pyodbc
from Libr.getInfoForLibrary import *
from Libr.saveLibrary import *



class Library(getInfoForLibrary, saveLibrary):
    """
    A class to manage libraries and files on an IBM i system.

    It provides methods to connect to the system via pyodbc for SQL and
    paramiko for SFTP transfers.
    """

    # ------------------------------------------------------
    # __init__ - initzialise the class
    # ------------------------------------------------------
    def __init__(self, db_user: str, db_password: str, db_host: str, db_driver: str, mapepire: bool = False):
        """
        Initializes the class attributes for a database connection.
        The actual connection is established in the __enter__ method.

        Args:
            db_user (str): The user ID for the database connection.
            db_password (str): The password for the database user.
            db_host (str): The system/host name for the database connection.
            db_driver (str): The ODBC driver to be used.
        """
        self.db_user = db_user
        self.db_host = db_host
        self.db_driver = db_driver
        self.db_password = db_password
        self.mapepire = mapepire

    # ------------------------------------------------------
    # __enter__ - enter to the class
    # ------------------------------------------------------
    def __enter__(self) -> 'Library':
        """
        Establishes the database connection when entering a 'with' block.
        """
        try:
            if not self.mapepire:
                conn_str = (
                    f"DRIVER={self.db_driver};"
                    f"SYSTEM={self.db_host};"
                    f"UID={self.db_user};"
                    f"PWD={self.db_password};"
                )
                self.conn = pyodbc.connect(conn_str, autocommit=True)

            else:
                conn_str = {
                      "host": self.db_host,
                      "port": 8076,
                      "user": self.db_user,
                      "password": self.db_password,
                    }
                self.conn = connect(conn_str)
            super().__init__(self.conn, mapepire=self.mapepire)
            return self

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Database connection failed with error: {sqlstate}")
            raise
        except Exception as e:

            print(f"Database connection failed with error: {e}")
            raise

    # ------------------------------------------------------
    # __exit__ - leave the class
    # ------------------------------------------------------
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection when exiting a 'with' block.
        This method is called automatically, even if an error occurred.
        """
        self.iclose()


    # ------------------------------------------------------
    # iClose - close connection
    # ------------------------------------------------------
    def iclose(self):
        if not self.conn:
            return

        try:
            # Both pyodbc and mapepire-python support .close()
            # but mapepire MUST have it called to kill background threads
            self.conn.close()
        except Exception:
            pass
        finally:
            self.conn = None