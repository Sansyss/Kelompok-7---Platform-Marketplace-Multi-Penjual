from abc import ABC, abstractmethod
from .exceptions import VoucherTidakValidError
from .utilitas import formatRupiah, validasiAngka, wajibIsi

class Voucher(ABC):
    def __init__(self, kode, minBelanja=0, kuota=10):
        self.__kode = wajibIsi(kode, "Kode voucher").upper()
        self.__minBelanja = validasiAngka(minBelanja, "Minimal belanja", 0)
        self.__kuota = validasiAngka(kuota, "Kuota", 1)

    @property
    def kode(self):
        return self.__kode

    @property
    def minBelanja(self):
        return self.__minBelanja

    @property
    def kuota(self):
        return self.__kuota

    def validasi(self, subtotal):
        if self.__kuota <= 0:
            raise VoucherTidakValidError(f"Kuota voucher {self.__kode} sudah habis.")
        if subtotal < self.__minBelanja:
            raise VoucherTidakValidError(
                f"Voucher {self.__kode} butuh minimal belanja {formatRupiah(self.__minBelanja)}.")

    def pakai(self):
        self.__kuota -= 1

    def kembalikan(self):
        self.__kuota += 1

    @property
    @abstractmethod
    def jenis(self):
        pass

    @abstractmethod
    def hitungPotongan(self, subtotal, ongkir):
        pass

    @abstractmethod
    def deskripsi(self):
        pass

class VoucherPersen(Voucher):
    def __init__(self, kode, persen, maksPotongan, minBelanja=0, kuota=10):
        super().__init__(kode, minBelanja, kuota)
        self.__persen = validasiAngka(persen, "Persen diskon", 1, 100)
        self.__maksPotongan = validasiAngka(maksPotongan, "Maksimal potongan", 1)

    @property
    def jenis(self):
        return "Diskon Persen"

    def hitungPotongan(self, subtotal, ongkir):
        return min(subtotal * self.__persen // 100, self.__maksPotongan)

    def deskripsi(self):
        return f"Diskon {self.__persen}% maks. {formatRupiah(self.__maksPotongan)}"

class VoucherNominal(Voucher):
    def __init__(self, kode, nominal, minBelanja=0, kuota=10):
        super().__init__(kode, minBelanja, kuota)
        self.__nominal = validasiAngka(nominal, "Nominal potongan", 1)

    @property
    def jenis(self):
        return "Potongan Nominal"

    def hitungPotongan(self, subtotal, ongkir):
        return min(self.__nominal, subtotal)

    def deskripsi(self):
        return f"Potongan {formatRupiah(self.__nominal)}"

class VoucherGratisOngkir(Voucher):
    def __init__(self, kode, maksPotongan, minBelanja=0, kuota=10):
        super().__init__(kode, minBelanja, kuota)
        self.__maksPotongan = validasiAngka(maksPotongan, "Maksimal potongan ongkir", 1)

    @property
    def jenis(self):
        return "Gratis Ongkir"

    def hitungPotongan(self, subtotal, ongkir):
        return min(ongkir, self.__maksPotongan)

    def deskripsi(self):
        return f"Gratis ongkir maks. {formatRupiah(self.__maksPotongan)}"
