import json
from typing import Any


JsonDict = dict[str, Any]


def dump_json(value: JsonDict | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def load_json(value: str | None) -> JsonDict:
    if not value:
        return {}
    data = json.loads(value)
    if not isinstance(data, dict):
        return {}
    return data


def merge_options(base: JsonDict | None, override: JsonDict | None) -> JsonDict:
    merged = dict(base or {})
    merged.update(override or {})
    return merged
