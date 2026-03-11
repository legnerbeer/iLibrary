import paramiko
from typing import Union
from pathlib import PureWindowsPath, Path
from ..util_functions.helper import create_success_envelope, create_error_envelope


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
                    getZip: bool = True,
                    port: int = None,
                    version: str = None,
                    max_records: Union[int, str, None] = None,
                    asp: Union[int, str, None] = None,
                    waitFile: Union[int, str, None] = None,
                    share: str = None,
                    authority: str = None
                    ) -> dict[str, str]:

        trgList = ["V1R1M0", "V1R1M2", "V1R2M0", "V1R3M0", "V2R1M0", "V2R1M1",
                   "V2R2M0", "V2R3M0", "V3R0M5", "V3R1M0", "V3R2M0", "V3R6M0",
                   "V3R7M0", "V4R1M0", "V4R2M0", "V4R3M0", "V4R4M0", "V4R5M0",
                   "V5R1M0", "V5R2M0", "V5R3M0", "V5R4M0", "V6R1M0", "V6R1M1",
                   "V7R1M0", "V7R2M0", "V7R3M0", "V7R4M0", "V7R5M0", "V7R6M0"]

        if not library:
            return create_error_envelope(error_msg="Library not found.", func_name='saveLibrary')
        if not saveFileName:
            return create_error_envelope(error_msg="A save file name is required.", func_name='saveLibrary')
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as counter FROM TABLE(QSYS2.LIBRARY_INFO(?))", (library.upper(),))
            data = cursor.fetchone()
            if self.mapepire:
                counter = data['data'][0].get('COUNTER')
            else:
                counter = data[0]
            if counter != 1:
                return create_error_envelope(error_msg="Library not found.", func_name='saveLibrary')
            # Standardize inputs

        toLibrary = toLibrary if toLibrary else library
        version = version.upper() if version and version.upper() in trgList else "*CURRENT"


        # Build SAVLIB command
        command_str = f'SAVLIB LIB({library.upper().strip()})'
        command_str += f' DEV({dev.upper() if dev in ["*SAVF", "*MEDDFN"] else "*SAVF"})'
        if vol == '*MOUNTED':
            command_str += f' VOL({vol})'

        try:
            # 1. Create the SAVF on IBM i
            if self.__crtsavf(saveFileName, toLibrary, description, max_records, asp, waitFile, share, authority):
                command_str += f" SAVF({toLibrary.strip()}/{saveFileName.strip()}) TGTRLS({version.strip()})"

                with self.conn.cursor() as cursor:
                    # Execute the Save Library command
                    cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str,))

                    # 2. Handle SFTP Download if requested
                    if getZip:
                        # Resolve local path logic
                        local_dir = Path(localPath) if localPath else Path.home() / "Downloads"
                        local_dir.mkdir(parents=True, exist_ok=True)
                        destination_local_path = str(local_dir / f"{saveFileName.upper()}.savf")

                        # Normalize remote IFS path (Ensure remPath is provided if getZip is True)
                        rem_dir = remPath.rstrip('/') if remPath else '/tmp'
                        remote_temp_savf_path = f"{rem_dir}/{saveFileName.upper()}.savf"

                        # Copy from Library (*FILE) to IFS (*STMF)
                        copy_cmd = (
                            f"CPYTOSTMF FROMMBR('/QSYS.LIB/{toLibrary.upper().strip()}.LIB/{saveFileName.upper().strip()}.FILE') "
                            f"TOSTMF('{remote_temp_savf_path}') STMFOPT(*REPLACE)"
                        )
                        cursor.execute("CALL QSYS2.QCMDEXC(?)", (copy_cmd,))

                        # Perform SFTP transfer
                        if self.__getSavFile(localFilePath=destination_local_path, remotePath=remote_temp_savf_path,
                                             port=port):
                            # Clean up the temporary IFS file
                            rmv_ifs_cmd = f"QSH CMD('rm -f {remote_temp_savf_path}')"
                            cursor.execute("CALL QSYS2.QCMDEXC(?)", (rmv_ifs_cmd,))
                            success_msg = f"Success: Downloaded to {destination_local_path}"
                        else:
                            return create_error_envelope(error_msg="Error: SFTP transfer failed.",
                                                         func_name='saveLibrary')


                    if not self.mapepire:
                        self.conn.commit()

                    return create_success_envelope(data=[], message=success_msg)

            else:
                return create_error_envelope(error_msg="Failed to create Save File (SAVF).", func_name='saveLibrary')

        except Exception as e:
            if not self.mapepire:
                self.conn.rollback()
            return create_error_envelope(error_msg=str(e), func_name='saveLibrary')
        finally:
            self.removeFile(library=toLibrary, saveFileName=saveFileName)


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
                    return False

                ftp_client.get(rem_path_posix, localFilePath)
                return True

        except Exception as e:
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
