from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- DATABASE PETUGAS MCSS ---
MCSS_PETUGAS = {
    'A': 'Yudha Prawira',
    'B': 'Ainur Rofik',
    'C': 'Suluh Arsha Adit W',
    'D': 'Fahrozy Nursadi P',
    'E': 'Abdul Gofur'
}

# --- ATURAN CUTI & PENGGANTI ---
# Format: Tanggal: ('Kode_Cuti', 'Kode_Pengganti')
overrides_mcss = {
    3:  ('A', 'B'), # Ainur ganti Yudha
    4:  ('A', 'B'), # Ainur ganti Yudha
    5:  ('A', 'E'), # Abdul ganti Yudha
    6:  ('C', 'D'), # Fahrozy ganti Suluh
    7:  ('C', 'D'), # Fahrozy ganti Suluh
    8:  ('C', 'B'), # Ainur ganti Suluh
    22: ('B', 'C'), # Suluh ganti Ainur
    23: ('B', 'C'), # Suluh ganti Ainur
    24: ('B', 'A')  # Yudha ganti Ainur
}

def generate_mcss_schedule():
    schedule = {}
    for tgl in range(1, 31):
        # Pola dasar rotasi tiap 5 hari
        mod = tgl % 5
        if mod == 1:   base = ['C', 'D', 'E', 'A', 'B']
        elif mod == 2: base = ['B', 'C', 'D', 'E', 'A']
        elif mod == 3: base = ['A', 'B', 'C', 'D', 'E']
        elif mod == 4: base = ['E', 'A', 'B', 'C', 'D']
        elif mod == 0: base = ['D', 'E', 'A', 'B', 'C']

        status_hari_ini = {
            base[0]: "☀️ Shift 1 (06.00-14.00)",
            base[1]: "🌤️ Shift 2 (14.00-22.00)",
            base[2]: "🌙 Shift 3 (22.00-06.00)",
            base[3]: "🛋️ Libur",
            base[4]: "🛋️ Libur",
        }

        # Eksekusi logika Cuti & Pengganti (Double Shift otomatis terekam)
        if tgl in overrides_mcss:
            cuti_code = overrides_mcss[tgl][0]
            pengganti_code = overrides_mcss[tgl][1]

            shift_cuti = status_hari_ini[cuti_code]
            nama_pengganti = MCSS_PETUGAS[pengganti_code].split()[0]
            nama_cuti = MCSS_PETUGAS[cuti_code].split()[0]

            status_hari_ini[cuti_code] = f"🏝️ Cuti (Diganti {nama_pengganti})"
            status_hari_ini[pengganti_code] = f"{status_hari_ini[pengganti_code]}\n      ↳ ➕ {shift_cuti} (Ganti {nama_cuti})"

        # Mapping untuk pencarian per tanggal
        shift_map = {'S1': [], 'S2': [], 'S3': []}
        for kode, status in status_hari_ini.items():
            nama = MCSS_PETUGAS[kode]
            if "Cuti" in status and "➕" not in status:
                continue # Kalo murni cuti, lewati dari daftar shift
            
            if "Shift 1" in status: shift_map['S1'].append(nama)
            if "Shift 2" in status: shift_map['S2'].append(nama)
            if "Shift 3" in status: shift_map['S3'].append(nama)

        schedule[tgl] = {
            'per_person': status_hari_ini,
            'per_shift': shift_map
        }
    return schedule

JADWAL_MCSS = generate_mcss_schedule()

# --- 1. FITUR /210 (CARI PER ORANG) ---
CARI_NAMA_MCSS = 1
async def mulai_jadwal_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗓️ Masukkan nama MCSS/Kashift yang mau dicek jadwalnya (Contoh: Yudha / Ainur):")
    return CARI_NAMA_MCSS

async def proses_nama_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    kode_ditemukan = None
    nama_lengkap = ""
    
    for kode, nama in MCSS_PETUGAS.items():
        if query in nama.lower():
            kode_ditemukan = kode
            nama_lengkap = nama
            break
            
    if not kode_ditemukan:
        await update.message.reply_text("❌ Nama Kashift tidak ditemukan. Coba lagi atau ketik /cancel.")
        return CARI_NAMA_MCSS
        
    pesan = f"📅 *JADWAL MCSS JUNI 2026*\n👤 *{nama_lengkap}*\n━━━━━━━━━━━━━━━━━━━━\n"
    for tgl in range(1, 31):
        posisi = JADWAL_MCSS[tgl]['per_person'][kode_ditemukan]
        tgl_str = str(tgl).zfill(2)
        pesan += f"Tgl {tgl_str} : {posisi}\n"
        if tgl % 10 == 0: pesan += "\n"
        
    await update.message.reply_text(pesan, parse_mode='Markdown')
    return ConversationHandler.END

# --- 2. FITUR /210s (CARI PER TANGGAL) ---
CARI_TANGGAL_MCSS = 1
async def mulai_shift_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📆 Masukkan tanggal untuk cek shift MCSS di bulan Juni 2026 (1 - 30):")
    return CARI_TANGGAL_MCSS

async def proses_tanggal_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tgl = int(update.message.text)
        if tgl < 1 or tgl > 30: raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Tolong masukkan angka tanggal yang valid (1 - 30) atau ketik /cancel.")
        return CARI_TANGGAL_MCSS
        
    shifts = JADWAL_MCSS[tgl]['per_shift']
    
    s1_text = " & ".join(shifts['S1']) if shifts['S1'] else "-"
    s2_text = " & ".join(shifts['S2']) if shifts['S2'] else "-"
    s3_text = " & ".join(shifts['S3']) if shifts['S3'] else "-"
    
    pesan = (
        f"📅 *JADWAL MCSS - {str(tgl).zfill(2)} JUNI 2026*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"☀️ Shift 1 : {s1_text}\n"
        f"🌤️ Shift 2 : {s2_text}\n"
        f"🌙 Shift 3 : {s3_text}\n"
    )
    
    await update.message.reply_text(pesan, parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_mcss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pengecekan jadwal MCSS dibatalkan. ❌")
    return ConversationHandler.END

jadwal_mcss_conv = ConversationHandler(
    entry_points=[CommandHandler('210', mulai_jadwal_mcss)], 
    states={CARI_NAMA_MCSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_nama_mcss)]}, 
    fallbacks=[CommandHandler('cancel', cancel_mcss)]
)

shift_mcss_conv = ConversationHandler(
    entry_points=[CommandHandler('210s', mulai_shift_mcss)], 
    states={CARI_TANGGAL_MCSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_tanggal_mcss)]}, 
    fallbacks=[CommandHandler('cancel', cancel_mcss)]
)