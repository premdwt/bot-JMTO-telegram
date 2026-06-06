import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# 1. Tentukan 12 Tahapan Pertanyaan untuk Laporan Laka
(JENIS, SHIFT_LAKA, WAKTU_KEJADIAN, WAKTU_TIBA, LOKASI, PENYEBAB, 
 KENDARAAN, KORBAN, CUACA, DAMPAK, SARANA, INFO_BAN) = range(12)

async def mulai_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 Siap! Mari buat Laporan Awal Kejadian (Laka 33).\n\n"
        "1️⃣ Jenis Kecelakaan? (Contoh: M / L / K):"
    )
    return JENIS

async def simpan_jenis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['jenis'] = update.message.text
    await update.message.reply_text("2️⃣ Shift berapa? (1 / 2 / 3):")
    return SHIFT_LAKA

async def simpan_shift_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['shift_laka'] = update.message.text
    await update.message.reply_text("3️⃣ Waktu Kejadian? (Contoh: 09.30 WIB):")
    return WAKTU_KEJADIAN

async def simpan_waktu_kejadian(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waktu_kejadian'] = update.message.text
    await update.message.reply_text("4️⃣ Petugas Tiba di TKP? (Contoh: 10.10 WIB (JSM 211)):")
    return WAKTU_TIBA

async def simpan_waktu_tiba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waktu_tiba'] = update.message.text
    await update.message.reply_text("5️⃣ Lokasi Kejadian? (Contoh: KM 70 A di Bahu Luar):")
    return LOKASI

async def simpan_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lokasi'] = update.message.text
    await update.message.reply_text("6️⃣ Penyebab Kecelakaan? (Contoh: Mengantuk / Pecah Ban):")
    return PENYEBAB

async def simpan_penyebab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['penyebab'] = update.message.text
    await update.message.reply_text(
        "7️⃣ Data Kendaraan Terlibat?\n"
        "(Jika lebih dari 1, pisahkan dengan Enter / Baris Baru.\n"
        "Contoh:\nKendaraan 1: Avanza B 1234 CD\nKendaraan 2: Truk L 9876 AZ)"
    )
    return KENDARAAN

async def simpan_kendaraan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kendaraan'] = update.message.text
    await update.message.reply_text("8️⃣ Korban? (Contoh: 1 LR / Nihil):")
    return KORBAN

async def simpan_korban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['korban'] = update.message.text
    await update.message.reply_text("9️⃣ Cuaca saat kejadian? (Contoh: Cerah / Hujan):")
    return CUACA

async def simpan_cuaca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cuaca'] = update.message.text
    await update.message.reply_text("🔟 Dampak? (Contoh: Penutupan Bahu Luar / L1):")
    return DAMPAK

async def simpan_dampak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dampak'] = update.message.text
    await update.message.reply_text("1️⃣1️⃣ Sarana yang terlibat? (Contoh: JSM 211, Derek, Medis):")
    return SARANA

async def simpan_sarana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sarana'] = update.message.text
    await update.message.reply_text(
        "1️⃣2️⃣ Keterangan Ban?\n"
        "(Format: Umur Ban, Tekanan, Kondisi, Penyebab, Jenis Ban)\n\n"
        "Contoh jawab: 2 Tahun, 35 psi, Aus, Tertusuk Benda Tajam, Tubeless\n"
        "(Jika tidak ada info ban, ketik: nihil, nihil, nihil, nihil, nihil)"
    )
    return INFO_BAN

async def simpan_info_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Memisahkan input keterangan ban
    info_ban = update.message.text.split(',')
    
    # Mencegah error jika user ngetik kurang dari 5 item
    if len(info_ban) >= 5:
        umur_ban = info_ban[0].strip()
        tekanan = info_ban[1].strip()
        kondisi = info_ban[2].strip()
        penyebab_ban = info_ban[3].strip()
        jenis = info_ban[4].strip()
    else:
        umur_ban = update.message.text
        tekanan = "-"
        kondisi = "-"
        penyebab_ban = "-"
        jenis = "-"

    # Proses Tanggal Otomatis
    now = datetime.datetime.now()
    hari_dict = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jum at", "Saturday": "Sabtu", "Sunday": "Minggu"}
    bulan_dict = {"01": "Januari", "02": "Februari", "03": "Maret", "04": "April", "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus", "09": "September", "10": "Oktober", "11": "November", "12": "Desember"}
    
    hari = hari_dict[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = bulan_dict[now.strftime("%m")]
    tahun = now.strftime("%Y")
    tanggal_indo = f"{hari} / {tanggal} {bulan} {tahun}"

    # Susun Laporan Akhir
    pesan_hasil = (
        "_*LAPORAN AWAL KEJADIAN*_\n\n"
        "Ruas : *Surabaya - Mojokerto*\n"
        f"Jenis Kecelakaan : 3-3 {context.user_data['jenis']}\n"
        f"Hari / Tanggal : {tanggal_indo}\n"
        f"Shift : {context.user_data['shift_laka']}\n"
        f"Waktu Kejadian : {context.user_data['waktu_kejadian']}\n"
        "Petugas Tiba di TKP :\n"
        f"- {context.user_data['waktu_tiba']}\n"
        f"Lokasi : {context.user_data['lokasi']}\n"
        f"Penyebab : {context.user_data['penyebab']}\n"
        "Kendaraan Terlibat :\n"
        f"{context.user_data['kendaraan']}\n"
        f"Korban : {context.user_data['korban']}\n"
        f"Cuaca : {context.user_data['cuaca']}\n"
        f"Dampak : {context.user_data['dampak']}\n"
        f"Sarana : {context.user_data['sarana']}\n\n"
        "Keterangan Ban >>\n"
        f"- Umur Ban : {umur_ban}\n"
        f"- Tekanan Ban : {tekanan}\n"
        f"- Kondisi Ban : {kondisi}\n"
        f"- Penyebab : {penyebab_ban}\n"
        f"- Jenis Ban : {jenis}"
    )
    
    await update.message.reply_text(pesan_hasil)
    return ConversationHandler.END

async def cancel_laka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pembuatan Laporan Laka dibatalkan. ❌")
    return ConversationHandler.END

# Daftarkan Conversation Handler untuk Laka
laka_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('laka', mulai_laka)],
    states={
        JENIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_jenis)],
        SHIFT_LAKA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift_laka)],
        WAKTU_KEJADIAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_waktu_kejadian)],
        WAKTU_TIBA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_waktu_tiba)],
        LOKASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi)],
        PENYEBAB: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_penyebab)],
        KENDARAAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kendaraan)],
        KORBAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_korban)],
        CUACA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_cuaca)],
        DAMPAK: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_dampak)],
        SARANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_sarana)],
        INFO_BAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_info_ban)],
    },
    fallbacks=[CommandHandler('cancel', cancel_laka)]
)