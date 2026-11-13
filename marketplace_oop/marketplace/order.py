from datetime import datetime
from enum import Enum
from itertools import count
from .exceptions import StatusOrderError

class StatusOrder(Enum):
    MENUNGGU = "Menunggu Konfirmasi"
    DIPROSES = "Diproses"
    DIKIRIM = "Dikirim"
    SELESAI = "Selesai"
    DIBATALKAN = "Dibatalkan"

TRANSISI_STATUS = {
    StatusOrder.MENUNGGU: (StatusOrder.DIPROSES, StatusOrder.DIBATALKAN),
    StatusOrder.DIPROSES: (StatusOrder.DIKIRIM, StatusOrder.DIBATALKAN),
    StatusOrder.DIKIRIM: (StatusOrder.SELESAI,),
    StatusOrder.SELESAI: (),
    StatusOrder.DIBATALKAN: (),
}

def hitungBiaya(items, kotaAsal, kotaTujuan, kurir, voucher=None):
    subtotal = sum(item.produk.harga * item.jumlah for item in items)
    berat = sum(item.produk.beratTotal(item.jumlah) for item in items)
    ongkir = kurir.hitungOngkir(berat, kotaAsal, kotaTujuan)
    potongan = voucher.hitungPotongan(subtotal, ongkir) if voucher else 0
    return subtotal, ongkir, potongan

class ItemOrder:
    def __init__(self, produk, jumlah):
        self.__produk = produk
        self.__namaProduk = produk.nama
        self.__harga = produk.harga
        self.__jumlah = jumlah

    @property
    def produk(self):
        return self.__produk

    @property
    def namaProduk(self):
        return self.__namaProduk

    @property
    def harga(self):
        return self.__harga

    @property
    def jumlah(self):
        return self.__jumlah

    @property
    def subtotal(self):
        return self.__harga * self.__jumlah

class Order:
    _penghitungId = count(1)

    def __init__(self, buyer, toko, itemsKeranjang, kurir, voucher=None):
        _, ongkir, potongan = hitungBiaya(itemsKeranjang, toko.kota, buyer.kota, kurir, voucher)
        self.__id = f"ORD-{next(Order._penghitungId):04d}"
        self.__buyer = buyer
        self.__toko = toko
        self.__items = [ItemOrder(item.produk, item.jumlah) for item in itemsKeranjang]
        self.__kurir = kurir
        self.__voucher = voucher
        self.__ongkir = ongkir
        self.__potongan = potongan
        self.__tanggal = datetime.now()
        self.__status = StatusOrder.MENUNGGU
        self.__riwayat = [(StatusOrder.MENUNGGU, self.__tanggal)]

    @property
    def id(self):
        return self.__id

    @property
    def buyer(self):
        return self.__buyer

    @property
    def toko(self):
        return self.__toko

    @property
    def kurir(self):
        return self.__kurir

    @property
    def voucher(self):
        return self.__voucher

    @property
    def ongkir(self):
        return self.__ongkir

    @property
    def potongan(self):
        return self.__potongan

    @property
    def tanggal(self):
        return self.__tanggal

    @property
    def status(self):
        return self.__status

    @property
    def riwayat(self):
        return tuple(self.__riwayat)

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self)

    @property
    def total(self):
        return self.subtotal + self.__ongkir - self.__potongan

    @property
    def jumlahBarang(self):
        return sum(item.jumlah for item in self)

    def __iter__(self):
        return iter(self.__items)

    def statusBerikutnya(self):
        return TRANSISI_STATUS[self.__status]

    def ubahStatus(self, statusBaru):
        if statusBaru not in TRANSISI_STATUS[self.__status]:
            raise StatusOrderError(self.__status, statusBaru)
        if statusBaru is StatusOrder.DIBATALKAN:
            for item in self:
                item.produk.kembalikanStok(item.jumlah)
            if self.__voucher is not None:
                self.__voucher.kembalikan()
        self.__status = statusBaru
        self.__riwayat.append((statusBaru, datetime.now()))
