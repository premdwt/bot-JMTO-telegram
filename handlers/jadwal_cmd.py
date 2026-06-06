from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- DATABASE NAMA PETUGAS ---
PETUGAS = {
    'A': 'M. Amirul T', 'B': 'Rizky Aulia Putra', 'C': 'Ade Nurachmatullah',
    'D': 'Yohanes Hutting', 'E': 'Roby Setiawan', 'F': 'Rivantio Fadhly',
    'G': 'Doddy Wiria', 'H': 'Enggarjaya Premana', 'I': 'Adriatma Crisdianto Salati',
    'J': 'M. Mahmudi Basya', 'K': 'Galih Agung N', 'L': 'Rizky Ardiansyah Rifai',
    'M': 'Agus Nurdiansyah', 'N': 'M. Fahris Hidayat', 'O': 'Hepri Wahyu',
    'P': 'Andi Tri W', 'Q': 'Ikhwan Rosidi', 'R': 'Wiki Wicaksono',
    'S': 'Aditya Priambodo', 'T': 'David Aprilianto'
}

# --- DATABASE JADWAL MANUAL 1-30 JUNI 2026 BERDASARKAN FOTO EXCEL ---
# Format urutan list: [211_S2_A, 211_S2_B, 211_S3, 211_LBR1, 211_LBR2, 211_S1_A, 211_S1_B, 211_S3_B, 211_LBR3,  212_S2_A, 212_S2_B, 212_S3, 212_LBR1, 212_LBR2, 212_S1_A, 212_S1_B, 212_S3_B, 212_LBR3, PC]
raw_jadwal = {
    1:  ['G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D'],
    2:  ['D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K'],
    3:  ['K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S'],
    4:  ['S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A'], # S Cuti diganti C
    5:  ['A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R'], # S Cuti diganti C
    6:  ['R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H'], # S Cuti diganti C
    7:  ['H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F'],
    8:  ['F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N'], # K Cuti diganti C
    9:  ['N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T'], # K Cuti diganti C
    10: ['T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B'], # K Cuti diganti C
    11: ['B','T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E'],
    12: ['E','B','T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J'],
    13: ['J','E','B','T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q'],
    14: ['Q','J','E','B','T','N','F','H','R','A','S','K','D','G','O','I','P','L','M'],
    15: ['M','Q','J','E','B','T','N','F','H','R','A','S','K','D','G','O','I','P','L'],
    16: ['L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D','G','O','I','P'],
    17: ['P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D','G','O','I'],
    18: ['I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D','G','O'],
    19: ['O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D','G'],
    20: ['G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K','D'],
    21: ['D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S','K'],
    22: ['K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A','S'],
    23: ['S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R','A'],
    24: ['A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H','R'],
    25: ['R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F','H'],
    26: ['H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N','F'],
    27: ['F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T','N'],
    28: ['N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B','T'],
    29: ['T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E','B'],
    30: ['B','T','N','F','H','R','A','S','K','D','G','O','I','P','L','M','Q','J','E']
}

# Menyusun database final yang sudah disisipkan Cadangan (C) pengganti Cuti
jadwal_juni = {}
for tgl, baris in raw_jadwal.items():
    susunan = baris.copy()
    if tgl in [4, 5, 6]:  # S digantikan C
        idx_s = susunan.index('S')
        susunan[idx_s] = 'C'
    elif tgl in [8, 9, 10]:  # K digantikan C
        idx_k = susunan.index('K')
        susunan[idx_k] = 'C'
    jadwal_juni[tgl] = susunan

def get_posisi_string(idx):
    if idx in [0, 1]:    return "🚔 211 | 🌤️ Shift 2 (14.00-22.00)"
    elif idx == 2:       return "🚔 211 | 🌙 Shift 3 (22.00-06.00)"
    elif idx in [3, 4]:  return "🛋️ LIBUR"
    elif idx in [5, 6]:  return "🚔 211 | ☀️ Shift 1 (06.00-14.00)"
    elif idx == 7:       return "🚔 211 | 🌙 Shift 3 (22.00-06.00)"
    elif idx == 8:       return "🛋️ LIBUR"
    elif idx in [9, 10]: return "🚔 212 | 🌤️ Shift 2 (14.00-22.00)"
    elif idx == 11:      return "🚔 212 | 🌙 Shift 3 (22.00-06.00)"
    elif idx in [12, 13]:return "🛋️ LIBUR"
    elif idx in [14, 15]:return "🚔 212 | ☀️ Shift 1 (06.00-14.00)"
    elif idx == 16:      return "🚔 212 | 🌙 Shift 3 (22.00-06.00)"
    elif idx == 17:      return "🛋️ LIBUR"
    elif idx == 18:      return "💼 Petugas PC (Dinas Pagi)"
    return "🛋️ LIBUR"

# --- 1. FITUR /jadwal (CARI PER ORANG) ---
CARI_NAMA = 1
async def mulai_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗓️ Masukkan nama petugas yang mau dicek jadwalnya (Contoh: Enggar / Amirul):")
    return CARI_NAMA

async def proses_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    kode_ditemukan = None
    nama_lengkap = ""
    
    for kode, nama in PETUGAS.items():
        if query in nama.lower():
            kode_ditemukan = kode
            nama_lengkap = nama
            break
            
    if not kode_ditemukan:
        await update.message.reply_text("❌ Nama tidak ditemukan. Coba ketik nama panggilan yang lain atau ketik /cancel.")
        return CARI_NAMA
        
    pesan = f"📅 *JADWAL JUNI 2026*\n👤 *{nama_lengkap}*\n━━━━━━━━━━━━━━━━━━━━\n"
    for tgl in range(1, 31):
        try:
            idx_posisi = jadwal_juni[tgl].index(kode_ditemukan)
            posisi = get_posisi_string(idx_posisi)
        except ValueError:
            posisi = "🛋️ LIBUR"
            
        tgl_str = str(tgl).zfill(2)
        pesan += f"Tgl {tgl_str} : {posisi}\n"
        if tgl % 10 == 0: pesan += "\n"
        
    await update.message.reply_text(pesan, parse_mode='Markdown')
    return ConversationHandler.END

# --- 2. FITUR /shift (CARI PER TANGGAL) ---
CARI_TANGGAL = 1
async def mulai_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📆 Masukkan tanggal di bulan Juni 2026 (Ketik angka 1 sampai 30):")
    return CARI_TANGGAL

async def proses_tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tgl = int(update.message.text)
        if tgl < 1 or tgl > 30: raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Tolong masukkan angka tanggal yang valid (1 - 30) atau ketik /cancel.")
        return CARI_TANGGAL
        
    h = jadwal_juni[tgl]
    
    pesan = (
        f"📅 *JADWAL PETUGAS - {str(tgl).zfill(2)} JUNI 2026*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚔 *UNIT 211*\n"
        f"☀️ Shift 1 : {PETUGAS[h[5]]} & {PETUGAS[h[6]]}\n"
        f"🌤️ Shift 2 : {PETUGAS[h[0]]} & {PETUGAS[h[1]]}\n"
        f"🌙 Shift 3 : {PETUGAS[h[2]]} & {PETUGAS[h[7]]}\n\n"
        "🚔 *UNIT 212*\n"
        f"☀️ Shift 1 : {PETUGAS[h[14]]} & {PETUGAS[h[15]]}\n"
        f"🌤️ Shift 2 : {PETUGAS[h[9]]} & {PETUGAS[h[10]]}\n"
        f"🌙 Shift 3 : {PETUGAS[h[11]]} & {PETUGAS[h[16]]}\n\n"
        f"💼 *PC (Dinas Pagi)* : {PETUGAS[h[18]]}"
    )
    
    await update.message.reply_text(pesan, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pengecekan jadwal dibatalkan. ❌")
    return ConversationHandler.END

jadwal_conv = ConversationHandler(entry_points=[CommandHandler('jadwal', mulai_jadwal)], states={CARI_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_nama)]}, fallbacks=[CommandHandler('cancel', cancel_jadwal)])
shift_conv = ConversationHandler(entry_points=[CommandHandler('shift', mulai_shift)], states={CARI_TANGGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_tanggal)]}, fallbacks=[CommandHandler('cancel', cancel_jadwal)])