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
    escape_markdown,
    handle_preview,
    keyboard_pilihan,
    keyboard_preview,
    keyboard_unit,
    nilai_callback,
    tampilkan_preview,
)

UNIT_G, PERSONIL1_G, PERSONIL2_G, MCSS_G, LOKASI_G, GIAT_G, PREVIEW_G = range(7)


def _buat_pesan_giat(user_data: dict) -> str:
    return (
        "*LAPORAN MCS RUAS SUMO*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"{escape_markdown(user_data.get('unit', '-'))}\n\n"
        f"1. {escape_markdown(user_data.get('p1', '-'))}\n"
        f"2. {escape_markdown(user_data.get('p2', '-'))}\n\n"
        f"MCSS : {escape_markdown(user_data.get('mcss', '-'))}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"GIAT {escape_markdown(user_data.get('unit', '-'))}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"Lokasi : {escape_markdown(user_data.get('lokasi_g', '-'))}\n"
        f"Giat : {escape_markdown(user_data.get('giat_g', '-'))}\n\n"
        "Demikian yang dapat dilaporkan.\n"
        "Terima Kasih 🙏🏼"
    )


async def _lanjut_personil1(update: Update, unit: str):
    teks = (
        f"✅ Unit: *{unit}*\n\n"
        "2️⃣ Masukkan nama Personil 1:"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(teks, parse_mode="Markdown")
    else:
        await update.message.reply_text(teks, parse_mode="Markdown")


async def mulai_giat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚧 Siap! Mari buat Laporan Giat / Penanganan Biasa.\n\n"
        "1️⃣ Pilih ID Unit/Kendaraan (atau ketik manual, contoh: JSM 211):",
        reply_markup=keyboard_unit("giat_unit"),
    )
    return UNIT_G


async def simpan_unit_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["unit"] = update.message.text.strip().upper()
    await _lanjut_personil1(update, context.user_data["unit"])
    return PERSONIL1_G


async def simpan_unit_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unit = nilai_callback(update.callback_query.data)
    context.user_data["unit"] = unit
    await _lanjut_personil1(update, unit)
    return PERSONIL1_G


async def simpan_personil1_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["p1"] = update.message.text
    await update.message.reply_text("3️⃣ Masukkan nama Personil 2:")
    return PERSONIL2_G


async def simpan_personil2_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["p2"] = update.message.text
    await update.message.reply_text(
        "4️⃣ Siapa nama MCSS? (Cukup ketik namanya saja, contoh: Bambang):"
    )
    return MCSS_G


async def simpan_mcss_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama_mcss = update.message.text.strip()

    if nama_mcss.lower().startswith("bpk.") or nama_mcss.lower().startswith("bpk "):
        context.user_data["mcss"] = nama_mcss
    else:
        context.user_data["mcss"] = f"Bpk. {nama_mcss}"

    await update.message.reply_text("5️⃣ Lokasi? (Contoh: KM 714 A / Bahu Luar):")
    return LOKASI_G


async def simpan_lokasi_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lokasi_g"] = update.message.text
    await update.message.reply_text(
        "6️⃣ Giat yang dilakukan?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "giat_jenis",
            [
                ("🚔 Patroli Rutin", "Patroli rutin"),
                ("🛑 Standby", "Standby"),
                ("🧹 Pembersihan Lajur", "Pembersihan lajur"),
            ],
            per_baris=1,
        ),
    )
    return GIAT_G


async def _tampilkan_preview_giat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tampilkan_preview(update, _buat_pesan_giat(context.user_data), parse_mode="Markdown")


async def simpan_giat_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["giat_g"] = update.message.text
    await _tampilkan_preview_giat(update, context)
    return PREVIEW_G


async def simpan_giat_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["giat_g"] = nilai_callback(query.data)
    await query.message.reply_text(
        "📋 *CEK DULU YA:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{_buat_pesan_giat(context.user_data)}",
        parse_mode="Markdown",
        reply_markup=keyboard_preview(),
    )
    return PREVIEW_G


async def konfirmasi_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_preview(update, context, _buat_pesan_giat, parse_mode="Markdown")


async def cancel_giat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await cancel_laporan(update, "Pembuatan Laporan Giat dibatalkan. ❌")


giat_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("giat", mulai_giat)],
    states={
        UNIT_G: [
            CallbackQueryHandler(simpan_unit_tombol, pattern=r"^giat_unit:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_unit_teks),
        ],
        PERSONIL1_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil1_g)],
        PERSONIL2_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil2_g)],
        MCSS_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mcss_g)],
        LOKASI_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi_g)],
        GIAT_G: [
            CallbackQueryHandler(simpan_giat_tombol, pattern=r"^giat_jenis:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_giat_teks),
        ],
        PREVIEW_G: [CallbackQueryHandler(konfirmasi_preview, pattern=r"^preview:")],
    },
    fallbacks=[CommandHandler("cancel", cancel_giat)],
)