from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    
    pesan = (
        f"Halo Komandan {user_name}! 🫡✨\n\n"
        "Saya adalah Bot laporan JMTO yg berada di JSM. 🚔🛣️\n"
        "Siap membantu meringankan beban ngetik laporan & ngecek jadwal lu! ⚡\n\n"
        "Berikut adalah menu yang bisa lu pakai:\n"
        "📝 /lapor - *Laporan Serah Terima Shift*\n"
        "🚨 /laka - *Laporan Awal Kejadian 33*\n"
        "👀 /pantauan - *Laporan Pantauan Kondisi*\n"
        "🛠️ /trace - *Laporan Penanganan Kendala (Trace)*\n"
        "🚧 /giat - *Laporan Penanganan Biasa / Rutin*\n\n"
        "👮‍♂️ *MENU JADWAL PETUGAS:*\n"
        "🗓️ /jadwal - *Cek Jadwal Sebulan per Petugas*\n"
        "📆 /shift - *Cek Petugas Shift per Tanggal*\n\n"
        "👔 *MENU JADWAL MCSS (210):*\n"
        "🗓️ /210 - *Cek Jadwal Sebulan per Kashift*\n"
        "📆 /210s - *Cek Shift Kashift per Tanggal*\n\n"
        "💡 *Tips:* Kalau di tengah-tengah ngisi laporan lu mau batalin, ketik aja /cancel ya 🙈\n\n"
        "Yuk, langsung aja klik atau ketik salah satu command di atas buat mulai. Selamat bertugas dan semoga selalu Aman TKA! 🤲🏻🚀"
    )
    
    gambar = "https://cdn.discordapp.com/attachments/1507982479913390171/1512521389066686546/generated-image.png?ex=6a2464d0&is=6a231350&hm=90a9af27f62edd2078f8fd1cc60cfb29c6feba90a00af7aa29aead2730d2a91f&"
    
    await update.message.reply_photo(photo=gambar, caption=pesan, parse_mode='Markdown')