import json
import os
from datetime import datetime
from typing import Any

from utils.run_blocking import to_thread


@to_thread
def read_file(path: str) -> Any | None:
    if os.path.exists(path):
        with open(path, 'r', encoding="UTF-8") as file:
            data = json.load(file)
        return data

    data = {
        "users": {},
        "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "channels": []
    }

    with open(path, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4)

    return data


@to_thread
def write_file(path: str, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4)
