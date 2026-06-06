import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Tentukan 12 Tahapan Pertanyaan untuk Trace (Nambah UNIT)
(UNIT_T, PERSONIL1, PERSONIL2, MCSS, TERIMA_INFO, TIBA_LOKASI, LOKASI_T, SHIFT_T, JENIS_K, NOPOL, KENDALA, TINDAKAN) = range(12)

async def mulai_trace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ Siap! Mari buat Laporan Penanganan Kendala (Trace).\n\n1️⃣ Masukkan ID Unit/Kendaraan (Contoh: JSM 211):")
    return UNIT_T

async def simpan_unit_t(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['unit'] = update.message.text.upper() # Otomatis dibikin huruf besar
    await update.message.reply_text("2️⃣ Masukkan nama Personil 1:")
    return PERSONIL1

async def simpan_personil1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p1'] = update.message.text
    await update.message.reply_text("3️⃣ Masukkan nama Personil 2:")
    return PERSONIL2

async def simpan_personil2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p2'] = update.message.text
    await update.message.reply_text("4️⃣ Siapa nama MCSS? (Cukup ketik namanya saja, contoh: Bambang):")
    return MCSS

async def simpan_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama_mcss = update.message.text
    
    # Proteksi biar gak "Bpk. Bpk. Bambang"
    if nama_mcss.lower().startswith("bpk.") or nama_mcss.lower().startswith("bpk "):
        context.user_data['mcss'] = nama_mcss
    else:
        context.user_data['mcss'] = f"Bpk. {nama_mcss}"
        
    await update.message.reply_text("5️⃣ Waktu Info Diterima? (Contoh: 14.15 WIB):")
    return TERIMA_INFO

async def simpan_terima_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['terima_info'] = update.message.text
    await update.message.reply_text("6️⃣ Waktu Sampai di Lokasi? (Contoh: 14.25 WIB):")
    return TIBA_LOKASI

async def simpan_tiba_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tiba_lokasi'] = update.message.text
    await update.message.reply_text("7️⃣ Lokasi Kejadian? (Contoh: KM 720 B):")
    return LOKASI_T

async def simpan_lokasi_t(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lokasi_t'] = update.message.text
    await update.message.reply_text("8️⃣ Shift berapa? (1 / 2 / 3):")
    return SHIFT_T

async def simpan_shift_t(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['shift_t'] = update.message.text
    await update.message.reply_text("9️⃣ Jenis Kendaraan? (Contoh: Avanza):")
    return JENIS_K

async def simpan_jenis_k(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['jenis_k'] = update.message.text
    await update.message.reply_text("🔟 Nomor Polisi / No Pol? (Contoh: L 1234 AB):")
    return NOPOL

async def simpan_nopol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nopol'] = update.message.text
    await update.message.reply_text("1️⃣1️⃣ Kendala Kendaraan? (Contoh: Pecah Ban / Overheat):")
    return KENDALA

async def simpan_kendala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kendala'] = update.message.text
    await update.message.reply_text("1️⃣2️⃣ Tindak Lanjut? (Contoh: di panggilkan derek):")
    return TINDAKAN

async def simpan_tindakan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tindakan'] = update.message.text
    
    # --- PROSES TANGGAL OTOMATIS ---
    now = datetime.datetime.now()
    hari_dict = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jum at", "Saturday": "Sabtu", "Sunday": "Minggu"}
    bulan_dict = {"01": "Januari", "02": "Februari", "03": "Maret", "04": "April", "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus", "09": "September", "10": "Oktober", "11": "November", "12": "Desember"}
    
    hari = hari_dict[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = bulan_dict[now.strftime("%m")]
    tahun = now.strftime("%Y")
    
    # --- CETAK HASIL AKHIR (Ganti _ dengan karakter garis solid ━) ---
    pesan_hasil = (
        "*LAPORAN MCS RUAS SUMO*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"{context.user_data['unit']}\n\n"
        f"1. {context.user_data['p1']}\n"
        f"2. {context.user_data['p2']}\n\n"
        f"MCSS : {context.user_data['mcss']}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"Hari : {hari}\n"
        f"Tanggal : {tanggal} {bulan} {tahun}\n"
        f"Info diterima : {context.user_data['terima_info']}\n"
        f"Sampai dilokasi : {context.user_data['tiba_lokasi']}\n"
        f"Lokasi : {context.user_data['lokasi_t']}\n"
        f"Shift : {context.user_data['shift_t']}\n\n"
        f"GIAT {context.user_data['unit']}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        "Mohon ijin melaporkan 1 kendaraan >> \n"
        f"Jenis : {context.user_data['jenis_k']}\n"
        f"No Pol : {context.user_data['nopol']}\n"
        f"Kendala : {context.user_data['kendala']}\n\n"
        "TINDAK LANJUT\n"
        "━━━━━━━━━━━━━━━━━\n"
        f"{context.user_data['tindakan']}\n\n"
        "Demikian yang dapat dilaporkan.\n"
        "Terima Kasih 🙏🏼"
    )
    
    await update.message.reply_text(pesan_hasil, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_trace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pembuatan Laporan Trace dibatalkan. ❌")
    return ConversationHandler.END

trace_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('trace', mulai_trace)],
    states={
        UNIT_T: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_unit_t)],
        PERSONIL1: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil1)],
        PERSONIL2: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil2)],
        MCSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mcss)],
        TERIMA_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_terima_info)],
        TIBA_LOKASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_tiba_lokasi)],
        LOKASI_T: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi_t)],
        SHIFT_T: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift_t)],
        JENIS_K: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_jenis_k)],
        NOPOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_nopol)],
        KENDALA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendala)],
        TINDAKAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_tindakan)],
    },
    fallbacks=[CommandHandler('cancel', cancel_trace)]
)