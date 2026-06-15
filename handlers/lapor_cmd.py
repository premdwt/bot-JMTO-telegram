import datetime
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

WIB = ZoneInfo("Asia/Jakarta")

MOBIL, SHIFT, PERSONIL, RC, RAMBU, KONDISI, ODDO_AWAL, ODDO_AKHIR, ODDO_KONFIRMASI, PENANGANAN, ESTAFET, PREVIEW = range(12)


def _keyboard_mobil():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚔 JSM 211", callback_data="mobil:JSM 211"),
            InlineKeyboardButton("🚔 JSM 212", callback_data="mobil:JSM 212"),
        ],
    ])


def _keyboard_shift():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("☀️ Shift 1", callback_data="shift:1"),
            InlineKeyboardButton("🌤️ Shift 2", callback_data="shift:2"),
            InlineKeyboardButton("🌙 Shift 3", callback_data="shift:3"),
        ],
    ])


def _keyboard_kondisi():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Semua Baik (default)", callback_data="kondisi:baik")],
    ])


def _keyboard_preview():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Kirim Laporan", callback_data="preview:kirim"),
            InlineKeyboardButton("❌ Batal", callback_data="preview:batal"),
        ],
    ])


def _keyboard_oddo_konfirmasi():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ya, lanjut", callback_data="oddo:lanjut"),
            InlineKeyboardButton("🔄 Ulang Oddo Akhir", callback_data="oddo:ulang"),
        ],
    ])


def _tanggal_indo():
    now = datetime.datetime.now(WIB)
    hari_dict = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu",
    }
    bulan_dict = {
        "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
        "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
        "09": "September", "10": "Oktober", "11": "November", "12": "Desember",
    }
    hari = hari_dict[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = bulan_dict[now.strftime("%m")]
    tahun = now.strftime("%Y")
    return f"{hari} , {tanggal} {bulan} {tahun}"


def _set_kondisi_baik(context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rotator"] = "Baik"
    context.user_data["ban"] = "Baik"
    context.user_data["body"] = "Baik"
    context.user_data["sirine"] = "Baik"
    context.user_data["radio"] = "Aman"


def _buat_pesan_laporan(user_data: dict) -> str:
    try:
        oddo_awal = int(user_data["oddo_awal"])
        oddo_akhir = int(user_data["oddo_akhir"])

        if oddo_akhir == 0:
            jumlah_oddo = 0
            status_tugas = "awal tugas"
        else:
            jumlah_oddo = oddo_akhir - oddo_awal
            status_tugas = "akhir tugas"
    except ValueError:
        jumlah_oddo = "Error (Input selain angka)"
        status_tugas = "akhir tugas"

    tanggal_indo = _tanggal_indo()
    personil_list = user_data["personil"].split(",")
    personil_format = "\n".join([f"▪️{p.strip()}" for p in personil_list])

    return (
        f"Mohon ijin *melaporkan serah terima {status_tugas}* :\n\n"
        f"🚔 {user_data['mobil']}\n"
        f"📆 {tanggal_indo}\n"
        f"🕕 Shift {user_data['shift']}\n"
        f"Personil :\n{personil_format}\n\n"
        f"Jumlah RC :  {user_data['rc']}\n"
        f"Jumlah Rambu : {user_data['rambu']}\n"
        f"Rotator & Lampu : {user_data['rotator']}\n"
        f"Ban : {user_data['ban']}\n"
        f"Kondisi Body : {user_data['body']}\n"
        f"Sirine : {user_data['sirine']}\n"
        f"Radio Komunikasi : {user_data['radio']}\n"
        f"Oddo Awal : {user_data['oddo_awal']}\n"
        f"Oddo Akhir : {user_data['oddo_akhir']}\n"
        f"Jumlah Oddo : {jumlah_oddo}\n"
        f"Jumlah Penanganan : {user_data['penanganan']}\n"
        f"Estafet : {user_data['estafet']}\n\n"
        f"Semoga tetap Aman TKA sampai serah terima {status_tugas} 🤲🏻"
    )


async def _kirim_pilih_shift(update: Update, mobil: str):
    text = (
        f"✅ Kendaraan: *{mobil}*\n\n"
        "2️⃣ Pilih shift (atau ketik manual, contoh: 2):"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=_keyboard_shift()
        )
    else:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=_keyboard_shift()
        )


async def _kirim_tanya_personil(update: Update, shift: str):
    text = (
        f"✅ Shift: *{shift}*\n\n"
        "3️⃣ Siapa saja personilnya? (Pisahkan dengan koma. Contoh: Ade, amirul):"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def mulai_lapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Siap laksanakan! 📝\n\n"
        "1️⃣ Pilih ID Kendaraan (atau ketik manual, contoh: JSM 211):",
        reply_markup=_keyboard_mobil(),
    )
    return MOBIL


async def simpan_mobil_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mobil"] = update.message.text.strip()
    await _kirim_pilih_shift(update, context.user_data["mobil"])
    return SHIFT


async def simpan_mobil_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobil = update.callback_query.data.split(":", 1)[1]
    context.user_data["mobil"] = mobil
    await _kirim_pilih_shift(update, mobil)
    return SHIFT


async def simpan_shift_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["shift"] = update.message.text.strip()
    await _kirim_tanya_personil(update, context.user_data["shift"])
    return PERSONIL


async def simpan_shift_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shift = update.callback_query.data.split(":", 1)[1]
    context.user_data["shift"] = shift
    await _kirim_tanya_personil(update, shift)
    return PERSONIL


async def simpan_personil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["personil"] = update.message.text
    await update.message.reply_text("4️⃣ Berapa Jumlah RC?:")
    return RC


async def simpan_rc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rc"] = update.message.text
    await update.message.reply_text("5️⃣ Berapa Jumlah Rambu?:")
    return RAMBU


async def simpan_rambu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rambu"] = update.message.text
    await update.message.reply_text(
        "6️⃣ Bagaimana Kondisi Kendaraan?\n"
        "Tap *Semua Baik* untuk default, atau ketik manual.\n"
        "(Urutan manual: Rotator/Lampu, Ban, Body, Sirine, Radio)\n\n"
        "Contoh: baik, Baik, Baik, menyala baik, aman",
        parse_mode="Markdown",
        reply_markup=_keyboard_kondisi(),
    )
    return KONDISI


async def simpan_kondisi_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _set_kondisi_baik(context)
    await query.edit_message_text(
        "✅ Kondisi: Semua Baik\n\n7️⃣ Masukkan angka Oddo Awal:"
    )
    return ODDO_AWAL


async def simpan_kondisi_teks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kondisi = update.message.text.split(",")

    if len(kondisi) >= 5:
        context.user_data["rotator"] = kondisi[0].strip()
        context.user_data["ban"] = kondisi[1].strip()
        context.user_data["body"] = kondisi[2].strip()
        context.user_data["sirine"] = kondisi[3].strip()
        context.user_data["radio"] = kondisi[4].strip()
    else:
        context.user_data["rotator"] = update.message.text
        context.user_data["ban"] = "Baik"
        context.user_data["body"] = "Baik"
        context.user_data["sirine"] = "Baik"
        context.user_data["radio"] = "Aman"

    await update.message.reply_text("7️⃣ Masukkan angka Oddo Awal:")
    return ODDO_AWAL


async def simpan_oddo_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    if not teks.isdigit():
        await update.message.reply_text("❌ Oddo awal harus angka. Coba lagi:")
        return ODDO_AWAL

    context.user_data["oddo_awal"] = teks
    await update.message.reply_text(
        "8️⃣ Masukkan angka Oddo Akhir (Ketik 0 jika ini Laporan Awal):"
    )
    return ODDO_AKHIR


async def _lanjut_penanganan(update: Update):
    teks = "9️⃣ Berapa Jumlah Penanganan?:"
    if update.callback_query:
        await update.callback_query.edit_message_text(teks)
    else:
        await update.message.reply_text(teks)


async def simpan_oddo_akhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    if not teks.isdigit():
        await update.message.reply_text("❌ Oddo akhir harus angka. Coba lagi:")
        return ODDO_AKHIR

    context.user_data["oddo_akhir"] = teks

    try:
        awal = int(context.user_data["oddo_awal"])
        akhir = int(teks)
        if akhir != 0 and akhir < awal:
            await update.message.reply_text(
                f"⚠️ Oddo akhir ({akhir}) lebih kecil dari awal ({awal}). Yakin lanjut?",
                reply_markup=_keyboard_oddo_konfirmasi(),
            )
            return ODDO_KONFIRMASI
    except ValueError:
        pass

    await _lanjut_penanganan(update)
    return PENANGANAN


async def konfirmasi_oddo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "oddo:ulang":
        await query.edit_message_text(
            "8️⃣ Masukkan angka Oddo Akhir (Ketik 0 jika ini Laporan Awal):"
        )
        return ODDO_AKHIR

    await query.edit_message_text("9️⃣ Berapa Jumlah Penanganan?:")
    return PENANGANAN


async def simpan_penanganan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["penanganan"] = update.message.text
    await update.message.reply_text("🔟 Status Estafet? (Contoh: nihil):")
    return ESTAFET


async def simpan_estafet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["estafet"] = update.message.text
    pesan = _buat_pesan_laporan(context.user_data)

    await update.message.reply_text(
        "📋 *CEK DULU YA:*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{pesan}",
        parse_mode="Markdown",
        reply_markup=_keyboard_preview(),
    )
    return PREVIEW


async def handle_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "preview:batal":
        await query.edit_message_text("Pengisian laporan dibatalkan. ❌")
        return ConversationHandler.END

    pesan = _buat_pesan_laporan(context.user_data)
    await query.edit_message_text(pesan, parse_mode="Markdown")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Pengisian laporan dibatalkan. ❌")
    else:
        await update.message.reply_text("Pengisian laporan dibatalkan. ❌")
    return ConversationHandler.END


lapor_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("lapor", mulai_lapor)],
    states={
        MOBIL: [
            CallbackQueryHandler(simpan_mobil_tombol, pattern=r"^mobil:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mobil_teks),
        ],
        SHIFT: [
            CallbackQueryHandler(simpan_shift_tombol, pattern=r"^shift:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift_teks),
        ],
        PERSONIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil)],
        RC: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_rc)],
        RAMBU: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_rambu)],
        KONDISI: [
            CallbackQueryHandler(simpan_kondisi_tombol, pattern=r"^kondisi:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kondisi_teks),
        ],
        ODDO_AWAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_awal)],
        ODDO_AKHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_akhir)],
        ODDO_KONFIRMASI: [
            CallbackQueryHandler(konfirmasi_oddo, pattern=r"^oddo:"),
        ],
        PENANGANAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_penanganan)],
        ESTAFET: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_estafet)],
        PREVIEW: [CallbackQueryHandler(handle_preview, pattern=r"^preview:")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)