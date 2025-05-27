import re

def safe_string(raw_name: str, max_length: int = 64) -> str:
    name = raw_name.lower()

    name = name.replace("_", "-")

    name = re.sub(r"[^a-z0-9_-]", "-", name)

    name = re.sub(r"_+", "-", name).strip("-")

    return name[:max_length]