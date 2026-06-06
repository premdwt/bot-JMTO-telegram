from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN

# --- IMPORT DARI FOLDER HANDLERS ---
from handlers.base_cmds import start_command
from handlers.lapor_cmd import lapor_conv_handler
from handlers.laka_cmd import laka_conv_handler
from handlers.pantauan_cmd import pantauan_conv_handler
from handlers.trace_cmd import trace_conv_handler
from handlers.giat_cmd import giat_conv_handler
from handlers.jadwal_cmd import jadwal_conv, shift_conv
from handlers.jadwal_mcss_cmd import jadwal_mcss_conv, shift_mcss_conv # TAMBAHAN BARU

def main():
    print("Membangunkan bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # --- DAFTARIN FITUR ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(lapor_conv_handler)
    app.add_handler(laka_conv_handler)
    app.add_handler(pantauan_conv_handler)
    app.add_handler(trace_conv_handler)
    app.add_handler(giat_conv_handler)
    
    # Fitur Jadwal Petugas
    app.add_handler(jadwal_conv)
    app.add_handler(shift_conv)
    
    # Fitur Jadwal MCSS
    app.add_handler(jadwal_mcss_conv) # TAMBAHAN BARU
    app.add_handler(shift_mcss_conv)  # TAMBAHAN BARU
    
    print("Bot berhasil nyala! Tekan Ctrl+C untuk mematikan.")
    app.run_polling()

if __name__ == '__main__':
    main()