from abc import ABC, abstractmethod
from .exceptions import AksesDitolakError, DataTidakDitemukanError, ValidasiError
from .keranjang import Keranjang
from .toko import Toko
from .utilitas import validasiEmail, validasiNoHp, validasiPassword, validasiUsername, wajibIsi

class Pengguna(ABC):
    def __init__(self, username, password, nama, email, noHp, kota):
        self.__username = validasiUsername(username)
        self.__password = validasiPassword(password)
        self.nama = nama
        self.email = email
        self.noHp = noHp
        self.kota = kota

    @property
    def username(self):
        return self.__username

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        self.__nama = wajibIsi(nilai, "Nama")

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, nilai):
        self.__email = validasiEmail(nilai)

    @property
    def noHp(self):
        return self.__noHp

    @noHp.setter
    def noHp(self, nilai):
        self.__noHp = validasiNoHp(nilai)

    @property
    def kota(self):
        return self.__kota

    @kota.setter
    def kota(self, nilai):
        self.__kota = wajibIsi(nilai, "Kota").title()

    def cekPassword(self, password):
        return self.__password == password

    @property
    @abstractmethod
    def peran(self):
        pass

    @abstractmethod
    def daftarOrderTerkait(self):
        pass

    def infoProfil(self):
        return [
            ("Peran", self.peran),
            ("Username", self.__username),
            ("Nama", self.__nama),
            ("Email", self.__email),
            ("No HP", self.__noHp),
            ("Kota", self.__kota),
        ]

    def __str__(self):
        return f"{self.__nama} ({self.peran})"

class Buyer(Pengguna):
    def __init__(self, username, password, nama, email, noHp, kota, alamat):
        super().__init__(username, password, nama, email, noHp, kota)
        self.alamat = alamat
        self.__keranjang = Keranjang()
        self.__wishlist = []
        self.__daftarOrder = []

    @property
    def peran(self):
        return "Buyer"

    @property
    def alamat(self):
        return self.__alamat

    @alamat.setter
    def alamat(self, nilai):
        self.__alamat = wajibIsi(nilai, "Alamat")

    @property
    def keranjang(self):
        return self.__keranjang

    @property
    def wishlist(self):
        return tuple(self.__wishlist)

    def tambahWishlist(self, produk):
        if produk in self.__wishlist:
            raise ValidasiError(f"'{produk.nama}' sudah ada di wishlist.")
        self.__wishlist.append(produk)

    def hapusWishlist(self, produk):
        if produk not in self.__wishlist:
            raise DataTidakDitemukanError(f"'{produk.nama}' tidak ada di wishlist.")
        self.__wishlist.remove(produk)

    def catatOrder(self, order):
        self.__daftarOrder.append(order)

    def daftarOrderTerkait(self):
        return tuple(self.__daftarOrder)

    def infoProfil(self):
        return super().infoProfil() + [
            ("Alamat", self.__alamat),
            ("Isi keranjang", f"{len(self.__keranjang)} produk"),
            ("Wishlist", f"{len(self.__wishlist)} produk"),
            ("Total pesanan", f"{len(self.__daftarOrder)} order"),
        ]

class Seller(Pengguna):
    def __init__(self, username, password, nama, email, noHp, kota):
        super().__init__(username, password, nama, email, noHp, kota)
        self.__toko = None

    @property
    def peran(self):
        return "Seller"

    @property
    def toko(self):
        return self.__toko

    def buatToko(self, namaToko):
        if self.__toko is not None:
            raise ValidasiError(f"Anda sudah memiliki toko '{self.__toko.nama}'.")
        self.__toko = Toko(namaToko, self)
        return self.__toko

    def wajibPunyaToko(self):
        if self.__toko is None:
            raise AksesDitolakError("Buat toko terlebih dahulu.")
        return self.__toko

    def daftarOrderTerkait(self):
        return self.__toko.daftarOrder if self.__toko else ()

    def infoProfil(self):
        return super().infoProfil() + [
            ("Toko", self.__toko.nama if self.__toko else "- (belum ada)"),
            ("Jumlah produk", f"{len(self.__toko) if self.__toko else 0} produk"),
            ("Pesanan masuk", f"{len(self.daftarOrderTerkait())} order"),
        ]
