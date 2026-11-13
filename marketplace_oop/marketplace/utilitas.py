import re
from .exceptions import ValidasiError

def formatRupiah(angka):
    return "Rp " + f"{angka:,.0f}".replace(",", ".")

def wajibIsi(nilai, namaField):
    teks = str(nilai).strip()
    if not teks:
        raise ValidasiError(f"{namaField} tidak boleh kosong.")
    return teks

def validasiAngka(nilai, namaField, minimal=0, maksimal=None):
    try:
        angka = int(nilai)
    except (TypeError, ValueError):
        raise ValidasiError(f"{namaField} harus berupa bilangan bulat.") from None
    if angka < minimal:
        raise ValidasiError(f"{namaField} minimal {minimal}.")
    if maksimal is not None and angka > maksimal:
        raise ValidasiError(f"{namaField} maksimal {maksimal}.")
    return angka

def validasiUsername(username):
    username = wajibIsi(username, "Username")
    if not re.fullmatch(r"[A-Za-z0-9_]{4,20}", username):
        raise ValidasiError("Username 4-20 karakter, hanya huruf, angka, dan underscore.")
    return username

def validasiPassword(password):
    if len(str(password)) < 6:
        raise ValidasiError("Password minimal 6 karakter.")
    return str(password)

def validasiEmail(email):
    email = wajibIsi(email, "Email")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValidasiError("Format email tidak valid (contoh: nama@mail.com).")
    return email

def validasiNoHp(noHp):
    noHp = wajibIsi(noHp, "No HP")
    if not re.fullmatch(r"\+?\d{8,15}", noHp):
        raise ValidasiError("No HP hanya boleh angka (boleh diawali +) dengan panjang 8-15 digit.")
    return noHp
