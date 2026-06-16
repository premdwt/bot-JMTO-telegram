import datetime
import json
import os
from typing import Optional

from handlers.report_helpers import WIB

SHIFT_SESSIONS_FILE = "shift_sessions.json"
EXPIRE_JAM = 10


def _load_sessions() -> dict:
    if not os.path.exists(SHIFT_SESSIONS_FILE):
        return {}
    with open(SHIFT_SESSIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_sessions(data: dict):
    with open(SHIFT_SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_laporan_awal(data: dict) -> bool:
    return str(data.get("oddo_akhir", "")).strip() == "0"


def simpan_sesi_shift(user_id: int, data: dict):
    sekarang = datetime.datetime.now(WIB)
    sessions = _load_sessions()
    sessions[str(user_id)] = {
        "saved_at": sekarang.isoformat(),
        "expires_at": (sekarang + datetime.timedelta(hours=EXPIRE_JAM)).isoformat(),
        "data": dict(data),
    }
    _save_sessions(sessions)


def hapus_sesi_shift(user_id: int):
    sessions = _load_sessions()
    if str(user_id) in sessions:
        del sessions[str(user_id)]
        _save_sessions(sessions)


def get_sesi_shift(user_id: int) -> Optional[dict]:
    sessions = _load_sessions()
    sesi = sessions.get(str(user_id))
    if not sesi:
        return None

    expires_at = datetime.datetime.fromisoformat(sesi["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=WIB)

    if datetime.datetime.now(WIB) >= expires_at:
        hapus_sesi_shift(user_id)
        return None

    return sesi