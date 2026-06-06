from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Tentukan 6 Tahapan Pertanyaan untuk Giat
(UNIT_G, PERSONIL1_G, PERSONIL2_G, MCSS_G, LOKASI_G, GIAT_G) = range(6)

async def mulai_giat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 Siap! Mari buat Laporan Giat / Penanganan Biasa.\n\n1️⃣ Masukkan ID Unit/Kendaraan (Contoh: JSM 211):")
    return UNIT_G

async def simpan_unit_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['unit'] = update.message.text.upper()
    await update.message.reply_text("2️⃣ Masukkan nama Personil 1:")
    return PERSONIL1_G

async def simpan_personil1_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p1'] = update.message.text
    await update.message.reply_text("3️⃣ Masukkan nama Personil 2:")
    return PERSONIL2_G

async def simpan_personil2_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p2'] = update.message.text
    await update.message.reply_text("4️⃣ Siapa nama MCSS? (Cukup ketik namanya saja, contoh: Bambang):")
    return MCSS_G

async def simpan_mcss_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama_mcss = update.message.text
    
    # Proteksi biar gak "Bpk. Bpk."
    if nama_mcss.lower().startswith("bpk.") or nama_mcss.lower().startswith("bpk "):
        context.user_data['mcss'] = nama_mcss
    else:
        context.user_data['mcss'] = f"Bpk. {nama_mcss}"
        
    await update.message.reply_text("5️⃣ Lokasi? (Contoh: KM 714 A / Bahu Luar):")
    return LOKASI_G

async def simpan_lokasi_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lokasi_g'] = update.message.text
    await update.message.reply_text("6️⃣ Giat yang dilakukan? (Contoh: Pembersihan lajur / Patroli rutin):")
    return GIAT_G

async def simpan_giat_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['giat_g'] = update.message.text
    
    # --- CETAK HASIL AKHIR ---
    pesan_hasil = (
        "*LAPORAN MCS RUAS SUMO*\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"{context.user_data['unit']}\n\n"
        f"1. {context.user_data['p1']}\n"
        f"2. {context.user_data['p2']}\n\n"
        f"MCSS : {context.user_data['mcss']}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"GIAT {context.user_data['unit']}\n"
        "━━━━━━━━━━━━━━━━━\n\n"
        f"Lokasi : {context.user_data['lokasi_g']}\n"
        f"Giat : {context.user_data['giat_g']}\n\n"
        "Demikian yang dapat dilaporkan.\n"
        "Terima Kasih 🙏🏼"
    )
    
    await update.message.reply_text(pesan_hasil, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_giat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pembuatan Laporan Giat dibatalkan. ❌")
    return ConversationHandler.END

giat_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('giat', mulai_giat)],
    states={
        UNIT_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_unit_g)],
        PERSONIL1_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil1_g)],
        PERSONIL2_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_personil2_g)],
        MCSS_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_mcss_g)],
        LOKASI_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_lokasi_g)],
        GIAT_G: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_giat_g)],
    },
    fallbacks=[CommandHandler('cancel', cancel_giat)]
)