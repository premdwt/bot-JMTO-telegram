import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# 1. Tentukan 6 Tahapan Pertanyaan untuk Pantauan
(KENDARAAN_P, POSISI_P, CUACA_P, LALIN_P, ODDO_P, GIAT_P) = range(6)

async def mulai_pantauan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👀 Siap! Mari buat Laporan Pantauan.\n\n"
        "1️⃣ ID Kendaraan? (Contoh: JSM 211):"
    )
    return KENDARAAN_P

async def simpan_kendaraan_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kendaraan_p'] = update.message.text
    await update.message.reply_text("2️⃣ 10.2 / Posisi saat ini? (Contoh: KM 714 A):")
    return POSISI_P

async def simpan_posisi_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['posisi_p'] = update.message.text
    await update.message.reply_text("3️⃣ 8.1.5 / Cuaca? (Contoh: Cerah / Mendung / Gerimis):")
    return CUACA_P

async def simpan_cuaca_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cuaca_p'] = update.message.text
    await update.message.reply_text("4️⃣ 8.1.9 / Situasi Lalin? (Contoh: Ramai Lancar / Sepi):")
    return LALIN_P

async def simpan_lalin_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lalin_p'] = update.message.text
    await update.message.reply_text("5️⃣ Posisi Oddo saat ini? (Contoh: 71350):")
    return ODDO_P

async def simpan_oddo_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oddo_p'] = update.message.text
    await update.message.reply_text("6️⃣ Giat saat ini? (Contoh: Standby / Patroli / Turlalin):")
    return GIAT_P

async def simpan_giat_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['giat_p'] = update.message.text
    
    # --- LOGIKA OTOMATIS UCAPAN WAKTU ---
    # Menentukan Pagi/Siang/Sore/Malam berdasarkan jam server saat laporan dibuat
    sekarang = datetime.datetime.now()
    jam = sekarang.hour
    
    if 4 <= jam < 11:
        ucapan_waktu = "Selamat Pagi"
    elif 11 <= jam < 15:
        ucapan_waktu = "Selamat Siang"
    elif 15 <= jam < 18:
        ucapan_waktu = "Selamat Sore"
    else:
        ucapan_waktu = "Selamat Malam"

    # --- CETAK HASIL AKHIR ---
    pesan_hasil = (
        f"{ucapan_waktu}\n"
        f"{context.user_data['kendaraan_p']}\n"
        "Mohon ijin melaporkan situasi & kondisi terkini :\n\n"
        f"10.2 : {context.user_data['posisi_p']}\n"
        f"8.1.5 : {context.user_data['cuaca_p']}\n"
        f"8.1.9 : {context.user_data['lalin_p']}\n"
        f"Oddo : {context.user_data['oddo_p']}\n"
        f"Giat : {context.user_data['giat_p']}\n\n"
        "Demikian yang dapat dilaporkan, Semoga Aman TKA.\n"
        "Terima Kasih 🙏"
    )
    
    await update.message.reply_text(pesan_hasil)
    return ConversationHandler.END

async def cancel_pantauan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pembuatan Laporan Pantauan dibatalkan. ❌")
    return ConversationHandler.END

# Daftarkan Conversation Handler untuk Pantauan
pantauan_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('pantauan', mulai_pantauan)],
    states={
        KENDARAAN_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendaraan_p)],
        POSISI_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_posisi_p)],
        CUACA_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_cuaca_p)],
        LALIN_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lalin_p)],
        ODDO_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_p)],
        GIAT_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_giat_p)],
    },
    fallbacks=[CommandHandler('cancel', cancel_pantauan)]
)