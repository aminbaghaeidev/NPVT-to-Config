import json


def load_tables_from_path(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tables_from_bytes(file_bytes):
    return json.loads(file_bytes.decode("utf-8"))
