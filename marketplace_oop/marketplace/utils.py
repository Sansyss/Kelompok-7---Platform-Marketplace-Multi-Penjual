"""Fungsi bantu untuk tampilan di terminal."""

LEBAR = 72


def rupiah(nilai):
    """Format angka menjadi Rupiah, contoh: 150000 -> Rp150.000"""
    return "Rp" + f"{nilai:,.0f}".replace(",", ".")


def garis(karakter="-", panjang=LEBAR):
    print(karakter * panjang)


def judul(teks, karakter="="):
    garis(karakter)
    print(teks.center(LEBAR))
    garis(karakter)
