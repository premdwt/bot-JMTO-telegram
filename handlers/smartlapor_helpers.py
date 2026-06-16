import time
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

RATE_LIMIT_DETIK = 15
_terakhir_request: dict[int, float] = {}


def cek_rate_limit(user_id: int) -> Optional[int]:
    sekarang = time.time()
    terakhir = _terakhir_request.get(user_id, 0)
    sisa = RATE_LIMIT_DETIK - (sekarang - terakhir)
    if sisa > 0:
        return int(sisa) + 1
    _terakhir_request[user_id] = sekarang
    return None


def ambil_angka(teks: str) -> str:
    return "".join(ch for ch in str(teks) if ch.isdigit())


def keyboard_preview(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Kirim Laporan", callback_data=f"{prefix}:kirim"),
            InlineKeyboardButton("❌ Batal", callback_data=f"{prefix}:batal"),
        ],
    ])


def keyboard_oddo_konfirmasi(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ya, lanjut", callback_data=f"{prefix}:lanjut"),
            InlineKeyboardButton("🔄 Ulang Oddo Akhir", callback_data=f"{prefix}:ulang"),
        ],
    ])