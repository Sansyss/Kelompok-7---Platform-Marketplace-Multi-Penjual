from .exceptions import DataTidakDitemukanError, StokTidakCukupError
from .utilitas import validasiAngka

class ItemKeranjang:
    def __init__(self, produk, jumlah):
        self.__produk = produk
        self.jumlah = jumlah

    @property
    def produk(self):
        return self.__produk

    @property
    def jumlah(self):
        return self.__jumlah

    @jumlah.setter
    def jumlah(self, nilai):
        nilai = validasiAngka(nilai, "Jumlah", 1)
        if nilai > self.__produk.stok:
            raise StokTidakCukupError(self.__produk.nama, self.__produk.stok, nilai)
        self.__jumlah = nilai

    @property
    def subtotal(self):
        return self.__produk.harga * self.__jumlah

class Keranjang:
    def __init__(self):
        self.__items = {}

    def __iter__(self):
        yield from self.__items.values()

    def __len__(self):
        return len(self.__items)

    def __ambil(self, idProduk):
        if idProduk not in self.__items:
            raise DataTidakDitemukanError(f"Produk dengan ID {idProduk} tidak ada di keranjang.")
        return self.__items[idProduk]

    def tambah(self, produk, jumlah):
        jumlah = validasiAngka(jumlah, "Jumlah", 1)
        if produk.id in self.__items:
            item = self.__items[produk.id]
            item.jumlah = item.jumlah + jumlah
        else:
            self.__items[produk.id] = ItemKeranjang(produk, jumlah)

    def ubahJumlah(self, idProduk, jumlah):
        self.__ambil(idProduk).jumlah = jumlah

    def hapus(self, idProduk):
        self.__ambil(idProduk)
        del self.__items[idProduk]

    def kosongkan(self):
        self.__items.clear()

    @property
    def total(self):
        return sum(item.subtotal for item in self)

    def kelompokPerToko(self):
        kelompok = {}
        for item in self:
            kelompok.setdefault(item.produk.toko, []).append(item)
        return kelompok
