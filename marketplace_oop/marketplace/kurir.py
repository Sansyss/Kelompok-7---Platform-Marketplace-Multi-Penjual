import math
from abc import ABC, abstractmethod

class Kurir(ABC):
    @property
    @abstractmethod
    def nama(self):
        pass

    @property
    @abstractmethod
    def estimasi(self):
        pass

    @abstractmethod
    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        pass

    @staticmethod
    def _beratKg(beratGram):
        return math.ceil(beratGram / 1000) if beratGram > 0 else 0

    @staticmethod
    def _luarKota(kotaAsal, kotaTujuan):
        return kotaAsal.strip().lower() != kotaTujuan.strip().lower()

class KurirReguler(Kurir):
    TARIF_PER_KG = 9000
    BIAYA_LUAR_KOTA = 6000

    @property
    def nama(self):
        return "Reguler"

    @property
    def estimasi(self):
        return "2-4 hari"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        kg = self._beratKg(beratGram)
        if kg == 0:
            return 0
        biaya = kg * self.TARIF_PER_KG
        if self._luarKota(kotaAsal, kotaTujuan):
            biaya += self.BIAYA_LUAR_KOTA
        return biaya

class KurirEkspres(Kurir):
    TARIF_PER_KG = 16000
    BIAYA_LUAR_KOTA = 10000

    @property
    def nama(self):
        return "Ekspres"

    @property
    def estimasi(self):
        return "1 hari"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        kg = self._beratKg(beratGram)
        if kg == 0:
            return 0
        biaya = kg * self.TARIF_PER_KG
        if self._luarKota(kotaAsal, kotaTujuan):
            biaya += self.BIAYA_LUAR_KOTA
        return biaya

class AmbilDiToko(Kurir):
    @property
    def nama(self):
        return "Ambil di Toko"

    @property
    def estimasi(self):
        return "Diambil pembeli"

    def hitungOngkir(self, beratGram, kotaAsal, kotaTujuan):
        return 0

DAFTAR_KURIR = (KurirReguler(), KurirEkspres(), AmbilDiToko())
