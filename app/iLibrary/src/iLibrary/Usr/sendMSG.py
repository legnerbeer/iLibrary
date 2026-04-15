from ..util_functions.helper import create_success_envelope, create_error_envelope


class sendMSG():
    """
    Handles message-related operations by providing functionality to send messages
    to specific users within the system. The class interacts with system APIs to
    execute the required operations and ensures the input parameters are validated
    before proceeding with the message sending process.

    Attributes supported by this class are not specified because the class relies
    on method-level operations.
    """
    def __init__(self, connection, mapepire=False):
        self.conn = connection
        self.mapepire = mapepire
    def send_message_to_user(
            self,
            username: str,
            message: str,
            # tomsgq: str = None,
            # msgtype: str = None,
            # rpymsgq: str = None,
            ccsid: int = None
    ) -> dict[str, str]:
        """
        Sends a message to a specified user on the system. This method interacts with the system
        to send a message by executing an SQL query. It validates the required
        inputs and raises an exception if they are missing. Optional parameters for
        further message configuration can also be provided.

        :param username: The username of the recipient to whom the message will be sent.
        :type username: str
        :param message: The actual text message to be sent to the user.
        :type message: str
        :param ccsid: Optional character set identifier (CCSID) for the message. Defaults to None.
        :type ccsid: int, optional

        :return: None if the message is sent successfully.
        :rtype: None

        :raises ValueError: If any required parameter, such as `username` or `message`, is missing.

        :raises Exception: Any other exceptions that occur during the execution of the
            SQL query are raised, indicating issues during the process of sending the
            message.
        """
        if not username:
            raise ValueError("Username are required.")
        if not message:
            raise ValueError("Message are required.")

        username = username.upper()
        message = message.upper()
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as counter FROM QSYS2.USER_INFO WHERE AUTHORIZATION_NAME = ?", (username,))
            data = cursor.fetchone()
            if self.mapepire:
                counter = data['data'][0].get('COUNTER')
            else:
                counter = data[0]
            if counter != 1:
                return create_error_envelope(error_msg="User not Found", func_name='sendMSG')

        sql_query = f"CALL QSYS2.QCMDEXC('SNDMSG MSG(''{message}'') TOUSR({username})')"
        if ccsid:
            sql_query += f" CCSID({ccsid})"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                row_dict= f'Message sent to {username}'
                return create_success_envelope(row_dict)
        except Exception as e:
            return create_error_envelope(str(e), 'sendMSG')