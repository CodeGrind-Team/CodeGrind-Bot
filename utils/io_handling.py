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


@to_thread
def read_ratings_txt(title: str) -> Any | None:
    with open('ratings.txt', 'r', encoding="UTF-8") as file:
        for line in file:
            line = line.strip().split('\t')
            if line[2] == title:
                return line[0].split('.')[0]
