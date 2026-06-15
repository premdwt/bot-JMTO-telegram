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
    keyboard_shift,
    nilai_callback,
    tanggal_indo,
    tampilkan_preview,
)

(
    JENIS, SHIFT_LAKA, WAKTU_KEJADIAN, WAKTU_TIBA, LOKASI, PENYEBAB,
    KENDARAAN, KORBAN, CUACA, DAMPAK, SARANA, INFO_BAN, PREVIEW_L,
) = range(13)


def _parse_info_ban(teks: str) -> tuple[str, str, str, str, str]:
    info_ban = teks.split(",")
    if len(info_ban) >= 5:
        return (
            info_ban[0].strip(),
            info_ban[1].strip(),
            info_ban[2].strip(),
            info_ban[3].strip(),
            info_ban[4].strip(),
        )
    return teks, "-", "-", "-", "-"


def _buat_pesan_laka(user_data: dict) -> str:
    umur_ban, tekanan, kondisi, penyebab_ban, jenis = _parse_info_ban(
        user_data.get("info_ban_raw", "nihil, nihil, nihil, nihil, nihil")
    )

    return (
        "_*LAPORAN AWAL KEJADIAN*_\n\n"
        "Ruas : *Surabaya - Mojokerto*\n"
        f"Jenis Kecelakaan : 3-3 {user_data['jenis']}\n"
        f"Hari / Tanggal : {tanggal_indo(separator=' / ')}\n"
        f"Shift : {user_data['shift_laka']}\n"
        f"Waktu Kejadian : {user_data['waktu_kejadian']}\n"
        "Petugas Tiba di TKP :\n"
        f"- {user_data['waktu_tiba']}\n"
        f"Lokasi : {user_data['lokasi']}\n"
        f"Penyebab : {user_data['penyebab']}\n"
        "Kendaraan Terlibat :\n"
        f"{user_data['kendaraan']}\n"
        f"Korban : {user_data['korban']}\n"
        f"Cuaca : {user_data['cuaca']}\n"
        f"Dampak : {user_data['dampak']}\n"
        f"Sarana : {user_data['sarana']}\n\n"
        "Keterangan Ban >>\n"
        f"- Umur Ban : {umur_ban}\n"
        f"- Tekanan Ban : {tekanan}\n"
        f"- Kondisi Ban : {kondisi}\n"
        f"- Penyebab : {penyebab_ban}\n"
        f"- Jenis Ban : {jenis}"
    )


async def _lanjut_shift(update: Update):
    teks = "2️⃣ Pilih shift (atau ketik manual, contoh: 2):"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            teks, reply_markup=keyboard_shift("laka_shift")
        )
    else:
        await update.message.reply_text(
            teks, reply_markup=keyboard_shift("laka_shift")
        )


async def mulai_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Siap! Mari buat Laporan Awal Kejadian (Laka 33).\n\n"
        "1️⃣ Jenis Kecelakaan?\nTap pilihan atau ketik manual (M / L / K):",
        reply_markup=keyboard_pilihan(
            "laka_jenis",
            [("🚗 M", "M"), ("🏍️ L", "L"), ("🚛 K", "K")],
            per_baris=3,
        ),
    )
    return JENIS


async def simpan_jenis_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jenis"] = update.message.text.strip().upper()
    await _lanjut_shift(update)
    return SHIFT_LAKA


async def simpan_jenis_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jenis = nilai_callback(update.callback_query.data)
    context.user_data["jenis"] = jenis
    await _lanjut_shift(update)
    return SHIFT_LAKA


async def simpan_shift_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["shift_laka"] = update.message.text.strip()
    await update.message.reply_text("3️⃣ Waktu Kejadian? (Contoh: 09.30 WIB):")
    return WAKTU_KEJADIAN


async def simpan_shift_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    shift = nilai_callback(query.data)
    context.user_data["shift_laka"] = shift
    await query.edit_message_text(
        f"✅ Shift: *{shift}*\n\n3️⃣ Waktu Kejadian? (Contoh: 09.30 WIB):",
        parse_mode="Markdown",
    )
    return WAKTU_KEJADIAN


async def simpan_waktu_kejadian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waktu_kejadian"] = update.message.text
    await update.message.reply_text(
        "4️⃣ Petugas Tiba di TKP? (Contoh: 10.10 WIB (JSM 211)):"
    )
    return WAKTU_TIBA


async def simpan_waktu_tiba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waktu_tiba"] = update.message.text
    await update.message.reply_text("5️⃣ Lokasi Kejadian? (Contoh: KM 70 A di Bahu Luar):")
    return LOKASI


async def simpan_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lokasi"] = update.message.text
    await update.message.reply_text(
        "6️⃣ Penyebab Kecelakaan?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "laka_penyebab",
            [
                ("😴 Mengantuk", "Mengantuk"),
                ("🛞 Pecah Ban", "Pecah Ban"),
                ("💥 Tabrak Belakang", "Tabrak Belakang"),
                ("🌧️ Jalan Licin", "Jalan Licin"),
            ],
            per_baris=2,
        ),
    )
    return PENYEBAB


async def simpan_penyebab_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["penyebab"] = update.message.text
    await update.message.reply_text(
        "7️⃣ Data Kendaraan Terlibat?\n"
        "(Jika lebih dari 1, pisahkan dengan Enter / Baris Baru.\n"
        "Contoh:\nKendaraan 1: Avanza B 1234 CD\nKendaraan 2: Truk L 9876 AZ)"
    )
    return KENDARAAN


async def simpan_penyebab_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["penyebab"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Penyebab: *{context.user_data['penyebab']}*\n\n"
        "7️⃣ Data Kendaraan Terlibat?\n"
        "(Jika lebih dari 1, pisahkan dengan Enter / Baris Baru.)",
        parse_mode="Markdown",
    )
    return KENDARAAN


async def simpan_kendaraan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kendaraan"] = update.message.text
    await update.message.reply_text(
        "8️⃣ Korban?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "laka_korban",
            [("✅ Nihil", "Nihil"), ("🩹 1 LR", "1 LR"), ("🚑 1 Berat", "1 Berat")],
            per_baris=3,
        ),
    )
    return KORBAN


async def simpan_korban_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["korban"] = update.message.text
    await update.message.reply_text(
        "9️⃣ Cuaca saat kejadian?\nTap pilihan atau ketik manual:",
        reply_markup=keyboard_pilihan(
            "laka_cuaca",
            [("☀️ Cerah", "Cerah"), ("🌧️ Hujan", "Hujan"), ("🌥️ Mendung", "Mendung")],
            per_baris=3,
        ),
    )
    return CUACA


async def simpan_korban_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["korban"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Korban: *{context.user_data['korban']}*\n\n"
        "9️⃣ Cuaca saat kejadian?\nTap pilihan atau ketik manual:",
        parse_mode="Markdown",
        reply_markup=keyboard_pilihan(
            "laka_cuaca",
            [("☀️ Cerah", "Cerah"), ("🌧️ Hujan", "Hujan"), ("🌥️ Mendung", "Mendung")],
            per_baris=3,
        ),
    )
    return CUACA


async def simpan_cuaca_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cuaca"] = update.message.text
    await update.message.reply_text("🔟 Dampak? (Contoh: Penutupan Bahu Luar / L1):")
    return DAMPAK


async def simpan_cuaca_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cuaca"] = nilai_callback(query.data)
    await query.edit_message_text(
        f"✅ Cuaca: *{context.user_data['cuaca']}*\n\n"
        "🔟 Dampak? (Contoh: Penutupan Bahu Luar / L1):",
        parse_mode="Markdown",
    )
    return DAMPAK


async def simpan_dampak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dampak"] = update.message.text
    await update.message.reply_text(
        "1️⃣1️⃣ Sarana yang terlibat? (Contoh: JSM 211, Derek, Medis):"
    )
    return SARANA


async def simpan_sarana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sarana"] = update.message.text
    await update.message.reply_text(
        "1️⃣2️⃣ Keterangan Ban?\n"
        "Tap *Nihil* jika tidak ada info ban, atau ketik manual.\n"
        "(Format manual: Umur, Tekanan, Kondisi, Penyebab, Jenis)\n\n"
        "Contoh: 2 Tahun, 35 psi, Aus, Tertusuk Benda Tajam, Tubeless",
        parse_mode="Markdown",
        reply_markup=keyboard_pilihan(
            "laka_ban",
            [("➖ Nihil (tidak ada info)", "nihil, nihil, nihil, nihil, nihil")],
            per_baris=1,
        ),
    )
    return INFO_BAN


async def _tampilkan_preview_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tampilkan_preview(update, _buat_pesan_laka(context.user_data))


async def simpan_info_ban_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["info_ban_raw"] = update.message.text
    await _tampilkan_preview_laka(update, context)
    return PREVIEW_L


async def simpan_info_ban_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["info_ban_raw"] = nilai_callback(query.data)
    await query.message.reply_text(
        "📋 *CEK DULU YA:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{_buat_pesan_laka(context.user_data)}",
        reply_markup=keyboard_preview(),
    )
    return PREVIEW_L


async def konfirmasi_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_preview(update, context, _buat_pesan_laka)


async def cancel_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await cancel_laporan(update, "Pembuatan Laporan Laka dibatalkan. ❌")


laka_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("laka", mulai_laka)],
    states={
        JENIS: [
            CallbackQueryHandler(simpan_jenis_tombol, pattern=r"^laka_jenis:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_jenis_teks),
        ],
        SHIFT_LAKA: [
            CallbackQueryHandler(simpan_shift_tombol, pattern=r"^laka_shift:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift_teks),
        ],
        WAKTU_KEJADIAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_waktu_kejadian)],
        WAKTU_TIBA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_waktu_tiba)],
        LOKASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi)],
        PENYEBAB: [
            CallbackQueryHandler(simpan_penyebab_tombol, pattern=r"^laka_penyebab:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_penyebab_teks),
        ],
        KENDARAAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendaraan)],
        KORBAN: [
            CallbackQueryHandler(simpan_korban_tombol, pattern=r"^laka_korban:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_korban_teks),
        ],
        CUACA: [
            CallbackQueryHandler(simpan_cuaca_tombol, pattern=r"^laka_cuaca:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_cuaca_teks),
        ],
        DAMPAK: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_dampak)],
        SARANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_sarana)],
        INFO_BAN: [
            CallbackQueryHandler(simpan_info_ban_tombol, pattern=r"^laka_ban:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_info_ban_teks),
        ],
        PREVIEW_L: [CallbackQueryHandler(konfirmasi_preview, pattern=r"^preview:")],
    },
    fallbacks=[CommandHandler("cancel", cancel_laka)],
)