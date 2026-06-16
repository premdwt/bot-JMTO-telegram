import json
import re

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, AuthenticationError

from config import KONEKTIKA_API_KEY, KONEKTIKA_BASE_URL, KONEKTIKA_MODEL

LAPOR_SYSTEM_PROMPT = """Kamu parser laporan serah terima shift JMTO Ruas JSM.
Tugasmu: ubah teks bebas pengguna menjadi JSON terstruktur.

Balas HANYA JSON valid tanpa markdown, tanpa penjelasan tambahan.

Format JSON wajib:
{
  "mobil": "JSM 211 atau JSM 212",
  "shift": "1 atau 2 atau 3",
  "personil": "nama dipisah koma, contoh: Ade, Amirul",
  "rc": "angka jumlah RC",
  "rambu": "angka jumlah rambu",
  "rotator": "kondisi rotator & lampu",
  "ban": "kondisi ban",
  "body": "kondisi body",
  "sirine": "kondisi sirine",
  "radio": "kondisi radio komunikasi",
  "oddo_awal": "angka oddo awal",
  "oddo_akhir": "angka oddo akhir, 0 jika laporan awal tugas",
  "penanganan": "jumlah penanganan",
  "estafet": "status estafet"
}

Aturan:
- mobil harus JSM 211 atau JSM 212 (default JSM 211 jika tidak jelas)
- shift harus 1, 2, atau 3
- jika kondisi kendaraan tidak disebut, isi: Baik, Baik, Baik, Baik, Aman
- jika rc/rambu/penanganan tidak disebut, isi "0"
- jika estafet tidak disebut, isi "nihil"
- oddo_awal dan oddo_akhir wajib angka string
- personil wajib diisi dari teks pengguna"""

LAPOR_AKHIR_SYSTEM_PROMPT = """Kamu parser laporan akhir shift JMTO Ruas JSM.
Tugasmu: ubah teks singkat pengguna menjadi JSON terstruktur.

Balas HANYA JSON valid tanpa markdown, tanpa penjelasan tambahan.

Format JSON wajib:
{
  "oddo_akhir": "angka oddo akhir",
  "penanganan": "jumlah penanganan",
  "estafet": "status estafet"
}

Aturan:
- oddo_akhir wajib angka string dan harus lebih dari 0
- jika penanganan tidak disebut, isi "0"
- jika estafet tidak disebut, isi "nihil"
- penanganan "nihil" diubah menjadi "0"
"""


async def _panggil_konektika(system_prompt: str, teks_pengguna: str) -> dict:
    if not KONEKTIKA_API_KEY:
        raise ValueError("API key Konektika belum diisi di config.py")

    client = AsyncOpenAI(
        api_key=KONEKTIKA_API_KEY,
        base_url=KONEKTIKA_BASE_URL,
        timeout=120.0,
    )

    try:
        response = await client.chat.completions.create(
            model=KONEKTIKA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": teks_pengguna},
            ],
        )
    except AuthenticationError as e:
        raise ValueError("API key Konektika tidak valid. Cek isian di config.py.") from e
    except APIConnectionError as e:
        raise ValueError("Koneksi ke Konektika gagal. Cek internet lalu coba lagi.") from e
    except APIStatusError as e:
        if e.status_code == 429:
            raise ValueError("Kuota Konektika habis atau terlalu banyak request. Coba lagi nanti.") from e
        raise ValueError(f"Konektika menolak request (HTTP {e.status_code}).") from e

    isi = response.choices[0].message.content
    if not isi:
        raise ValueError("AI tidak mengembalikan respons")

    return _ekstrak_json(isi)


def _ekstrak_json(teks: str) -> dict:
    teks = teks.strip()
    if teks.startswith("```"):
        teks = re.sub(r"^```(?:json)?\s*", "", teks)
        teks = re.sub(r"\s*```$", "", teks)

    try:
        return json.loads(teks)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", teks, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("AI mengembalikan format yang tidak bisa dibaca. Coba ketik ulang lebih jelas.")


async def parse_lapor_teks(teks_pengguna: str) -> dict:
    return await _panggil_konektika(LAPOR_SYSTEM_PROMPT, teks_pengguna)


async def parse_lapor_akhir_teks(teks_pengguna: str) -> dict:
    return await _panggil_konektika(LAPOR_AKHIR_SYSTEM_PROMPT, teks_pengguna)