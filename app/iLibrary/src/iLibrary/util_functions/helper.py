#--------------------------------------------
# Helper Functions to get better Error Mails
# --------------------------------------------
import json
from datetime import datetime, timezone


def create_success_envelope(data, message="successful"):
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    return json.dumps({
        "success": True,
        "code": 200,
        "message": message,
        "metadata": {
            "timestamp": timestamp,
            "count": len(data)
        },
        "data": data,
        "error": None
    }, indent=4, default=str)

def create_error_envelope(error_msg:str, func_name:str):
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    return json.dumps({
        "success": False,
        "code": 500,
        "message": f"An error occurred in {func_name}",
        "metadata": {
            "timestamp": timestamp,
            "count": 0
        },
        "data": [],
        "error": {"details": error_msg}
    }, indent=4, default=str)