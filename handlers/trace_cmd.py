from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import datetime

from handlers.report_helpers import (
    BULAN_ID,
    HARI_ID,
    WIB,
    cancel_laporan,
    escape_markdown,
    handle_preview,
    keyboard_pilihan,
    keyboard_preview,
    keyboard_shift,
    keyboard_unit,
    nilai_callback,
    tampilkan_preview,
)

(
    UNIT_T, PERSONIL1, PERSONIL2, MCSS, TERIMA_INFO, TIBA_LOKASI,
    LOKASI_T, SHIFT_T, JENIS_K, NOPOL, KENDALA, TINDAKAN, PREVIEW_T,
) = range(13)


def _tanggal_trace():
    now = datetime.datetime.now(WIB)
    hari = HARI_ID[now.strftime("%A")]
    tanggal = f"{now.strftime('%d')} {BULAN_ID[now.strftime('%m')]} {now.strftime('%Y')}"
    return hari, tanggal


def _buat_pesan_trace(user_data: dict) -> str:
    hari, tanggal = _tanggal_trace()

    return (
        "*LAPORAN MCS RUAS SUMO*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{escape_markdown(user_data.get('unit', '-'))}\n\n"
        f"1. {escape_markdown(user_data.get('p1', '-'))}\n"
        f"2. {escape_markdown(user_data.get('p2', '-'))}\n\n"
        f"MCSS : {escape_markdown(user_data.get('mcss', '-'))}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hari : {hari}\n"
        f"Tanggal : {tanggal}\n"
        f"Info diterima : {escape_markdown(user_data.get('terima_info', '-'))}\n"
        f"Sampai dilokasi : {escape_markdown(user_data.get('tiba_lokasi', '-'))}\n"
        f"Lokasi : {escape_markdown(user_data.get('lokasi_t', '-'))}\n"
        f"Shift : {escape_markdown(user_data.get('shift_t', '-'))}\n\n"
        f"GIAT {escape_markdown(user_data.get('unit', '-'))}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Mohon ijin melaporkan 1 kendaraan >>\n"
        f"Jenis : {escape_markdown(user_data.get('jenis_k', '-'))}\n"
        f"No Pol : {escape_markdown(user_data.get('nopol', '-'))}\n"
        f"Kendala : {escape_markdown(user_data.get('kendala', '-'))}\n\n"
        "TINDAK LANJUT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{escape_markdown(user_data.get('tindakan', '-'))}\n\n"
        "Demikian yang dapat dilaporkan.\n"
        "Terima Kasih 🙏🏼"
    )


async def _lanjut_personil1(update: Update, unit: str):
    teks = f"✅ Unit: *{unit}*\n\n2️⃣ Masukkan nama Personil 1:"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(teks, parse_mode="Markdown")
    else:
        await update.message.reply_text(teks, parse_mode="Markdown")


async def _lanjut_shift(update: Update):
    teks = "8️⃣ Pilih shift (atau ketik manual, contoh: 2):"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            teks, reply_markup=keyboard_shift("trace_shift")
        )
    else:
        await update.message.reply_text(
            teks, reply_markup=keyboard_shift("trace_shift")
        )


async def mulai_trace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ Siap! Mari buat Laporan Penanganan Kendala (Trace).\n\n"
        "1️⃣ Pilih ID Unit/Kendaraan (atau ketik manual, contoh: JSM 211):",
        reply_markup=keyboard_unit("trace_unit"),
    )
    return UNIT_T


async def simpan_unit_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["unit"] = update.message.text.strip().upper()
    await _lanjut_personil1(update, context.user_data["unit"])
    return PERSONIL1


async def simpan_unit_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unit = nilai_callback(update.callback_query.data)
    context.user_data["unit"] = unit
    await _lanjut_personil1(update, unit)
    return PERSONIL1


async def simpan_personil1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["p1"] = update.message.text
    await update.message.reply_text("3️⃣ Masukkan nama Personil 2:")
    return PERSONIL2


async def simpan_personil2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["p2"] = update.message.text
    await update.message.reply_text(
        "4️⃣ Siapa nama MCSS? (Cukup ketik namanya saja, contoh: Bambang):"
    )
    return MCSS


async def simpan_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama_mcss = update.message.text.strip()

    if nama_mcss.lower().startswith("bpk.") or nama_mcss.lower().startswith("bpk "):
        context.user_data["mcss"] = nama_mcss
    else:
        context.user_data["mcss"] = f"Bpk. {nama_mcss}"

    await update.message.reply_text("5️⃣ Waktu Info Diterima? (Contoh: 14.15 WIB):")
    return TERIMA_INFO


async def simpan_terima_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["terima_info"] = update.message.text
    await update.message.reply_text("6️⃣ Waktu Sampai di Lokasi? (Contoh: 14.25 WIB):")
    return TIBA_LOKASI


async def simpan_tiba_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tiba_lokasi"] = update.message.text
    await update.message.reply_text("7️⃣ Lokasi Kejadian? (Contoh: KM 720 B):")
    return LOKASI_T


async def simpan_lokasi_t(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lokasi_t"] = update.message.text
    await _lanjut_shift(update)
    return SHIFT_T


async def simpan_shift_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["shift_t"] = update.message.text.strip()
    await update.message.reply_text("9️⃣ Jenis Kendaraan? (Contoh: Avanza):")
    return JENIS_K


async def simpan_shift_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    shift = nilai_callback(query.data)
    context.user_data["shift_t"] = shift
    await query.edit_message_text(
        f"✅ Shift: *{shift}*\n\n9️⃣ Jenis Kendaraan? (Contoh: Avanza):",
        parse_mode="Markdown",
    )
    return JENIS_K


async def simpan_jenis_k(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jenis_k"] = update.message.text
    await update.message.reply_text("🔟 Nomor Polisi / No Pol? (Contoh: L 1234 AB):")
    return NOPOL


async def simpan_nopol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nopol"] = update.message.text
    await update.message.reply_text(
        "1️⃣1️⃣ Kendala Kendaraan?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "trace_kendala",
            [
                ("🛞 Pecah Ban", "Pecah Ban"),
                ("🌡️ Overheat", "Overheat"),
                ("🔧 Mogok", "Mogok"),
                ("⛽ Bahan Bakar Habis", "Bahan Bakar Habis"),
            ],
            per_baris=2,
        ),
    )
    return KENDALA


async def simpan_kendala_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kendala"] = update.message.text
    await update.message.reply_text(
        "1️⃣2️⃣ Tindak Lanjut?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "trace_tindakan",
            [
                ("🚛 Panggil Derek", "dipanggilkan derek"),
                ("🛞 Ganti Ban", "ganti ban"),
                ("🚔 Ditolak Unit", "ditolak ke unit terdekat"),
            ],
            per_baris=1,
        ),
    )
    return TINDAKAN


async def simpan_kendala_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["kendala"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Kendala: *{context.user_data['kendala']}*\n\n"
        "1️⃣2️⃣ Tindak Lanjut?\nTap pilihan atau ketik manual:",
        parse_mode="Markdown",
        reply_markup=keyboard_pilihan(
            "trace_tindakan",
            [
                ("🚛 Panggil Derek", "dipanggilkan derek"),
                ("🛞 Ganti Ban", "ganti ban"),
                ("🚔 Ditolak Unit", "ditolak ke unit terdekat"),
            ],
            per_baris=1,
        ),
    )
    return TINDAKAN


async def simpan_tindakan_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tindakan"] = update.message.text
    await tampilkan_preview(update, _buat_pesan_trace(context.user_data), parse_mode="Markdown")
    return PREVIEW_T


async def simpan_tindakan_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["tindakan"] = nilai_callback(query.data)
    await query.message.reply_text(
        "📋 *CEK DULU YA:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{_buat_pesan_trace(context.user_data)}",
        parse_mode="Markdown",
        reply_markup=keyboard_preview(),
    )
    return PREVIEW_T


async def konfirmasi_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_preview(update, context, _buat_pesan_trace, parse_mode="Markdown")


async def cancel_trace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await cancel_laporan(update, "Pembuatan Laporan Trace dibatalkan. ❌")


trace_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("trace", mulai_trace)],
    states={
        UNIT_T: [
            CallbackQueryHandler(simpan_unit_tombol, pattern=r"^trace_unit:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_unit_teks),
        ],
        PERSONIL1: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil1)],
        PERSONIL2: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil2)],
        MCSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mcss)],
        TERIMA_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_terima_info)],
        TIBA_LOKASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_tiba_lokasi)],
        LOKASI_T: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi_t)],
        SHIFT_T: [
            CallbackQueryHandler(simpan_shift_tombol, pattern=r"^trace_shift:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift_teks),
        ],
        JENIS_K: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_jenis_k)],
        NOPOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_nopol)],
        KENDALA: [
            CallbackQueryHandler(simpan_kendala_tombol, pattern=r"^trace_kendala:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendala_teks),
        ],
        TINDAKAN: [
            CallbackQueryHandler(simpan_tindakan_tombol, pattern=r"^trace_tindakan:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_tindakan_teks),
        ],
        PREVIEW_T: [CallbackQueryHandler(konfirmasi_preview, pattern=r"^preview:")],
    },
    fallbacks=[CommandHandler("cancel", cancel_trace)],
)