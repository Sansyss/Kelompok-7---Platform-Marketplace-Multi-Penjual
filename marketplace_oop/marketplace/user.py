"""
User, Buyer, dan Seller.

Materi yang dipakai:
- Pert-01 : atribut private (__password)
- Pert-02 : Inheritance (Buyer & Seller mewarisi User) dan super().__init__()
- Pert-03 : Abstract class (SyaratUser) + multiple inheritance + overriding
            method tampilkanProfil() (polymorphism)
"""
import abc

from .exceptions import DataGandaError, AksesDitolakError
from .validator import cekNama, cekEmail, cekNoHP, cekPassword, cekTeks
from .produk import Toko
from .cart import Cart, Wishlist
from .utils import judul


class SyaratUser(metaclass=abc.ABCMeta):
    """Abstract class: syarat yang WAJIB dipenuhi setiap jenis user."""

    @property
    @abc.abstractmethod
    def peran(self):
        pass

    @abc.abstractmethod
    def tampilkanProfil(self):
        pass


class User:
    """Kelas induk: atribut yang sama antara Buyer dan Seller."""
    _jumlahUser = 0

    def __init__(self, nama, email, noHP, password):
        self.nama = cekNama(nama)
        self.email = cekEmail(email)
        self.noHP = cekNoHP(noHP)
        self.__password = cekPassword(password)     # private
        User._jumlahUser += 1
        self.idUser = f"U{User._jumlahUser:03d}"

    def login(self, password):
        return password == self.__password

    def gantiPassword(self, passwordLama, passwordBaru):
        if not self.login(passwordLama):
            raise AksesDitolakError("Password lama salah")
        self.__password = cekPassword(passwordBaru)

    def _infoDasar(self):
        print(f"ID User  : {self.idUser}")
        print(f"Nama     : {self.nama}")
        print(f"Email    : {self.email}")
        print(f"No HP    : {self.noHP}")


class Buyer(User, SyaratUser):
    def __init__(self, nama, email, noHP, password, alamat, kota):
        alamat = cekTeks(alamat, "Alamat")
        kota = cekNama(kota, "Kota").title()
        super().__init__(nama, email, noHP, password)     # memanggil __init__ kelas induk
        self.alamat = alamat
        self.kota = kota
        self.cart = Cart(self)
        self.wishlist = Wishlist(self)
        self.daftarOrder = []

    @property
    def peran(self):
        return "Buyer"

    def tampilkanProfil(self):                            # overriding (polymorphism)
        judul(f"PROFIL {self.peran.upper()}")
        self._infoDasar()
        print(f"Alamat   : {self.alamat}, {self.kota}")
        print(f"Keranjang: {len(self.cart)} jenis produk")
        print(f"Wishlist : {len(self.wishlist)} produk")
        print(f"Order    : {len(self.daftarOrder)} order")


class Seller(User, SyaratUser):
    def __init__(self, nama, email, noHP, password):
        super().__init__(nama, email, noHP, password)
        self.toko = None

    @property
    def peran(self):
        return "Seller"

    @property
    def tokoSaya(self):
        if self.toko is None:
            raise AksesDitolakError("Anda belum membuat toko. Buat toko terlebih dahulu")
        return self.toko

    def buatToko(self, namaToko, kota):
        if self.toko is not None:
            raise DataGandaError(f"{self.nama} sudah memiliki toko '{self.toko.namaToko}'")
        self.toko = Toko(namaToko, kota, self)
        return self.toko

    def tambahProduk(self, kode, nama, harga, stok, kategori, berat=500):
        return self.tokoSaya.tambahProduk(kode, nama, harga, stok, kategori, berat)

    def tampilkanProfil(self):                            # overriding (polymorphism)
        judul(f"PROFIL {self.peran.upper()}")
        self._infoDasar()
        if self.toko:
            print(f"Toko     : {self.toko.namaToko} ({self.toko.kota})")
            print(f"Produk   : {len(self.toko)} produk")
        else:
            print("Toko     : (belum membuat toko)")
