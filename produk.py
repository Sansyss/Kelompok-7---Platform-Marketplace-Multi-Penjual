from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count
from .exceptions import StokTidakCukupError, ValidasiError
from .utilitas import validasiAngka, wajibIsi

class Review:
    def __init__(self, buyer, rating, komentar):
        self.__buyer = buyer
        self.__rating = validasiAngka(rating, "Rating", 1, 5)
        self.__komentar = str(komentar).strip() or "-"
        self.__tanggal = datetime.now()

    @property
    def buyer(self):
        return self.__buyer

    @property
    def rating(self):
        return self.__rating

    @property
    def komentar(self):
        return self.__komentar

    @property
    def tanggal(self):
        return self.__tanggal

class Produk(ABC):
    _penghitungId = count(1)

    def __init__(self, nama, harga, stok, kategori, toko):
        self.nama = nama
        self.harga = harga
        self.stok = stok
        self.kategori = kategori
        self.__toko = toko
        self.__terjual = 0
        self.__daftarReview = []
        self.__id = next(Produk._penghitungId)

    @property
    def id(self):
        return self.__id

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        self.__nama = wajibIsi(nilai, "Nama produk")

    @property
    def harga(self):
        return self.__harga

    @harga.setter
    def harga(self, nilai):
        self.__harga = validasiAngka(nilai, "Harga", 1)

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        self.__stok = validasiAngka(nilai, "Stok", 0)

    @property
    def kategori(self):
        return self.__kategori

    @kategori.setter
    def kategori(self, nilai):
        self.__kategori = wajibIsi(nilai, "Kategori").title()

    @property
    def toko(self):
        return self.__toko

    @property
    def terjual(self):
        return self.__terjual

    @property
    def daftarReview(self):
        return tuple(self.__daftarReview)

    @property
    def rataRating(self):
        if not self.__daftarReview:
            return 0.0
        return round(sum(r.rating for r in self.__daftarReview) / len(self.__daftarReview), 1)

    def kurangiStok(self, jumlah):
        if jumlah > self.__stok:
            raise StokTidakCukupError(self.__nama, self.__stok, jumlah)
        self.__stok -= jumlah
        self.__terjual += jumlah

    def kembalikanStok(self, jumlah):
        self.__stok += jumlah
        self.__terjual -= jumlah

    def sudahDireviewOleh(self, buyer):
        return any(r.buyer is buyer for r in self.__daftarReview)

    def tambahReview(self, review):
        if self.sudahDireviewOleh(review.buyer):
            raise ValidasiError("Anda sudah memberi review untuk produk ini.")
        self.__daftarReview.append(review)

    @property
    @abstractmethod
    def jenis(self):
        pass

    @abstractmethod
    def beratTotal(self, jumlah):
        pass

    @abstractmethod
    def infoTambahan(self):
        pass

    def __str__(self):
        return f"[{self.id}] {self.nama}"

class ProdukFisik(Produk):
    def __init__(self, nama, harga, stok, kategori, toko, beratGram):
        super().__init__(nama, harga, stok, kategori, toko)
        self.beratGram = beratGram

    @property
    def beratGram(self):
        return self.__beratGram

    @beratGram.setter
    def beratGram(self, nilai):
        self.__beratGram = validasiAngka(nilai, "Berat (gram)", 1)

    @property
    def jenis(self):
        return "Fisik"

    def beratTotal(self, jumlah):
        return self.__beratGram * jumlah

    def infoTambahan(self):
        return f"Berat {self.__beratGram} gram, dikirim lewat kurir"

class ProdukDigital(Produk):
    def __init__(self, nama, harga, stok, kategori, toko, formatFile):
        super().__init__(nama, harga, stok, kategori, toko)
        self.formatFile = formatFile

    @property
    def formatFile(self):
        return self.__formatFile

    @formatFile.setter
    def formatFile(self, nilai):
        self.__formatFile = wajibIsi(nilai, "Format file").upper()

    @property
    def jenis(self):
        return "Digital"

    def beratTotal(self, jumlah):
        return 0

    def infoTambahan(self):
        return f"File {self.__formatFile}, dikirim lewat email (tanpa ongkir)"
