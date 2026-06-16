import logging

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.konektika_client import parse_lapor_akhir_teks
from handlers.lapor_cmd import _buat_pesan_laporan
from handlers.shift_session import get_sesi_shift, hapus_sesi_shift
from handlers.smartlapor_helpers import (
    ambil_angka,
    cek_rate_limit,
    keyboard_oddo_konfirmasi,
    keyboard_preview,
)

logger = logging.getLogger(__name__)

INPUT, ODDO_KONFIRMASI, PREVIEW = range(3)
PREVIEW_PREFIX = "smartakhirpreview"
ODDO_PREFIX = "smartakhiroddo"


def _seragamkan_kunci_akhir(data: dict) -> dict:
    peta_alias = {
        "oddo_akhir": ("oddo_akhir", "oddoakhir", "oddo_akhir_km"),
        "penanganan": ("penanganan", "jumlah_penanganan"),
        "estafet": ("estafet",),
    }

    data_bersih = {}
    for kunci, nilai in data.items():
        data_bersih[str(kunci).lower().replace(" ", "_").replace("-", "_")] = nilai

    hasil = {}
    for target, alias_list in peta_alias.items():
        for alias in alias_list:
            if alias in data_bersih and data_bersih[alias] not in (None, ""):
                hasil[target] = data_bersih[alias]
                break
    return hasil


def _normalisasi_data_akhir(data: dict) -> dict:
    data = _seragamkan_kunci_akhir(data)

    oddo_akhir = ambil_angka(data.get("oddo_akhir", ""))
    if not oddo_akhir.isdigit() or oddo_akhir == "0":
        raise ValueError("Oddo akhir wajib disebutkan dan harus lebih dari 0")

    penanganan = str(data.get("penanganan", "0")).strip()
    if penanganan.lower() in {"nihil", "-", "tidak ada", ""}:
        penanganan = "0"

    estafet = str(data.get("estafet", "nihil")).strip() or "nihil"

    return {
        "oddo_akhir": oddo_akhir,
        "penanganan": penanganan,
        "estafet": estafet,
    }


def _gabung_dengan_sesi(sesi_data: dict, update_akhir: dict) -> dict:
    hasil = dict(sesi_data)
    hasil["oddo_akhir"] = update_akhir["oddo_akhir"]
    hasil["penanganan"] = update_akhir["penanganan"]
    hasil["estafet"] = update_akhir["estafet"]
    return hasil


async def _tampilkan_preview(update: Update, data: dict):
    pesan = _buat_pesan_laporan(data)
    await update.message.reply_text(
        "📋 *CEK DULU YA (data shift + input akhir):*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{pesan}",
        parse_mode="Markdown",
        reply_markup=keyboard_preview(PREVIEW_PREFIX),
    )


async def mulai_smartlapor_akhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sesi = get_sesi_shift(user_id)

    if not sesi:
        await update.message.reply_text(
            "❌ *Belum ada laporan awal shift yang tersimpan.*\n\n"
            "Buat dulu laporan awal lewat /smartlapor\n"
            "(dengan oddo akhir = 0), lalu baru bisa pakai\n"
            "/smartlapor\\_akhir di akhir shift.\n\n"
            "_Sesi shift berlaku 10 jam sejak laporan awal dikirim._",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    data = sesi["data"]
    context.user_data["shift_sesi"] = data

    await update.message.reply_text(
        "🤖 *Smart Lapor Akhir (Beta)*\n\n"
        "Data shift kamu sudah tersimpan dari laporan awal:\n"
        f"🚔 {data['mobil']} | Shift {data['shift']} | Oddo awal: {data['oddo_awal']}\n\n"
        "Cukup ketik perubahan untuk akhir shift:\n"
        "• Oddo akhir\n"
        "• Jumlah penanganan\n"
        "• Estafet\n\n"
        "*Contoh:*\n"
        "`oddo akhir 250, penanganan 2, estafet nihil`\n\n"
        "Batal: /cancel",
        parse_mode="Markdown",
    )
    return INPUT


async def proses_input_akhir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sisa = cek_rate_limit(user_id)
    if sisa:
        await update.message.reply_text(
            f"⏳ Tunggu {sisa} detik dulu sebelum pakai Smart Lapor lagi."
        )
        return INPUT

    sesi = get_sesi_shift(user_id)
    if not sesi:
        await update.message.reply_text(
            "❌ Sesi laporan awal sudah tidak ada atau kadaluarsa.\n"
            "Buat laporan awal baru lewat /smartlapor."
        )
        return ConversationHandler.END

    teks = update.message.text.strip()
    if len(teks) < 5:
        await update.message.reply_text(
            "Teks terlalu pendek. Sebutkan oddo akhir, penanganan, dan estafet.\n"
            "Batal: /cancel"
        )
        return INPUT

    pesan_proses = await update.message.reply_text("⏳ AI sedang memproses data akhir shift...")

    try:
        data_mentah = await parse_lapor_akhir_teks(teks)
        logger.info("Smart Lapor Akhir data AI: %s", data_mentah)
        update_akhir = _normalisasi_data_akhir(data_mentah)
        data_gabungan = _gabung_dengan_sesi(sesi["data"], update_akhir)

        oddo_awal = int(data_gabungan["oddo_awal"])
        oddo_akhir = int(data_gabungan["oddo_akhir"])
        if oddo_akhir < oddo_awal:
            context.user_data["laporan_akhir"] = data_gabungan
            await pesan_proses.edit_text(
                f"⚠️ Oddo akhir ({oddo_akhir}) lebih kecil dari awal ({oddo_awal}). Yakin lanjut?",
                reply_markup=keyboard_oddo_konfirmasi(ODDO_PREFIX),
            )
            return ODDO_KONFIRMASI

        context.user_data["laporan_akhir"] = data_gabungan
        await pesan_proses.delete()
        await _tampilkan_preview(update, data_gabungan)
        return PREVIEW

    except ValueError as e:
        await pesan_proses.edit_text(
            f"❌ {e}\n\n"
            "Coba ketik ulang. Contoh: `oddo akhir 250, penanganan 2, estafet nihil`\n"
            "Batal: /cancel",
            parse_mode="Markdown",
        )
        return INPUT

    except (KeyError, TypeError) as e:
        logger.error("Smart Lapor Akhir gagal parsing: %s", e, exc_info=True)
        await pesan_proses.edit_text(
            "❌ AI mengembalikan data tidak lengkap.\n"
            "Pastikan oddo akhir disebutkan dengan jelas.\n"
            "Batal: /cancel"
        )
        return INPUT

    except Exception as e:
        logger.error("Smart Lapor Akhir gagal: %s", e, exc_info=True)
        await pesan_proses.edit_text(
            "❌ Terjadi kesalahan saat memproses AI.\n"
            "Coba lagi sebentar, atau pakai /lapor manual.\n"
            "Batal: /cancel"
        )
        return INPUT


async def konfirmasi_oddo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == f"{ODDO_PREFIX}:ulang":
        await query.edit_message_text(
            "Ketik ulang data akhir shift.\n"
            "Contoh: `oddo akhir 250, penanganan 2, estafet nihil`\n"
            "Batal: /cancel",
            parse_mode="Markdown",
        )
        return INPUT

    data = context.user_data.get("laporan_akhir")
    if not data:
        await query.edit_message_text("❌ Data laporan hilang. Mulai ulang dengan /smartlapor_akhir")
        return ConversationHandler.END

    pesan = _buat_pesan_laporan(data)
    await query.edit_message_text(
        "📋 *CEK DULU YA (data shift + input akhir):*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{pesan}",
        parse_mode="Markdown",
        reply_markup=keyboard_preview(PREVIEW_PREFIX),
    )
    return PREVIEW


async def handle_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == f"{PREVIEW_PREFIX}:batal":
        await query.edit_message_text("Smart Lapor Akhir dibatalkan. ❌")
        return ConversationHandler.END

    data = context.user_data.get("laporan_akhir")
    if not data:
        await query.edit_message_text("❌ Data laporan hilang. Mulai ulang dengan /smartlapor_akhir")
        return ConversationHandler.END

    user_id = update.effective_user.id
    hapus_sesi_shift(user_id)

    pesan = _buat_pesan_laporan(data)
    await query.edit_message_text(
        f"{pesan}\n\n"
        "✅ _Sesi shift dihapus. Buat laporan awal baru untuk shift berikutnya._",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Smart Lapor Akhir dibatalkan. ❌")
    else:
        await update.message.reply_text("Smart Lapor Akhir dibatalkan. ❌")
    return ConversationHandler.END


smartlapor_akhir_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("smartlapor_akhir", mulai_smartlapor_akhir)],
    states={
        INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_input_akhir)],
        ODDO_KONFIRMASI: [
            CallbackQueryHandler(konfirmasi_oddo, pattern=rf"^{ODDO_PREFIX}:"),
        ],
        PREVIEW: [CallbackQueryHandler(handle_preview, pattern=rf"^{PREVIEW_PREFIX}:")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)