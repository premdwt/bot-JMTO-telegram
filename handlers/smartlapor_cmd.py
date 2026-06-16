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

from handlers.konektika_client import parse_lapor_teks
from handlers.lapor_cmd import _buat_pesan_laporan
from handlers.shift_session import is_laporan_awal, simpan_sesi_shift
from handlers.smartlapor_helpers import ambil_angka, cek_rate_limit, keyboard_preview

logger = logging.getLogger(__name__)

INPUT, PREVIEW = range(2)
PREVIEW_PREFIX = "smartpreview"


def _seragamkan_kunci(data: dict) -> dict:
    peta_alias = {
        "mobil": ("mobil", "kendaraan", "unit"),
        "shift": ("shift",),
        "personil": ("personil", "petugas", "anggota"),
        "rc": ("rc", "jumlah_rc"),
        "rambu": ("rambu", "jumlah_rambu"),
        "rotator": ("rotator", "rotator_lampu"),
        "ban": ("ban",),
        "body": ("body", "kondisi_body"),
        "sirine": ("sirine",),
        "radio": ("radio", "radio_komunikasi"),
        "oddo_awal": ("oddo_awal", "oddoawal", "oddo_awal_km"),
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


def _normalisasi_data(data: dict) -> dict:
    data = _seragamkan_kunci(data)

    defaults = {
        "mobil": "JSM 211",
        "shift": "1",
        "rc": "0",
        "rambu": "0",
        "rotator": "Baik",
        "ban": "Baik",
        "body": "Baik",
        "sirine": "Baik",
        "radio": "Aman",
        "oddo_awal": "",
        "oddo_akhir": "0",
        "penanganan": "0",
        "estafet": "nihil",
    }

    hasil = {}
    for kunci, nilai_default in defaults.items():
        nilai = data.get(kunci, nilai_default)
        hasil[kunci] = str(nilai).strip() if nilai is not None else nilai_default

    personil = data.get("personil", "")
    if not personil or not str(personil).strip():
        raise ValueError("Personil wajib disebutkan dalam teks laporan")

    hasil["personil"] = str(personil).strip()

    mobil = hasil["mobil"].upper()
    if "212" in mobil:
        hasil["mobil"] = "JSM 212"
    else:
        hasil["mobil"] = "JSM 211"

    if hasil["shift"] not in {"1", "2", "3"}:
        raise ValueError("Shift harus 1, 2, atau 3")

    for kunci in ("oddo_awal", "oddo_akhir"):
        hasil[kunci] = ambil_angka(hasil[kunci])
        if not hasil[kunci].isdigit():
            raise ValueError(f"{kunci.replace('_', ' ').title()} wajib disebutkan dan harus angka")

    if hasil["penanganan"].lower() in {"nihil", "-", "tidak ada"}:
        hasil["penanganan"] = "0"

    return hasil


async def mulai_smartlapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Smart Lapor Awal (Beta)*\n\n"
        "Ceritakan laporan *awal shift* dalam satu pesan.\n"
        "AI akan menyusun format `/lapor` otomatis.\n\n"
        "Setelah dikirim, data shift tersimpan 10 jam\n"
        "untuk dipakai di /smartlapor\\_akhir.\n\n"
        "*Contoh:*\n"
        "`lapor awal shift 2 JSM 211, personil YY dan UU, "
        "rc 10 rambu 2, semua baik, oddo awal 189 oddo akhir 0, "
        "penanganan 0, estafet nihil`\n\n"
        "Ketik teks laporan kamu sekarang.\n"
        "Batal: /cancel",
        parse_mode="Markdown",
    )
    return INPUT


async def proses_input_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sisa = cek_rate_limit(user_id)
    if sisa:
        await update.message.reply_text(
            f"⏳ Tunggu {sisa} detik dulu sebelum pakai Smart Lapor lagi."
        )
        return INPUT

    teks = update.message.text.strip()
    if len(teks) < 10:
        await update.message.reply_text(
            "Teks terlalu pendek. Coba jelaskan laporan lebih lengkap, atau /cancel."
        )
        return INPUT

    pesan_proses = await update.message.reply_text("⏳ AI sedang menyusun laporan...")

    try:
        data_mentah = await parse_lapor_teks(teks)
        logger.info("Smart Lapor data AI: %s", data_mentah)
        data = _normalisasi_data(data_mentah)
        context.user_data.clear()
        context.user_data.update(data)

        pesan = _buat_pesan_laporan(context.user_data)
        await pesan_proses.delete()
        await update.message.reply_text(
            "📋 *CEK DULU YA (hasil AI):*\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"{pesan}",
            parse_mode="Markdown",
            reply_markup=keyboard_preview(PREVIEW_PREFIX),
        )
        return PREVIEW

    except ValueError as e:
        await pesan_proses.edit_text(
            f"❌ {e}\n\n"
            "Coba ketik ulang dengan lebih jelas, atau pakai /lapor manual.\n"
            "Batal: /cancel"
        )
        return INPUT

    except (KeyError, TypeError) as e:
        logger.error("Smart Lapor gagal parsing data AI: %s", e, exc_info=True)
        await pesan_proses.edit_text(
            "❌ AI mengembalikan data tidak lengkap.\n"
            "Coba ketik ulang dengan menyebut oddo awal & oddo akhir secara jelas.\n"
            "Contoh: `oddo awal 189 oddo akhir 0`\n"
            "Atau pakai /lapor manual. Batal: /cancel",
            parse_mode="Markdown",
        )
        return INPUT

    except Exception as e:
        logger.error("Smart Lapor gagal: %s", e, exc_info=True)
        await pesan_proses.edit_text(
            "❌ Terjadi kesalahan saat memproses AI.\n"
            "Coba lagi sebentar, atau pakai /lapor manual.\n"
            "Batal: /cancel"
        )
        return INPUT


async def handle_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == f"{PREVIEW_PREFIX}:batal":
        await query.edit_message_text("Smart Lapor dibatalkan. ❌")
        return ConversationHandler.END

    pesan = _buat_pesan_laporan(context.user_data)
    user_id = update.effective_user.id

    if is_laporan_awal(context.user_data):
        simpan_sesi_shift(user_id, context.user_data)
        pesan += (
            "\n\n💾 Data shift tersimpan 10 jam.\n"
            "Nanti akhir shift pakai /smartlapor\\_akhir"
        )

    await query.edit_message_text(pesan, parse_mode="Markdown")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Smart Lapor dibatalkan. ❌")
    else:
        await update.message.reply_text("Smart Lapor dibatalkan. ❌")
    return ConversationHandler.END


smartlapor_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("smartlapor", mulai_smartlapor)],
    states={
        INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_input_ai)],
        PREVIEW: [CallbackQueryHandler(handle_preview, pattern=rf"^{PREVIEW_PREFIX}:")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)