import csv
import os
from .exceptions import (AksesDitolakError, AutentikasiError, DataTidakDitemukanError,
                         KeranjangKosongError, MarketplaceError, StokTidakCukupError, ValidasiError)
from .iterator import KatalogIterator
from .kurir import DAFTAR_KURIR
from .order import Order, StatusOrder
from .pengguna import Buyer, Seller
from .produk import Review
from .utilitas import validasiUsername

URUTAN_PRODUK = {
    "harga_termurah": (lambda p: p.harga, False),
    "harga_termahal": (lambda p: p.harga, True),
    "nama": (lambda p: p.nama.lower(), False),
    "rating": (lambda p: p.rataRating, True),
    "terlaris": (lambda p: p.terjual, True),
}

class Marketplace:
    def __init__(self, nama):
        self.nama = nama
        self.__pengguna = {}
        self.__daftarToko = []
        self.__daftarOrder = []

    def cekUsernameTersedia(self, username):
        username = validasiUsername(username)
        if username.lower() in self.__pengguna:
            raise ValidasiError(f"Username '{username}' sudah dipakai.")
        return username

    def __simpanPengguna(self, pengguna):
        self.__pengguna[pengguna.username.lower()] = pengguna
        return pengguna

    def registrasiBuyer(self, username, password, nama, email, noHp, kota, alamat):
        username = self.cekUsernameTersedia(username)
        return self.__simpanPengguna(Buyer(username, password, nama, email, noHp, kota, alamat))

    def registrasiSeller(self, username, password, nama, email, noHp, kota):
        username = self.cekUsernameTersedia(username)
        return self.__simpanPengguna(Seller(username, password, nama, email, noHp, kota))

    def login(self, username, password):
        pengguna = self.__pengguna.get(str(username).strip().lower())
        if pengguna is None or not pengguna.cekPassword(password):
            raise AutentikasiError("Username atau password salah.")
        return pengguna

    def daftarPengguna(self):
        return iter(self.__pengguna.values())

    def bukaToko(self, seller, namaToko):
        if any(t.nama.lower() == str(namaToko).strip().lower() for t in self.__daftarToko):
            raise ValidasiError(f"Nama toko '{namaToko}' sudah dipakai.")
        toko = seller.buatToko(namaToko)
        self.__daftarToko.append(toko)
        return toko

    def katalog(self, saring=None):
        return KatalogIterator(self.__daftarToko, saring)

    def __iter__(self):
        return self.katalog()

    def cariProdukById(self, idProduk):
        for produk in self:
            if produk.id == idProduk:
                return produk
        raise DataTidakDitemukanError(f"Produk dengan ID {idProduk} tidak ditemukan.")

    def daftarKategori(self):
        return sorted({produk.kategori for produk in self})

    def cariProduk(self, kataKunci="", kategori=None, hargaMin=None, hargaMax=None,
                   urutan="relevan", hanyaTersedia=True):
        if hargaMin is not None and hargaMax is not None and hargaMin > hargaMax:
            raise ValidasiError("Harga minimum tidak boleh lebih besar dari harga maksimum.")
        if urutan != "relevan" and urutan not in URUTAN_PRODUK:
            raise ValidasiError(f"Urutan '{urutan}' tidak dikenal.")
        kataKunci = str(kataKunci).strip().lower()

        def cocok(produk):
            return ((not kataKunci or kataKunci in produk.nama.lower())
                    and (kategori is None or produk.kategori == kategori)
                    and (hargaMin is None or produk.harga >= hargaMin)
                    and (hargaMax is None or produk.harga <= hargaMax)
                    and (not hanyaTersedia or produk.stok > 0))
        hasil = list(self.katalog(cocok))
        if urutan in URUTAN_PRODUK:
            kunci, terbalik = URUTAN_PRODUK[urutan]
            hasil.sort(key=kunci, reverse=terbalik)
        return hasil

    def siapkanCheckout(self, buyer):
        if len(buyer.keranjang) == 0:
            raise KeranjangKosongError()
        kelompok = buyer.keranjang.kelompokPerToko()
        for items in kelompok.values():
            for item in items:
                if item.jumlah > item.produk.stok:
                    raise StokTidakCukupError(item.produk.nama, item.produk.stok, item.jumlah)
        return kelompok

    def checkout(self, buyer, pilihan=None):
        pilihan = pilihan or {}
        kelompok = self.siapkanCheckout(buyer)
        rencana = []
        for toko, items in kelompok.items():
            kurir, kodeVoucher = pilihan.get(toko, (DAFTAR_KURIR[0], ""))
            voucher = None
            if kodeVoucher:
                voucher = toko.ambilVoucher(kodeVoucher)
                voucher.validasi(sum(item.subtotal for item in items))
            rencana.append((toko, items, kurir, voucher))
        orderBaru = []
        for toko, items, kurir, voucher in rencana:
            order = Order(buyer, toko, items, kurir, voucher)
            for item in items:
                item.produk.kurangiStok(item.jumlah)
            if voucher is not None:
                voucher.pakai()
            toko.catatOrder(order)
            buyer.catatOrder(order)
            self.__daftarOrder.append(order)
            orderBaru.append(order)
        buyer.keranjang.kosongkan()
        return orderBaru

    def cariOrder(self, pengguna, idOrder):
        idOrder = str(idOrder).strip().upper()
        for order in pengguna.daftarOrderTerkait():
            if order.id == idOrder:
                return order
        raise DataTidakDitemukanError(f"Order {idOrder} tidak ditemukan.")

    def ubahStatusOlehSeller(self, seller, order, statusBaru):
        if order.toko is not seller.toko:
            raise AksesDitolakError("Order ini bukan milik toko Anda.")
        if statusBaru not in (StatusOrder.DIPROSES, StatusOrder.DIKIRIM, StatusOrder.DIBATALKAN):
            raise AksesDitolakError(f"Seller tidak boleh mengubah status menjadi '{statusBaru.value}'.")
        order.ubahStatus(statusBaru)

    def __cekPemilikOrder(self, buyer, order):
        if order.buyer is not buyer:
            raise AksesDitolakError("Order ini bukan milik Anda.")

    def batalkanOlehBuyer(self, buyer, order):
        self.__cekPemilikOrder(buyer, order)
        if order.status is not StatusOrder.MENUNGGU:
            raise AksesDitolakError("Pesanan hanya bisa dibatalkan pembeli selama masih Menunggu Konfirmasi.")
        order.ubahStatus(StatusOrder.DIBATALKAN)

    def konfirmasiDiterima(self, buyer, order):
        self.__cekPemilikOrder(buyer, order)
        order.ubahStatus(StatusOrder.SELESAI)

    def produkBisaDireview(self, buyer):
        sudahTampil = set()
        for order in buyer.daftarOrderTerkait():
            if order.status is not StatusOrder.SELESAI:
                continue
            for item in order:
                produk = item.produk
                if produk.id in sudahTampil or produk.sudahDireviewOleh(buyer):
                    continue
                sudahTampil.add(produk.id)
                yield produk

    def beriReview(self, buyer, produk, rating, komentar):
        if produk.sudahDireviewOleh(buyer):
            raise ValidasiError("Anda sudah memberi review untuk produk ini.")
        if produk not in self.produkBisaDireview(buyer):
            raise AksesDitolakError("Review hanya untuk produk dari pesanan Anda yang sudah Selesai.")
        produk.tambahReview(Review(buyer, rating, komentar))

    def laporanPenjualan(self, seller):
        toko = seller.wajibPunyaToko()
        selesai = list(toko.orderBerstatus(StatusOrder.SELESAI))
        perProduk = {}
        for order in selesai:
            for item in order:
                data = perProduk.setdefault(item.namaProduk, [0, 0])
                data[0] += item.jumlah
                data[1] += item.subtotal
        dibatalkan = sum(1 for _ in toko.orderBerstatus(StatusOrder.DIBATALKAN))
        return {
            "totalOrder": len(toko.daftarOrder),
            "orderSelesai": len(selesai),
            "orderDibatalkan": dibatalkan,
            "orderBerjalan": len(toko.daftarOrder) - len(selesai) - dibatalkan,
            "pendapatan": sum(order.subtotal - order.potongan for order in selesai),
            "perProduk": sorted(perProduk.items(), key=lambda pasangan: pasangan[1][1], reverse=True),
        }

    def barisLaporanCsv(self, seller):
        toko = seller.wajibPunyaToko()
        yield ["ID Order", "Tanggal", "Pembeli", "Produk", "Jumlah", "Harga", "Subtotal",
               "Ongkir Order", "Potongan Order", "Total Order", "Status"]
        for order in toko.daftarOrder:
            for item in order:
                yield [order.id, order.tanggal.strftime("%d-%m-%Y %H:%M"), order.buyer.nama,
                       item.namaProduk, item.jumlah, item.harga, item.subtotal,
                       order.ongkir, order.potongan, order.total, order.status.value]

    def eksporCsv(self, seller, namaFile=None):
        toko = seller.wajibPunyaToko()
        if not toko.daftarOrder:
            raise DataTidakDitemukanError("Belum ada order untuk diekspor.")
        namaFile = namaFile or f"laporan_{toko.nama.lower().replace(' ', '_')}.csv"
        try:
            with open(namaFile, "w", newline="", encoding="utf-8") as berkas:
                csv.writer(berkas).writerows(self.barisLaporanCsv(seller))
        except OSError as e:
            raise MarketplaceError(f"Gagal menulis file {namaFile}: {e}") from e
        return os.path.abspath(namaFile)
