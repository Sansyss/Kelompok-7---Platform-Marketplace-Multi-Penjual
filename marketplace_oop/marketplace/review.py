"""Ulasan (review) produk oleh buyer."""
from datetime import datetime

from .exceptions import ValidasiError


class Review:
    def __init__(self, buyer, produk, rating, komentar=""):
        if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValidasiError("Rating harus bilangan bulat 1 sampai 5")
        self.buyer = buyer
        self.produk = produk
        self.rating = rating
        self.komentar = (komentar or "").strip()
        self.tanggal = datetime.now().strftime("%d-%m-%Y")

    def __str__(self):
        bintang = "*" * self.rating + "." * (5 - self.rating)
        return f"[{bintang}] {self.buyer.nama}: {self.komentar or '-'} ({self.tanggal})"
