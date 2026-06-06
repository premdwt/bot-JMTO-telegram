import json
import os
import random
import string
import time
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# --- IMPORT ADMIN ID DARI CONFIG ---
from config import ADMIN_ID

KEYS_FILE = "keys_data.json"
ACCOUNTS_FILE = "accounts.json"

# --- FUNGSI DATABASE ---
def load_data(filename):
    if not os.path.exists(filename):
        return {"keys": {}, "users": {}} if filename == KEYS_FILE else {}
    with open(filename, "r") as f:
        try: return json.load(f)
        except json.JSONDecodeError: 
            return {"keys": {}, "users": {}} if filename == KEYS_FILE else {}

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# --- 1. FITUR ADMIN: /genkey ---
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ **Akses Ditolak!** Lu bukan Admin bot ini.")

    # Pilihan Durasi
    durasi_map = {
        "30m": (1800, "30 Menit"),
        "1h": (3600, "1 Jam"),
        "12h": (43200, "12 Jam"),
        "1d": (86400, "1 Hari"),
        "1w": (604800, "1 Minggu"),
        "1mo": (2592000, "1 Bulan")
    }

    if not context.args or context.args[0].lower() not in durasi_map:
        pesan_bantuan = (
            "⚠️ **Format Salah!**\n"
            "Gunakan: `/genkey <durasi>`\n\n"
            "**Pilihan Durasi:**\n"
            "`30m` = 30 Menit\n`1h` = 1 Jam\n`12h` = 12 Jam\n"
            "`1d` = 1 Hari\n`1w` = 1 Minggu\n`1mo` = 1 Bulan\n\n"
            "Contoh: `/genkey 1d`"
        )
        return await update.message.reply_text(pesan_bantuan, parse_mode='Markdown')

    pilihan = context.args[0].lower()
    duration_seconds, duration_label = durasi_map[pilihan]

    prefix = "PREM"
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    new_key = f"{prefix}-{random_str}"
    
    keys_db = load_data(KEYS_FILE)
    if "keys" not in keys_db: keys_db = {"keys": {}, "users": {}} # Safety check
        
    keys_db["keys"][new_key] = {
        "duration_seconds": duration_seconds, 
        "duration_label": duration_label,   
        "status": "available",
        "used_by": None
    }
    save_data(KEYS_FILE, keys_db)
    
    pesan_sukses = (
        f"✅ **Key Berhasil Dibuat!**\n"
        f"🔑 Key: `{new_key}`\n"
        f"⏳ Durasi: {duration_label}\n\n"
        f"Kasih key ini ke pembeli dan suruh ketik:\n`/redeem {new_key}`"
    )
    await update.message.reply_text(pesan_sukses, parse_mode='Markdown')

# --- 2. FITUR USER: /redeem ---
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ **Format Salah!** Gunakan: `/redeem <key>`", parse_mode='Markdown')

    key = context.args[0]
    user_id_str = str(update.effective_user.id)
    keys_db = load_data(KEYS_FILE)
    
    if key not in keys_db.get("keys", {}) or keys_db["keys"][key]["status"] != "available":
        return await update.message.reply_text("❌ **Gagal Aktivasi!** Key tidak valid, salah ketik, atau sudah terpakai.")
        
    key_data = keys_db["keys"][key]
    duration_seconds = key_data["duration_seconds"]
    expired_timestamp = time.time() + duration_seconds
    
    # Update Data User
    keys_db["users"][user_id_str] = {"expired_at": expired_timestamp}
    
    # Update Data Key
    keys_db["keys"][key]["status"] = "used"
    keys_db["keys"][key]["used_by"] = user_id_str
    save_data(KEYS_FILE, keys_db)
    
    pesan_redeem = (
        f"🎉 **Aktivasi Berhasil!**\n"
        f"Lu sekarang berstatus VIP selama **{key_data['duration_label']}** ke depan.\n\n"
        f"Gunakan command `/generate hbo` atau `/generate vision` untuk mengambil akun."
    )
    await update.message.reply_text(pesan_redeem, parse_mode='Markdown')

# --- 3. FITUR USER: /generate ---
async def generate_akun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_str = str(update.effective_user.id)
    keys_db = load_data(KEYS_FILE)
    
    # Cek Akses VIP
    if user_id_str not in keys_db.get("users", {}):
        return await update.message.reply_text("⛔ **Akses Ditolak!** Lu belum punya akses VIP. Silahkan `/redeem <key>` dulu.")
        
    user_data = keys_db["users"][user_id_str]
    if time.time() > user_data["expired_at"]:
        return await update.message.reply_text("⚠️ Masa aktif lisensi lu udah habis boss! Silahkan beli key baru.")

    if not context.args or context.args[0].lower() not in ["hbo", "vision"]:
        return await update.message.reply_text("⚠️ **Format Salah!** Gunakan: `/generate hbo` atau `/generate vision`", parse_mode='Markdown')

    layanan = context.args[0].lower()
    accounts = load_data(ACCOUNTS_FILE)
    
    if layanan not in accounts or not accounts[layanan]:
        return await update.message.reply_text(f"⚠️ Maaf boss, stok akun **{layanan.upper()}** lagi kosong di database!", parse_mode='Markdown')

    selected_account = random.choice(accounts[layanan])
    try:
        email, password = selected_account.split(":")
    except ValueError:
        return await update.message.reply_text("❌ Error Format Database! Hubungi Admin.")

    pesan_dm = (
        f"🎁 **TIKET PREMIUM: {layanan.upper()}**\n\n"
        f"Ini dia detail akun premium lu boss! Tolong jangan diganti passwordnya biar member lain bisa pake.\n\n"
        f"📧 **Email:** `{email}`\n"
        f"🔑 **Password:** `{password}`\n\n"
        f"*System Generated via Bot Enggar*"
    )

    # Kirim via DM (Private Message)
    try:
        await context.bot.send_message(chat_id=update.effective_user.id, text=pesan_dm, parse_mode='Markdown')
        if update.effective_chat.type != "private":
            await update.message.reply_text(f"✅ **Berhasil!** Akun **{layanan.upper()}** udah gw kirim ke DM lu ya. Cek sekarang!", parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Gagal mengirim akun! Pastikan lu udah pernah nge-chat (Start) bot ini secara pribadi via DM.")

# --- 4. FITUR ADMIN: /checkkey ---
async def checkkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Gunakan: `/checkkey <key>`", parse_mode='Markdown')

    key = context.args[0]
    keys_db = load_data(KEYS_FILE)
    
    if key not in keys_db.get("keys", {}):
        return await update.message.reply_text(f"❌ Key `{key}` tidak ditemukan!", parse_mode='Markdown')
        
    key_data = keys_db["keys"][key]
    status_icon = "🟢 Available" if key_data["status"] == "available" else "🔴 Used"
    
    pesan = (
        f"🔍 **INFO LICENSE KEY**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔑 Key: `{key}`\n"
        f"⏳ Durasi: {key_data['duration_label']}\n"
        f"📌 Status: {status_icon}\n"
    )
    
    if key_data["status"] == "used":
        used_by = key_data.get("used_by")
        pesan += f"👤 Dipakai Oleh: ID `{used_by}`\n"
        
    await update.message.reply_text(pesan, parse_mode='Markdown')

# --- 5. FITUR ADMIN: /deletekey & /cleankey ---
async def deletekey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Gunakan: `/deletekey <key>`", parse_mode='Markdown')

    key = context.args[0]
    keys_db = load_data(KEYS_FILE)
    
    if key in keys_db.get("keys", {}):
        used_by = keys_db["keys"][key].get("used_by")
        if used_by and used_by in keys_db["users"]:
            del keys_db["users"][used_by] # Cabut akses user
        del keys_db["keys"][key] # Hapus key
        save_data(KEYS_FILE, keys_db)
        await update.message.reply_text(f"✅ Key `{key}` dan akses usernya berhasil dihapus permanen!", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Key tidak ditemukan.")

async def cleankey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    keys_db = load_data(KEYS_FILE)
    
    current_time = time.time()
    old_users = keys_db.get("users", {})
    
    # Filter user yang masih aktif
    keys_db["users"] = {u: v for u, v in old_users.items() if v["expired_at"] > current_time}
    cleaned_users = len(old_users) - len(keys_db["users"])
    
    # Filter key yang masih available atau sedang dipakai user aktif
    old_keys = keys_db.get("keys", {})
    new_keys = {}
    for k, v in old_keys.items():
        if v["status"] == "available":
            new_keys[k] = v
        elif v["status"] == "used" and v.get("used_by") in keys_db["users"]:
            new_keys[k] = v
            
    keys_db["keys"] = new_keys
    cleaned_keys = len(old_keys) - len(keys_db["keys"])
    save_data(KEYS_FILE, keys_db)
    
    pesan = f"🧹 **Pembersihan Selesai!**\n🗑️ Key kedaluwarsa dihapus: `{cleaned_keys}`\n🗑️ User expired dihapus: `{cleaned_users}`"
    await update.message.reply_text(pesan, parse_mode='Markdown')

# --- DAFTAR COMMAND HANDLER ---
genkey_cmd = CommandHandler('genkey', genkey)
redeem_cmd = CommandHandler('redeem', redeem)
generate_cmd = CommandHandler('generate', generate_akun)
checkkey_cmd = CommandHandler('checkkey', checkkey)
deletekey_cmd = CommandHandler('deletekey', deletekey)
cleankey_cmd = CommandHandler('cleankey', cleankey)