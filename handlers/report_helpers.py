import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

WIB = ZoneInfo("Asia/Jakarta")

HARI_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu",
}

BULAN_ID = {
    "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
    "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
    "09": "September", "10": "Oktober", "11": "November", "12": "Desember",
}


def keyboard_unit(prefix: str = "unit"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚔 JSM 211", callback_data=f"{prefix}:JSM 211"),
            InlineKeyboardButton("🚔 JSM 212", callback_data=f"{prefix}:JSM 212"),
        ],
    ])


def keyboard_shift(prefix: str = "shift"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("☀️ Shift 1", callback_data=f"{prefix}:1"),
            InlineKeyboardButton("🌤️ Shift 2", callback_data=f"{prefix}:2"),
            InlineKeyboardButton("🌙 Shift 3", callback_data=f"{prefix}:3"),
        ],
    ])


def keyboard_pilihan(prefix: str, opsi: list[tuple[str, str]], per_baris: int = 2):
    baris = []
    baris_sekarang = []

    for label, nilai in opsi:
        baris_sekarang.append(
            InlineKeyboardButton(label, callback_data=f"{prefix}:{nilai}")
        )
        if len(baris_sekarang) == per_baris:
            baris.append(baris_sekarang)
            baris_sekarang = []

    if baris_sekarang:
        baris.append(baris_sekarang)

    return InlineKeyboardMarkup(baris)


def keyboard_preview():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Kirim Laporan", callback_data="preview:kirim"),
            InlineKeyboardButton("❌ Batal", callback_data="preview:batal"),
        ],
    ])


def tanggal_indo(separator: str = " ,") -> str:
    now = datetime.datetime.now(WIB)
    hari = HARI_ID[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = BULAN_ID[now.strftime("%m")]
    tahun = now.strftime("%Y")
    return f"{hari}{separator}{tanggal} {bulan} {tahun}"


def ucapan_waktu() -> str:
    sekarang = datetime.datetime.now(WIB)
    total_menit = sekarang.hour * 60 + sekarang.minute

    if total_menit < 11 * 60:
        return "Selamat Pagi"
    if total_menit < 15 * 60:
        return "Selamat Siang"
    if total_menit < 17 * 60 + 30:
        return "Selamat Sore"
    return "Selamat Malam"


def escape_markdown(text: str) -> str:
    if not text:
        return "-"

    text = str(text)
    for char in ("_", "*", "[", "]", "`"):
        text = text.replace(char, "\\" + char)
    return text


def nilai_callback(query_data: str) -> str:
    return query_data.split(":", 1)[1]


async def tampilkan_preview(
    update: Update,
    pesan: str,
    parse_mode: Optional[str] = None,
):
    kwargs = {
        "text": (
            "📋 *CEK DULU YA:*\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"{pesan}"
        ),
        "reply_markup": keyboard_preview(),
    }
    if parse_mode:
        kwargs["parse_mode"] = parse_mode

    await update.message.reply_text(**kwargs)


async def handle_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    builder,
    parse_mode: Optional[str] = None,
):
    query = update.callback_query
    await query.answer()

    if query.data == "preview:batal":
        await query.edit_message_text("Pembuatan laporan dibatalkan. ❌")
        return ConversationHandler.END

    pesan = builder(context.user_data)
    kwargs = {"text": pesan}
    if parse_mode:
        kwargs["parse_mode"] = parse_mode

    await query.edit_message_text(**kwargs)
    return ConversationHandler.END


async def cancel_laporan(
    update: Update,
    pesan: str = "Pembuatan laporan dibatalkan. ❌",
):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(pesan)
    else:
        await update.message.reply_text(pesan)
    return ConversationHandler.END