import copy
import json
from typing import Any

from .models import BbaState

DEFAULT_SEED: dict[str, Any] = {
    "adm": {"u": "admin", "p": "admin123"},
    "st": [{"login": "demo", "pass": "demo123", "name": "Namuna O'quvchi", "sid": 1}],
    "qs": [],
    "res": [],
    "dur": 90,
    "vars": [],
    "act": None,
}

DEF = {
    "st": DEFAULT_SEED["st"],
    "qs": [],
    "res": [],
    "dur": 90,
}

PB = 100_000


def _ensure_main_seed() -> None:
    row, created = BbaState.objects.get_or_create(id=1, defaults={"data": copy.deepcopy(DEFAULT_SEED)})
    if created:
        return
    data = row.data or {}
    st = data.get("st")
    adm = data.get("adm")
    empty_st = not adm and (not isinstance(st, list) or len(st) == 0)
    if empty_st or row.data in ({}, None) or data == {}:
        row.data = copy.deepcopy(DEFAULT_SEED)
        row.save(update_fields=["data", "updated_at"])


def get_data(row_id: int) -> Any | None:
    _ensure_main_seed()
    try:
        row = BbaState.objects.get(pk=row_id)
    except BbaState.DoesNotExist:
        return None
    return row.data


def upsert_data(row_id: int, data: Any) -> None:
    BbaState.objects.update_or_create(id=row_id, defaults={"data": data})


def delete_id(row_id: int) -> None:
    BbaState.objects.filter(pk=row_id).delete()


def delete_from_id(min_id: int) -> None:
    BbaState.objects.filter(id__gte=min_id).delete()


def list_data_from_id(min_id: int) -> list[dict]:
    return [{"data": row.data} for row in BbaState.objects.filter(id__gte=min_id).order_by("id")]


def import_from_legacy_sqlite(path: str) -> int:
    """Import rows from Node better-sqlite3 bba.sqlite file."""
    import sqlite3

    conn = sqlite3.connect(path)
    try:
        cur = conn.execute("SELECT id, data FROM bba_state")
        count = 0
        for row_id, raw in cur.fetchall():
            data = json.loads(raw) if isinstance(raw, str) else raw
            upsert_data(int(row_id), data)
            count += 1
        return count
    finally:
        conn.close()
