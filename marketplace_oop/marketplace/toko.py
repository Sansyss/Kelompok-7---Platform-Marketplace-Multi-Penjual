from .exceptions import DataTidakDitemukanError, ValidasiError, VoucherTidakValidError
from .iterator import ProdukIterator
from .utilitas import wajibIsi

class Toko:
    def __init__(self, nama, pemilik):
        self.nama = nama
        self.__pemilik = pemilik
        self.__daftarProduk = []
        self.__daftarOrder = []
        self.__daftarVoucher = {}

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        self.__nama = wajibIsi(nilai, "Nama toko")

    @property
    def pemilik(self):
        return self.__pemilik

    @property
    def kota(self):
        return self.__pemilik.kota

    def __iter__(self):
        return ProdukIterator(self.__daftarProduk)

    def __len__(self):
        return len(self.__daftarProduk)

    def produkTersedia(self):
        return ProdukIterator(self.__daftarProduk, hanyaTersedia=True)

    def tambahProduk(self, produk):
        if produk.toko is not self:
            raise ValidasiError("Produk harus dibuat untuk toko ini.")
        self.__daftarProduk.append(produk)
        return produk

    def cariProduk(self, idProduk):
        for produk in self:
            if produk.id == idProduk:
                return produk
        raise DataTidakDitemukanError(f"Produk dengan ID {idProduk} tidak ada di toko {self.__nama}.")

    def tambahVoucher(self, voucher):
        if voucher.kode in self.__daftarVoucher:
            raise ValidasiError(f"Kode voucher {voucher.kode} sudah ada.")
        self.__daftarVoucher[voucher.kode] = voucher
        return voucher

    def ambilVoucher(self, kode):
        voucher = self.__daftarVoucher.get(str(kode).strip().upper())
        if voucher is None:
            raise VoucherTidakValidError(f"Voucher '{kode}' tidak berlaku di toko {self.__nama}.")
        return voucher

    @property
    def daftarVoucher(self):
        return tuple(self.__daftarVoucher.values())

    def catatOrder(self, order):
        self.__daftarOrder.append(order)

    @property
    def daftarOrder(self):
        return tuple(self.__daftarOrder)

    def orderBerstatus(self, status=None):
        for order in self.__daftarOrder:
            if status is None or order.status is status:
                yield order

    def __str__(self):
        return f"{self.__nama} ({self.kota})"
