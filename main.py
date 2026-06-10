import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, TypeHandler
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
from handlers.generator_cmd import (
    genkey_cmd,
    redeem_cmd,
    generate_cmd,
    checkkey_cmd,
    deletekey_cmd,
    cleankey_cmd
)

# ================= LOGGING TERMINAL SAJA =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def log_all_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mencatat semua aktivitas user ke terminal.
    Tidak membuat file log.
    """
    if not update.effective_user:
        return

    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    nama = user.full_name
    username = f"@{user.username}" if user.username else "-"
    user_id = user.id
    chat_id = chat.id if chat else "-"
    chat_type = chat.type if chat else "-"

    pesan = "-"
    if message and message.text:
        pesan = message.text

    logger.info(
        f"AKTIVITAS USER | "
        f"nama={nama} | "
        f"username={username} | "
        f"user_id={user_id} | "
        f"chat_id={chat_id} | "
        f"chat_type={chat_type} | "
        f"pesan={pesan}"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Mencatat error bot ke terminal.
    """
    logger.error("TERJADI ERROR DI BOT", exc_info=context.error)


def main():
    logger.info("Membangunkan bot...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Logger semua aktivitas user
    app.add_handler(TypeHandler(Update, log_all_activity), group=-1)

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

    # Logger error
    app.add_error_handler(error_handler)

    logger.info("Bot berhasil nyala! Tekan Ctrl+C untuk mematikan.")
    app.run_polling()


if __name__ == '__main__':
    main()