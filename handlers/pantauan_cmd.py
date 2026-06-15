from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.report_helpers import (
    cancel_laporan,
    handle_preview,
    keyboard_pilihan,
    keyboard_preview,
    keyboard_unit,
    nilai_callback,
    tampilkan_preview,
    ucapan_waktu,
)

KENDARAAN_P, POSISI_P, CUACA_P, LALIN_P, ODDO_P, GIAT_P, PREVIEW_P = range(7)


def _buat_pesan_pantauan(user_data: dict) -> str:
    return (
        f"{ucapan_waktu()}\n"
        f"{user_data['kendaraan_p']}\n"
        "Mohon ijin melaporkan situasi & kondisi terkini :\n\n"
        f"10.2 : {user_data['posisi_p']}\n"
        f"8.1.5 : {user_data['cuaca_p']}\n"
        f"8.1.9 : {user_data['lalin_p']}\n"
        f"Oddo : {user_data['oddo_p']}\n"
        f"Giat : {user_data['giat_p']}\n\n"
        "Demikian yang dapat dilaporkan, Semoga Aman TKA.\n"
        "Terima Kasih 🙏"
    )


async def mulai_pantauan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👀 Siap! Mari buat Laporan Pantauan.\n\n"
        "1️⃣ Pilih ID Kendaraan (atau ketik manual, contoh: JSM 211):",
        reply_markup=keyboard_unit("pant_unit"),
    )
    return KENDARAAN_P


async def simpan_kendaraan_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kendaraan_p"] = update.message.text.strip()
    await update.message.reply_text("2️⃣ 10.2 / Posisi saat ini? (Contoh: KM 714 A):")
    return POSISI_P


async def simpan_kendaraan_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kendaraan = nilai_callback(query.data)
    context.user_data["kendaraan_p"] = kendaraan
    await query.edit_message_text(
        f"✅ Kendaraan: *{kendaraan}*\n\n2️⃣ 10.2 / Posisi saat ini? (Contoh: KM 714 A):",
        parse_mode="Markdown",
    )
    return POSISI_P


async def simpan_posisi_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["posisi_p"] = update.message.text
    await update.message.reply_text(
        "3️⃣ 8.1.5 / Cuaca?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "pant_cuaca",
            [("☀️ Cerah", "Cerah"), ("🌥️ Mendung", "Mendung"), ("🌦️ Gerimis", "Gerimis"), ("🌧️ Hujan", "Hujan")],
        ),
    )
    return CUACA_P


async def simpan_cuaca_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cuaca_p"] = update.message.text
    await update.message.reply_text(
        "4️⃣ 8.1.9 / Situasi Lalin?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "pant_lalin",
            [("🚗 Ramai Lancar", "Ramai Lancar"), ("😴 Sepi", "Sepi"), ("🐢 Padat", "Padat")],
            per_baris=1,
        ),
    )
    return LALIN_P


async def simpan_cuaca_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cuaca_p"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Cuaca: *{context.user_data['cuaca_p']}*\n\n"
        "4️⃣ 8.1.9 / Situasi Lalin?\nTap pilihan atau ketik manual:",
        parse_mode="Markdown",
        reply_markup=keyboard_pilihan(
            "pant_lalin",
            [("🚗 Ramai Lancar", "Ramai Lancar"), ("😴 Sepi", "Sepi"), ("🐢 Padat", "Padat")],
            per_baris=1,
        ),
    )
    return LALIN_P


async def simpan_lalin_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lalin_p"] = update.message.text
    await update.message.reply_text("5️⃣ Posisi Oddo saat ini? (Contoh: 71350):")
    return ODDO_P


async def simpan_lalin_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["lalin_p"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Lalin: *{context.user_data['lalin_p']}*\n\n5️⃣ Posisi Oddo saat ini? (Contoh: 71350):",
        parse_mode="Markdown",
    )
    return ODDO_P


async def simpan_oddo_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    if not teks.isdigit():
        await update.message.reply_text("❌ Oddo harus angka. Coba lagi:")
        return ODDO_P

    context.user_data["oddo_p"] = teks
    await update.message.reply_text(
        "6️⃣ Giat saat ini?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "pant_giat",
            [("🛑 Standby", "Standby"), ("🚔 Patroli", "Patroli"), ("🚦 Turlalin", "Turlalin")],
            per_baris=1,
        ),
    )
    return GIAT_P


async def simpan_giat_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["giat_p"] = update.message.text
    await tampilkan_preview(update, _buat_pesan_pantauan(context.user_data))
    return PREVIEW_P


async def simpan_giat_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["giat_p"] = nilai_callback(query.data)
    await query.message.reply_text(
        "📋 *CEK DULU YA:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{_buat_pesan_pantauan(context.user_data)}",
        parse_mode="Markdown",
        reply_markup=keyboard_preview(),
    )
    return PREVIEW_P


async def konfirmasi_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_preview(update, context, _buat_pesan_pantauan)


async def cancel_pantauan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await cancel_laporan(update, "Pembuatan Laporan Pantauan dibatalkan. ❌")


pantauan_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("pantauan", mulai_pantauan)],
    states={
        KENDARAAN_P: [
            CallbackQueryHandler(simpan_kendaraan_tombol, pattern=r"^pant_unit:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendaraan_teks),
        ],
        POSISI_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_posisi_p)],
        CUACA_P: [
            CallbackQueryHandler(simpan_cuaca_tombol, pattern=r"^pant_cuaca:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_cuaca_teks),
        ],
        LALIN_P: [
            CallbackQueryHandler(simpan_lalin_tombol, pattern=r"^pant_lalin:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lalin_teks),
        ],
        ODDO_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_p)],
        GIAT_P: [
            CallbackQueryHandler(simpan_giat_tombol, pattern=r"^pant_giat:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_giat_teks),
        ],
        PREVIEW_P: [CallbackQueryHandler(konfirmasi_preview, pattern=r"^preview:")],
    },
    fallbacks=[CommandHandler("cancel", cancel_pantauan)],
)