"""
Keranjang belanja (Cart) dan Wishlist.

Materi yang dipakai:
- Pert-06 : dict (cart), set (wishlist), list/set/dict comprehension
- Pert-04 : raise StokTidakCukupError ketika stok tidak mencukupi
"""
from .exceptions import (StokTidakCukupError, DataGandaError,
                         DataTidakDitemukanError)
from .validator import cekBilanganBulat
from .utils import rupiah, garis


class ItemCart:
    def __init__(self, produk, jumlah):
        self.produk = produk
        self.jumlah = jumlah

    @property
    def subtotal(self):
        return self.produk.harga * self.jumlah


class Cart:
    def __init__(self, pemilik):
        self.pemilik = pemilik
        self.items = {}             # dict  {kodeProduk: ItemCart}

    def tambah(self, produk, jumlah=1):
        cekBilanganBulat(jumlah, "Jumlah", 1)
        sudahAda = self.items[produk.kode].jumlah if produk.kode in self.items else 0
        if sudahAda + jumlah > produk.stok:
            raise StokTidakCukupError(produk.nama, produk.stok, sudahAda + jumlah)
        if produk.kode in self.items:
            self.items[produk.kode].jumlah += jumlah
        else:
            self.items[produk.kode] = ItemCart(produk, jumlah)

    def _ambil(self, kode):
        kode = str(kode).strip().upper()
        if kode not in self.items:
            raise DataTidakDitemukanError(f"Produk {kode} tidak ada di keranjang")
        return kode

    def ubahJumlah(self, kode, jumlahBaru):
        kode = self._ambil(kode)
        cekBilanganBulat(jumlahBaru, "Jumlah", 0)
        if jumlahBaru == 0:
            del self.items[kode]
            return
        produk = self.items[kode].produk
        if jumlahBaru > produk.stok:
            raise StokTidakCukupError(produk.nama, produk.stok, jumlahBaru)
        self.items[kode].jumlah = jumlahBaru

    def hapus(self, kode):
        del self.items[self._ambil(kode)]

    def kosongkan(self):
        self.items.clear()

    @property
    def kosong(self):
        return len(self.items) == 0

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.values())

    def __iter__(self):
        return iter(list(self.items.values()))

    def __len__(self):
        return len(self.items)

    def kelompokkanPerToko(self):
        """Mengelompokkan item berdasarkan toko (seller) -> dasar Order per seller.
        Memakai set comprehension + dict comprehension + list comprehension."""
        semuaItem = list(self.items.values())
        daftarToko = {item.produk.toko for item in semuaItem}          # set comprehension
        daftarToko = sorted(daftarToko, key=lambda t: t.namaToko)
        return {toko: [item for item in semuaItem if item.produk.toko is toko]
                for toko in daftarToko}                                  # dict comprehension

    def tampilkan(self):
        garis()
        print(f"KERANJANG BELANJA - {self.pemilik.nama}")
        garis()
        if self.kosong:
            print("  (keranjang kosong)")
            return
        for toko, items in self.kelompokkanPerToko().items():
            print(f"  Toko: {toko.namaToko} ({toko.kota})")
            for item in items:
                print(f"    [{item.produk.kode}] {item.produk.nama[:24]:<24} "
                      f"{item.jumlah:>3} x {rupiah(item.produk.harga):>11} = "
                      f"{rupiah(item.subtotal):>12}")
        garis()
        print(f"  {'Total belanja (belum termasuk ongkir)':<56}{rupiah(self.total):>12}")


class Wishlist:
    def __init__(self, pemilik):
        self.pemilik = pemilik
        self.produk = set()         # set -> produk tidak mungkin dobel

    def tambah(self, produk):
        if produk in self.produk:
            raise DataGandaError(f"'{produk.nama}' sudah ada di wishlist")
        self.produk.add(produk)

    def _cari(self, kode):
        kode = str(kode).strip().upper()
        for produk in self.produk:
            if produk.kode == kode:
                return produk
        raise DataTidakDitemukanError(f"Produk {kode} tidak ada di wishlist")

    def hapus(self, kode):
        self.produk.remove(self._cari(kode))

    def pindahkanKeCart(self, kode, cart, jumlah=1):
        produk = self._cari(kode)
        cart.tambah(produk, jumlah)        # jika stok kurang -> exception, wishlist tetap
        self.produk.remove(produk)
        return produk

    def __iter__(self):
        return iter(sorted(self.produk, key=lambda p: p.nama))

    def __len__(self):
        return len(self.produk)

    def tampilkan(self):
        garis()
        print(f"WISHLIST - {self.pemilik.nama}")
        garis()
        if not self.produk:
            print("  (wishlist kosong)")
            return
        for produk in self:
            status = "tersedia" if produk.stok > 0 else "STOK HABIS"
            print(f"  {produk.baris()}  ({status})")
