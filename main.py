from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN

# --- IMPORT DARI FOLDER HANDLERS (OPERASIONAL JSM) ---
from handlers.base_cmds import start_command
from handlers.lapor_cmd import lapor_conv_handler
from handlers.laka_cmd import laka_conv_handler
from handlers.pantauan_cmd import pantauan_conv_handler
from handlers.trace_cmd import trace_conv_handler
from handlers.giat_cmd import giat_conv_handler
from handlers.jadwal_cmd import jadwal_conv, shift_conv
from handlers.jadwal_mcss_cmd import jadwal_mcss_conv, shift_mcss_conv

# --- IMPORT DARI FOLDER HANDLERS (VIP GENERATOR) ---
from handlers.generator_cmd import genkey_cmd, redeem_cmd, generate_cmd, checkkey_cmd, deletekey_cmd, cleankey_cmd

def main():
    print("Membangunkan bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # --- DAFTARIN FITUR OPERASIONAL JSM ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(lapor_conv_handler)
    app.add_handler(laka_conv_handler)
    app.add_handler(pantauan_conv_handler)
    app.add_handler(trace_conv_handler)
    app.add_handler(giat_conv_handler)
    
    # Fitur Jadwal Petugas & MCSS
    app.add_handler(jadwal_conv)
    app.add_handler(shift_conv)
    app.add_handler(jadwal_mcss_conv)
    app.add_handler(shift_mcss_conv) 
    
    # --- DAFTARIN FITUR VIP GENERATOR ---
    app.add_handler(genkey_cmd)
    app.add_handler(redeem_cmd)
    app.add_handler(generate_cmd)
    app.add_handler(checkkey_cmd)
    app.add_handler(deletekey_cmd)
    app.add_handler(cleankey_cmd)
    
    print("Bot berhasil nyala! Tekan Ctrl+C untuk mematikan.")
    app.run_polling()

if __name__ == '__main__':
    main()