"""
Kumpulan fungsi pengecekan data (Pert-04: Exception).
Setiap fungsi melakukan `raise ValidasiError(...)` dengan pesan buatan sendiri
apabila data tidak sesuai aturan, lalu ditangkap dengan try/except oleh pemanggil.
"""
from .exceptions import ValidasiError

HURUF_KAPITAL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ANGKA = "0123456789"


def cekTeks(teks, label="Teks"):
    """Teks tidak boleh kosong."""
    if not isinstance(teks, str) or not teks.strip():
        raise ValidasiError(f"{label} tidak boleh kosong")
    return teks.strip()


def cekNama(nama, label="Nama"):
    """Nama hanya boleh terdiri dari huruf dan spasi (boleh titik/apostrof)."""
    nama = cekTeks(nama, label)
    for karakter in nama:
        if not (karakter.isalpha() or karakter in " .'-"):
            raise ValidasiError(f"{label} hanya boleh berisi huruf dan spasi")
    return nama


def cekEmail(email):
    email = cekTeks(email, "Email").lower()
    pesan = "Format email tidak valid (contoh: nama@email.com)"
    if " " in email or email.count("@") != 1:
        raise ValidasiError(pesan)
    lokal, domain = email.split("@")
    if not lokal or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValidasiError(pesan)
    return email


def cekNoHP(noHP):
    """No HP: hanya angka dan '+' (di depan), panjang 8 - 15 karakter."""
    noHP = cekTeks(noHP, "No HP")
    for i, karakter in enumerate(noHP):
        if karakter not in ANGKA and not (karakter == "+" and i == 0):
            raise ValidasiError("No HP hanya boleh berisi angka (tanda '+' hanya di awal)")
    if not 8 <= len(noHP) <= 15:
        raise ValidasiError("Panjang No HP harus 8 sampai 15 karakter")
    return noHP


def cekPassword(password):
    if not isinstance(password, str) or len(password) < 6:
        raise ValidasiError("Password minimal 6 karakter")
    return password


def cekKodeProduk(kode):
    """Kode produk: huruf kapital dan angka saja, tepat 6 karakter (contoh: ELK001)."""
    kode = cekTeks(kode, "Kode produk").upper()
    jumlahValid = 0
    for karakter in kode:
        if karakter in HURUF_KAPITAL or karakter in ANGKA:
            jumlahValid += 1
    if jumlahValid != len(kode):
        raise ValidasiError("Kode produk hanya boleh berisi huruf dan angka")
    if len(kode) != 6:
        raise ValidasiError("Panjang kode produk harus 6 karakter (contoh: ELK001)")
    return kode


def cekBilanganBulat(nilai, label, minimal=0):
    """Nilai harus bilangan bulat (int) dan >= minimal."""
    if isinstance(nilai, bool) or not isinstance(nilai, int):
        raise ValidasiError(f"{label} harus berupa bilangan bulat")
    if nilai < minimal:
        raise ValidasiError(f"{label} minimal {minimal}")
    return nilai
