import paramiko
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Union
from pathlib import PureWindowsPath, Path
from os.path import join


class saveLibrary:
    def __init__(self, connection, mapepire=False):
        """
        Initializes the saveLibrary parent class.
        """
        self.conn = connection
        self.mapepire = mapepire

    def saveLibrary(self,
                    library: str,
                    saveFileName: str,
                    dev: str = None,
                    vol: str = None,
                    toLibrary: str = None,
                    description: str = None,
                    localPath: str = None,
                    remPath: str = None,
                    getZip: bool = False,
                    port: int = None,
                    remSavf=True,
                    version: str = None,
                    max_records: Union[int, str, None] = None,
                    asp: Union[int, str, None] = None,
                    waitFile: Union[int, str, None] = None,
                    share: str = None,
                    authority: str = None
                    ) -> bool:

        trgList = ["V1R1M0", "V1R1M2", "V1R2M0", "V1R3M0", "V2R1M0", "V2R1M1",
                   "V2R2M0", "V2R3M0", "V3R0M5", "V3R1M0", "V3R2M0", "V3R6M0",
                   "V3R7M0", "V4R1M0", "V4R2M0", "V4R3M0", "V4R4M0", "V4R5M0",
                   "V5R1M0", "V5R2M0", "V5R3M0", "V5R4M0", "V6R1M0", "V6R1M1",
                   "V7R1M0", "V7R2M0", "V7R3M0", "V7R4M0", "V7R5M0", "V7R6M0"]

        if not library: raise ValueError("A library name is required.")
        if not saveFileName: raise ValueError("A save file name is required.")

        toLibrary = toLibrary if toLibrary else library
        version = version.upper() if version in trgList else "*CURRENT"

        # Start building the command
        command_str = f'SAVLIB LIB({library.upper().strip()})'
        command_str += f' DEV({dev.upper() if dev in ["*SAVF", "*MEDDFN"] else "*SAVF"})'

        if vol == '*MOUNTED':
            command_str += f' VOL({vol})'

        # 1. Create the SAVF
        if self.__crtsavf(saveFileName, toLibrary, description, max_records, asp, waitFile, share, authority):
            command_str += f" SAVF({toLibrary.strip()}/{saveFileName.strip()}) TGTRLS({version.strip()})"

            try:
                with self.conn.cursor() as cursor:
                    # Execute SAVLIB
                    cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str,))

                    if getZip:
                        # Normalize remote IFS path
                        rem_dir = remPath.rstrip('/')
                        remote_temp_savf_path = f"{rem_dir}/{saveFileName.upper()}.savf"

                        # Ensure local directory exists
                        local_dir = Path(localPath)
                        local_dir.mkdir(parents=True, exist_ok=True)
                        destination_local_path = str(local_dir / f"{saveFileName.upper()}.savf")

                        # Copy from Library to IFS
                        copy_cmd = (
                            f"CPYTOSTMF FROMMBR('/QSYS.LIB/{toLibrary.upper().strip()}.LIB/{saveFileName.upper().strip()}.FILE') "
                            f"TOSTMF('{remote_temp_savf_path}') STMFOPT(*REPLACE)"
                        )
                        cursor.execute("CALL QSYS2.QCMDEXC(?)", (copy_cmd,))

                        # 2. Download via SFTP

                        if self.__getSavFile(localFilePath=destination_local_path, remotePath=remote_temp_savf_path,
                                             port=port):
                            print(f"Success: File downloaded to {destination_local_path}")
                            # Remove temp IFS file
                            rmv_ifs_cmd = f"QSH CMD('rm -f {remote_temp_savf_path}')"
                            cursor.execute("CALL QSYS2.QCMDEXC(?)", (rmv_ifs_cmd,))
                        else:
                            print("Error: SFTP transfer failed. Check permissions and paths.")
                            return False

                        if remSavf:
                            self.removeFile(library=toLibrary, saveFileName=saveFileName)

                if not self.mapepire: self.conn.commit()
                return True

            except Exception as e:
                self.__handle_error(error=e, pgm="saveLibrary")
                if not self.mapepire: self.conn.rollback()
                return False

        return False

    def __crtsavf(self, saveFileName, library, description, max_records, asp, waitFile, share, authority) -> bool:
        if not description: description = 'A SaveFile from iLibrary'
        cmd = f"CRTSAVF FILE({library.upper().strip()}/{saveFileName.upper().strip()}) TEXT('{description.strip()}')"

        # Validation
        val_max = self.__validate_max_value(max_records, 'max_records', ['*NOMAX'], max_limit=4293525600)
        if val_max: cmd += f" MAXRCDS({val_max})"
        val_asp = self.__validate_max_value(asp, 'asp', ['*LIBASP'], max_limit=32)
        if val_asp: cmd += f" ASP({val_asp})"
        if authority: cmd += f" AUT({authority.upper()})"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (cmd,))
                if not self.mapepire: self.conn.commit()
                return True
        except Exception as e:
            if "already exists" in str(e).lower() or (len(e.args) > 0 and e.args[0] == 'HY000'):
                self.removeFile(library, saveFileName)
                try:
                    with self.conn.cursor() as cursor:
                        cursor.execute("CALL QSYS2.QCMDEXC(?)", (cmd,))
                        if not self.mapepire: self.conn.commit()
                        return True
                except:
                    return False
            return False

    def __getSavFile(self, localFilePath: str, remotePath: str, port: int = None) -> bool:
        connect_port = port if port else 22
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        def progress(transferred, total):
            print(f"Transferring: {transferred}/{total} bytes...", end="\r")

        try:
            ssh_client.connect(
                hostname=self.db_host,
                username=self.db_user,
                password=self.db_password,
                port=connect_port,
                timeout=15
            )

            with ssh_client.open_sftp() as ftp_client:
                rem_path_posix = PureWindowsPath(remotePath).as_posix()

                # Check if remote file exists before trying to get it
                try:
                    ftp_client.stat(rem_path_posix)
                except FileNotFoundError:
                    print(f"\nError: Remote file {rem_path_posix} does not exist on IBM i IFS.")
                    return False

                print(f"Starting download: {rem_path_posix} -> {localFilePath}")
                ftp_client.get(rem_path_posix, localFilePath, callback=progress)
                print("\nDownload complete.")
                return True

        except Exception as e:
            print(f"\nSFTP Error Details: {str(e)}")
            return False
        finally:
            ssh_client.close()

    def removeFile(self, library: str, saveFileName: str) -> bool:
        cmd = f"DLTF FILE({library.upper().strip()}/{saveFileName.upper().strip()})"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (cmd,))
                if not self.mapepire: self.conn.commit()
                return True
        except:
            return False

    def __validate_max_value(self, value, param_name, str_format, min_limit=1, max_limit=None):
        if value is None: return False
        if isinstance(value, str) and value.upper() in str_format: return value.upper()
        try:
            num = int(value)
            if max_limit and (num < min_limit or num > max_limit): return False
            return num
        except:
            return False

    def __handle_error(self, error, pgm: str):
        print(f"--- Error in {pgm} ---")
        try:
            state = error.args[0] if len(error.args) > 0 else "N/A"
            msg = error.args[1] if len(error.args) > 1 else str(error)
            print(f"SQLSTATE: {state}\nMessage: {msg}")
        except:
            print(f"Details: {str(error)}")