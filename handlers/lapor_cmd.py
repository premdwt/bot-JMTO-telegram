import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Tentukan 10 Tahapan Pertanyaan
MOBIL, SHIFT, PERSONIL, RC, RAMBU, KONDISI, ODDO_AWAL, ODDO_AKHIR, PENANGANAN, ESTAFET = range(10)

async def mulai_lapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siap laksanakan! 📝\n\n1️⃣ Masukkan ID Kendaraan (Contoh: JSM 211):")
    return MOBIL

async def simpan_mobil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mobil'] = update.message.text
    await update.message.reply_text("2️⃣ Shift berapa hari ini? (Contoh: 2):")
    return SHIFT

async def simpan_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['shift'] = update.message.text
    await update.message.reply_text("3️⃣ Siapa saja personilnya? (Pisahkan dengan koma. Contoh: Ade, amirul):")
    return PERSONIL

async def simpan_personil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['personil'] = update.message.text
    await update.message.reply_text("4️⃣ Berapa Jumlah RC?:")
    return RC

async def simpan_rc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['rc'] = update.message.text
    await update.message.reply_text("5️⃣ Berapa Jumlah Rambu?:")
    return RAMBU

async def simpan_rambu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['rambu'] = update.message.text
    await update.message.reply_text(
        "6️⃣ Bagaimana Kondisi Kendaraan?\n"
        "(Urutannya: Rotator/Lampu, Ban, Body, Sirine, Radio)\n\n"
        "Contoh jawab: baik, Baik, Baik, menyala baik, aman"
    )
    return KONDISI

async def simpan_kondisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kondisi = update.message.text.split(',')
    
    if len(kondisi) >= 5:
        context.user_data['rotator'] = kondisi[0].strip()
        context.user_data['ban'] = kondisi[1].strip()
        context.user_data['body'] = kondisi[2].strip()
        context.user_data['sirine'] = kondisi[3].strip()
        context.user_data['radio'] = kondisi[4].strip()
    else:
        context.user_data['rotator'] = update.message.text
        context.user_data['ban'] = "Baik"
        context.user_data['body'] = "Baik"
        context.user_data['sirine'] = "Baik"
        context.user_data['radio'] = "Aman"

    await update.message.reply_text("7️⃣ Masukkan angka Oddo Awal:")
    return ODDO_AWAL

async def simpan_oddo_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oddo_awal'] = update.message.text
    await update.message.reply_text("8️⃣ Masukkan angka Oddo Akhir (Ketik 0 jika ini Laporan Awal):")
    return ODDO_AKHIR

async def simpan_oddo_akhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['oddo_akhir'] = update.message.text
    await update.message.reply_text("9️⃣ Berapa Jumlah Penanganan?:")
    return PENANGANAN

async def simpan_penanganan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['penanganan'] = update.message.text
    await update.message.reply_text("🔟 Status Estafet? (Contoh: nihil):")
    return ESTAFET

async def simpan_estafet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['estafet'] = update.message.text
    
    # --- PROSES MATEMATIKA & PENENTUAN STATUS TUGAS (REVISI BARU) ---
    try:
        oddo_awal = int(context.user_data['oddo_awal'])
        oddo_akhir = int(context.user_data['oddo_akhir'])
        
        if oddo_akhir == 0:
            jumlah_oddo = 0
            status_tugas = "awal tugas" # Mengubah teks jadi awal tugas
        else:
            jumlah_oddo = oddo_akhir - oddo_awal
            status_tugas = "akhir tugas" # Mengubah teks jadi akhir tugas
    except ValueError:
        jumlah_oddo = "Error (Input selain angka)"
        status_tugas = "akhir tugas"

    # --- PROSES TANGGAL OTOMATIS ---
    now = datetime.datetime.now()
    hari_dict = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jum at", "Saturday": "Sabtu", "Sunday": "Minggu"}
    bulan_dict = {"01": "Januari", "02": "Februari", "03": "Maret", "04": "April", "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus", "09": "September", "10": "Oktober", "11": "November", "12": "Desember"}
    
    hari = hari_dict[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = bulan_dict[now.strftime("%m")]
    tahun = now.strftime("%Y")
    tanggal_indo = f"{hari} , {tanggal} {bulan} {tahun}"

    # --- PROSES BULLET POINT PERSONIL ---
    personil_list = context.user_data['personil'].split(',')
    personil_format = "\n".join([f"▪️{p.strip()}" for p in personil_list])

    # --- CETAK HASIL AKHIR ---
    pesan_hasil = (
        f"Mohon ijin *melaporkan serah terima {status_tugas}* :\n\n" # <--- Bagian ini sudah dinamis otomatis
        f"🚔 {context.user_data['mobil']}\n"
        f"📆 {tanggal_indo}\n"
        f"🕕 Shift {context.user_data['shift']}\n"
        f"Personil :\n{personil_format}\n\n"
        f"Jumlah RC :  {context.user_data['rc']}\n"
        f"Jumlah Rambu : {context.user_data['rambu']}\n"
        f"Rotator & Lampu : {context.user_data['rotator']}\n"
        f"Ban : {context.user_data['ban']}\n"
        f"Kondisi Body : {context.user_data['body']}\n"
        f"Sirine : {context.user_data['sirine']}\n"
        f"Radio Komunikasi : {context.user_data['radio']}\n"
        f"Oddo Awal : {context.user_data['oddo_awal']}\n"
        f"Oddo Akhir : {context.user_data['oddo_akhir']}\n"
        f"Jumlah Oddo : {jumlah_oddo}\n"
        f"Jumlah Penanganan : {context.user_data['penanganan']}\n"
        f"Estafet : {context.user_data['estafet']}\n\n"
        f"Semoga tetap Aman TKA sampai serah terima {status_tugas} 🤲🏻"
    )
    
    await update.message.reply_text(pesan_hasil, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pengisian laporan dibatalkan. ❌")
    return ConversationHandler.END

lapor_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('lapor', mulai_lapor)],
    states={
        MOBIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mobil)],
        SHIFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_shift)],
        PERSONIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil)],
        RC: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_rc)],
        RAMBU: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_rambu)],
        KONDISI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_kondisi)],
        ODDO_AWAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_awal)],
        ODDO_AKHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_oddo_akhir)],
        PENANGANAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_penanganan)],
        ESTAFET: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_estafet)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)