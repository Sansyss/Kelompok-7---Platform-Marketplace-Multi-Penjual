"""
Voucher dan Jasa Pengiriman (ongkir).

Materi yang dipakai:
- Pert-03 : Abstract class + Polymorphism.
  Satu method dengan nama sama (hitungDiskon / hitungOngkir) memiliki
  proses berbeda di setiap kelas turunan.
"""
import abc
import math

from .exceptions import VoucherError, ValidasiError
from .validator import cekTeks, cekBilanganBulat
from .utils import rupiah


# ============================== VOUCHER ==============================
class Voucher(metaclass=abc.ABCMeta):
    def __init__(self, kode, minBelanja=0, kuota=100):
        self.kode = cekTeks(kode, "Kode voucher").upper()
        self.minBelanja = cekBilanganBulat(minBelanja, "Minimal belanja", 0)
        self.kuota = cekBilanganBulat(kuota, "Kuota", 0)

    @property
    @abc.abstractmethod
    def keterangan(self):
        pass

    @abc.abstractmethod
    def hitungDiskon(self, subtotal):
        pass

    def terapkan(self, subtotal):
        """Memeriksa syarat voucher lalu mengembalikan besar diskon."""
        if self.kuota <= 0:
            raise VoucherError(f"Kuota voucher {self.kode} sudah habis")
        if subtotal < self.minBelanja:
            raise VoucherError(f"Voucher {self.kode} butuh minimal belanja "
                               f"{rupiah(self.minBelanja)} (belanja Anda {rupiah(subtotal)})")
        return min(self.hitungDiskon(subtotal), subtotal)

    def pakai(self):
        self.kuota -= 1


class VoucherPersen(Voucher):
    def __init__(self, kode, persen, maksDiskon=None, minBelanja=0, kuota=100):
        super().__init__(kode, minBelanja, kuota)
        self.persen = cekBilanganBulat(persen, "Persen diskon", 1)
        if self.persen > 100:
            raise ValidasiError("Persen diskon maksimal 100")
        self.maksDiskon = maksDiskon

    @property
    def keterangan(self):
        teks = f"Diskon {self.persen}%"
        if self.maksDiskon:
            teks += f" maks. {rupiah(self.maksDiskon)}"
        return teks + f", min. belanja {rupiah(self.minBelanja)}"

    def hitungDiskon(self, subtotal):
        diskon = subtotal * self.persen // 100
        return min(diskon, self.maksDiskon) if self.maksDiskon else diskon


class VoucherNominal(Voucher):
    def __init__(self, kode, nominal, minBelanja=0, kuota=100):
        super().__init__(kode, minBelanja, kuota)
        self.nominal = cekBilanganBulat(nominal, "Nominal diskon", 1)

    @property
    def keterangan(self):
        return f"Potongan {rupiah(self.nominal)}, min. belanja {rupiah(self.minBelanja)}"

    def hitungDiskon(self, subtotal):
        return self.nominal


# ========================== JASA PENGIRIMAN ==========================
class JasaPengiriman(metaclass=abc.ABCMeta):
    kode = ""
    nama = ""
    estimasi = ""

    @abc.abstractmethod
    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        pass

    @staticmethod
    def beratKg(beratGram):
        """Berat dibulatkan ke atas per kg, minimal 1 kg."""
        return max(1, math.ceil(beratGram / 1000))

    @staticmethod
    def dalamKota(kotaAsal, kotaTujuan):
        return kotaAsal.strip().lower() == kotaTujuan.strip().lower()

    def __str__(self):
        return f"{self.kode} - {self.nama} ({self.estimasi})"


class KurirReguler(JasaPengiriman):
    kode, nama, estimasi = "REG", "Reguler", "2-4 hari"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        tarif = 9000 if self.dalamKota(kotaAsal, kotaTujuan) else 18000
        return tarif * self.beratKg(beratGram)


class KurirExpress(JasaPengiriman):
    kode, nama, estimasi = "EXP", "Express", "1-2 hari"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        tarif = 15000 if self.dalamKota(kotaAsal, kotaTujuan) else 28000
        return tarif * self.beratKg(beratGram)


class KurirSameDay(JasaPengiriman):
    kode, nama, estimasi = "SDY", "Same Day", "sampai hari ini"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        if not self.dalamKota(kotaAsal, kotaTujuan):
            raise ValidasiError(f"Same Day hanya untuk pengiriman dalam kota "
                                f"(toko di {kotaAsal}, tujuan {kotaTujuan})")
        return 20000 + 5000 * (self.beratKg(beratGram) - 1)
