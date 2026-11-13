import csv
import os

from .exceptions import (MarketplaceError, ValidasiError, DataGandaError, DataTidakDitemukanError, AksesDitolakError, StatusOrderError, StokTidakCukupError, VoucherError)
from .validator import cekEmail
from .user import Buyer, Seller
from .order import Order, ItemOrder, StatusOrder
from .promo import KurirReguler, KurirExpress, KurirSameDay
from .review import Review
from .utils import rupiah, garis, judul

class Marketplace:
    PILIHAN_URUT = {
        "termurah": (lambda p: p.harga, False),
        "termahal": (lambda p: p.harga, True),
        "nama": (lambda p: p.nama.lower(), False),
        "rating": (lambda p: p.rating, True),
        "terlaris": (lambda p: p.terjual, True),
    }

    def __init__(self, nama="Marketplace Home Learning", batasStokMenipis=10):
        self.nama = nama
        self.batasStokMenipis = batasStokMenipis
        self.daftarUser = {}            
        self.daftarOrder = []           
        self.daftarVoucher = {}         
        self.daftarKurir = {k.kode: k for k in (KurirReguler(), KurirExpress(), KurirSameDay())}
        self.notifikasiStok = []
        self._pemantauStok = self._buatPemantauStok()
        next(self._pemantauStok)        

    def _cekEmailBelumTerdaftar(self, email):
        email = cekEmail(email)

        if email in self.daftarUser:
            raise DataGandaError(f"Email {email} sudah terdaftar")
        
        return email

    def registrasiBuyer(self, nama, email, noHP, password, alamat, kota):
        email = self._cekEmailBelumTerdaftar(email)
        buyer = Buyer(nama, email, noHP, password, alamat, kota)
        self.daftarUser[buyer.email] = buyer

        return buyer

    def registrasiSeller(self, nama, email, noHP, password):
        email = self._cekEmailBelumTerdaftar(email)
        seller = Seller(nama, email, noHP, password)
        self.daftarUser[seller.email] = seller

        return seller

    def login(self, email, password):
        user = self.daftarUser.get(str(email).strip().lower())

        if user is None or not user.login(password):
            raise AksesDitolakError("Email atau password salah")
        
        return user

    @property
    def daftarBuyer(self):
        return [u for u in self.daftarUser.values() if isinstance(u, Buyer)]

    @property
    def daftarSeller(self):
        return [u for u in self.daftarUser.values() if isinstance(u, Seller)]

    @property
    def daftarToko(self):
        return [s.toko for s in self.daftarSeller if s.toko is not None]

    @property
    def semuaProduk(self):
        return [produk for toko in self.daftarToko for produk in toko]

    def daftarKategori(self):
        return sorted({p.kategori for p in self.semuaProduk})      

    def cariProdukByKode(self, kode):
        kode = str(kode).strip().upper()

        for produk in self.semuaProduk:
            if produk.kode == kode:
                return produk
            
        raise DataTidakDitemukanError(f"Produk dengan kode {kode} tidak ditemukan")

    def produkStokMenipis(self, seller):
        return [p for p in seller.tokoSaya if p.stok < self.batasStokMenipis]

    def _buatPemantauStok(self):
        while True:
            produk = yield

            if produk.stok == 0:
                pesan = f"Stok '{produk.nama}' ({produk.toko.namaToko}) HABIS"
            elif produk.stok < self.batasStokMenipis:
                pesan = (f"Stok '{produk.nama}' ({produk.toko.namaToko}) menipis, " f"sisa {produk.stok}")
            else:
                continue

            self.notifikasiStok.append(pesan)
            print(f"  [!] PERINGATAN STOK: {pesan}")

    def _saringProduk(self, keyword, kategori, hargaMin, hargaMax, hanyaTersedia):
        keyword = (keyword or "").strip().lower()
        kategori = (kategori or "").strip().lower()

        for produk in self.semuaProduk:
            if keyword and keyword not in produk.nama.lower():
                continue
            if kategori and produk.kategori.lower() != kategori:
                continue
            if produk.harga < hargaMin:
                continue
            if hargaMax is not None and produk.harga > hargaMax:
                continue
            if hanyaTersedia and produk.stok == 0:
                continue

            yield produk

    def cariProduk(self, keyword="", kategori=None, hargaMin=0, hargaMax=None, urutkan=None, hanyaTersedia=True):
        if hargaMax is not None and hargaMax < hargaMin:
            raise ValidasiError("Harga maksimum tidak boleh lebih kecil dari harga minimum")
        
        hasil = list(self._saringProduk(keyword, kategori, hargaMin, hargaMax, hanyaTersedia))

        if urutkan:
            if urutkan not in self.PILIHAN_URUT:
                raise ValidasiError("Pilihan urutan tidak dikenal. Pilih: "
                                    + ", ".join(self.PILIHAN_URUT))
            
            kunci, menurun = self.PILIHAN_URUT[urutkan]
            hasil = sorted(hasil, key=kunci, reverse=menurun)

        return hasil

    def tambahVoucher(self, voucher):
        if voucher.kode in self.daftarVoucher:
            raise DataGandaError(f"Voucher {voucher.kode} sudah ada")
        
        self.daftarVoucher[voucher.kode] = voucher

    def hitungRingkasanCheckout(self, buyer, kodeKurir, kodeVoucher=None):
        if not isinstance(buyer, Buyer):
            raise AksesDitolakError("Hanya buyer yang dapat melakukan checkout")
        
        if buyer.cart.kosong:
            raise ValidasiError("Keranjang masih kosong")
        
        kurir = self.daftarKurir.get(str(kodeKurir).strip().upper())

        if kurir is None:
            raise DataTidakDitemukanError(f"Kurir '{kodeKurir}' tidak tersedia. " f"Pilih: {', '.join(self.daftarKurir)}")
        
        for item in buyer.cart:
            if item.jumlah > item.produk.stok:
                raise StokTidakCukupError(item.produk.nama, item.produk.stok, item.jumlah)

        bagian = []
        for toko, items in buyer.cart.kelompokkanPerToko().items():
            berat = sum(i.produk.berat * i.jumlah for i in items)
            bagian.append({
                "toko": toko,
                "items": items,
                "subtotal": sum(i.subtotal for i in items),
                "ongkir": kurir.hitungOngkir(berat, toko.kota, buyer.kota),
                "diskon": 0,
            })

        totalSubtotal = sum(b["subtotal"] for b in bagian)

        voucher, totalDiskon = None, 0
        if kodeVoucher:
            voucher = self.daftarVoucher.get(str(kodeVoucher).strip().upper())

            if voucher is None:
                raise VoucherError(f"Voucher '{kodeVoucher}' tidak ditemukan")
            
            totalDiskon = voucher.terapkan(totalSubtotal)
            sisa = totalDiskon

            for i, b in enumerate(bagian):
                if i == len(bagian) - 1:
                    b["diskon"] = sisa
                else:
                    b["diskon"] = totalDiskon * b["subtotal"] // totalSubtotal
                    sisa -= b["diskon"]

        for b in bagian:
            b["total"] = b["subtotal"] - b["diskon"] + b["ongkir"]

        return {
            "kurir": kurir,
            "voucher": voucher,
            "bagian": bagian,
            "totalSubtotal": totalSubtotal,
            "totalDiskon": totalDiskon,
            "totalOngkir": sum(b["ongkir"] for b in bagian),
            "grandTotal": sum(b["total"] for b in bagian),
        }

    def tampilkanRingkasan(self, r):
        judul("RINGKASAN CHECKOUT")
        teksVoucher = f"   Voucher: {r['voucher'].kode}" if r["voucher"] else ""
        print(f"Kurir: {r['kurir'].nama} ({r['kurir'].estimasi}){teksVoucher}")
        print(f"Pesanan akan dipecah menjadi {len(r['bagian'])} order (1 order per seller)")

        for no, b in enumerate(r["bagian"], start=1):
            garis()
            print(f"Order #{no} - {b['toko'].namaToko} ({b['toko'].kota})")

            for item in b["items"]:
                print(f"  {item.produk.nama[:28]:<28} {item.jumlah:>3} x " f"{rupiah(item.produk.harga):>11} = {rupiah(item.subtotal):>12}")
            print(f"  {'Subtotal':<49}{rupiah(b['subtotal']):>12}")

            if b["diskon"]:
                print(f"  {'Diskon voucher':<49}{'-' + rupiah(b['diskon']):>12}")

            print(f"  {'Ongkir':<49}{rupiah(b['ongkir']):>12}")
            print(f"  {'Total order':<49}{rupiah(b['total']):>12}")

        garis("=")
        print(f"  {'Total belanja':<49}{rupiah(r['totalSubtotal']):>12}")

        if r["totalDiskon"]:
            print(f"  {'Total diskon':<49}{'-' + rupiah(r['totalDiskon']):>12}")

        print(f"  {'Total ongkir':<49}{rupiah(r['totalOngkir']):>12}")
        print(f"  {'TOTAL BAYAR':<49}{rupiah(r['grandTotal']):>12}")
        garis("=")

    def checkout(self, buyer, kodeKurir, kodeVoucher=None):
        ringkasan = self.hitungRingkasanCheckout(buyer, kodeKurir, kodeVoucher)
        sudahDikurangi = []

        try:
            for b in ringkasan["bagian"]:
                for item in b["items"]:
                    item.produk.kurangiStok(item.jumlah)
                    sudahDikurangi.append((item.produk, item.jumlah))
        except StokTidakCukupError:
            for produk, jumlah in sudahDikurangi:
                produk.tambahStok(jumlah)
            raise

        voucher = ringkasan["voucher"]
        ordersBaru = []

        for b in ringkasan["bagian"]:
            order = Order(buyer, b["toko"], [ItemOrder(i.produk, i.jumlah) for i in b["items"]], ringkasan["kurir"], b["ongkir"], b["diskon"], voucher.kode if voucher else None)
            ordersBaru.append(order)

        if voucher:
            voucher.pakai()

        self.daftarOrder.extend(ordersBaru)
        buyer.daftarOrder.extend(ordersBaru)
        buyer.cart.kosongkan()

        for produk, _ in sudahDikurangi:
            self._pemantauStok.send(produk)

        return ordersBaru

    def daftarOrderBuyer(self, buyer, status=None):
        return [o for o in buyer.daftarOrder if status is None or o.status == status]

    def daftarOrderSeller(self, seller, status=None):
        return [o for o in self.daftarOrder if o.toko.pemilik is seller and (status is None or o.status == status)]

    def cariOrder(self, idOrder):
        idOrder = str(idOrder).strip().upper()
        semua = iter(self.daftarOrder)

        while True:
            try:
                order = next(semua)
            except StopIteration:
                raise DataTidakDitemukanError(f"Order {idOrder} tidak ditemukan")
            
            if order.idOrder == idOrder:
                return order

    def detailOrder(self, idOrder, oleh):
        
        order = self.cariOrder(idOrder)
        if oleh is not order.buyer and oleh is not order.toko.pemilik:
            raise AksesDitolakError("Anda tidak berhak melihat order ini")
        return order

    def updateStatusOrder(self, idOrder, statusBaru, oleh, keterangan=""):
        order = self.cariOrder(idOrder)
        order.ubahStatus(statusBaru, oleh, keterangan)
        return order

    def batalkanOrder(self, idOrder, oleh, alasan=""):
        return self.updateStatusOrder(idOrder, StatusOrder.DIBATALKAN, oleh,
                                      f"Dibatalkan oleh {oleh.peran}"
                                      + (f": {alasan}" if alasan else ""))

    # ======================= REVIEW =======================================
    def beriReview(self, buyer, idOrder, kodeProduk, rating, komentar=""):
        order = self.cariOrder(idOrder)
        if order.buyer is not buyer:
            raise AksesDitolakError("Order ini bukan milik Anda")
        if order.status != StatusOrder.SELESAI:
            raise StatusOrderError("Review hanya dapat diberikan setelah order berstatus "
                                   f"'Selesai' (status sekarang: {order.status})")
        kodeProduk = str(kodeProduk).strip().upper()
        item = next((i for i in order.items if i.produk.kode == kodeProduk), None)
        if item is None:
            raise DataTidakDitemukanError(f"Produk {kodeProduk} tidak ada di order {order.idOrder}")
        if kodeProduk in order.diulas:
            raise DataGandaError("Produk ini sudah Anda review untuk order tersebut")
        review = Review(buyer, item.produk, rating, komentar)
        item.produk.ulasan.append(review)
        order.diulas.add(kodeProduk)
        return review

    # ======================= LAPORAN & EKSPOR =============================
    def _orderSelesaiSeller(self, seller):
        """Generator: menghasilkan order SELESAI milik seller satu per satu."""
        for order in self.daftarOrder:
            if order.toko.pemilik is seller and order.status == StatusOrder.SELESAI:
                yield order

    def laporanPenjualan(self, seller):
        toko = seller.tokoSaya
        semuaOrder = self.daftarOrderSeller(seller)
        perStatus = {status: len([o for o in semuaOrder if o.status == status])
                     for status in StatusOrder.SEMUA}                    # dict comprehension
        produkTerjual = {}
        totalPenjualan, jumlahSelesai = 0, 0
        for order in self._orderSelesaiSeller(seller):
            jumlahSelesai += 1
            totalPenjualan += order.subtotal
            for item in order.items:
                produkTerjual[item.namaProduk] = produkTerjual.get(item.namaProduk, 0) + item.jumlah
        dalamProses = sum(o.subtotal for o in semuaOrder
                          if o.status in (StatusOrder.MENUNGGU, StatusOrder.DIKONFIRMASI,
                                          StatusOrder.DIKIRIM))
        return {
            "toko": toko,
            "jumlahOrder": len(semuaOrder),
            "perStatus": perStatus,
            "orderSelesai": jumlahSelesai,
            "totalPenjualan": totalPenjualan,
            "nilaiDalamProses": dalamProses,
            "produkTerjual": dict(sorted(produkTerjual.items(), key=lambda x: x[1], reverse=True)),
        }

    def tampilkanLaporan(self, seller):
        lap = self.laporanPenjualan(seller)
        judul(f"LAPORAN PENJUALAN - {lap['toko'].namaToko.upper()}")
        print(f"Total order masuk         : {lap['jumlahOrder']}")
        for status, jumlah in lap["perStatus"].items():
            print(f"   - {status:<22}: {jumlah}")
        print(f"Penjualan (order selesai) : {rupiah(lap['totalPenjualan'])}")
        print(f"Nilai order dalam proses  : {rupiah(lap['nilaiDalamProses'])}")
        if lap["orderSelesai"]:
            print(f"Rata-rata nilai order     : {rupiah(lap['totalPenjualan'] // lap['orderSelesai'])}")
        print("Produk terjual:")
        if not lap["produkTerjual"]:
            print("   (belum ada order yang selesai)")
        for no, (nama, jumlah) in enumerate(lap["produkTerjual"].items(), start=1):
            print(f"   {no}. {nama:<30} {jumlah} pcs")
        menipis = self.produkStokMenipis(seller)
        if menipis:
            print(f"Stok menipis (< {self.batasStokMenipis}):")
            for p in menipis:
                print(f"   - [{p.kode}] {p.nama} : sisa {p.stok}")

    def eksporLaporanCSV(self, seller, namaFile=None):
        """Ekspor semua order seller ke file CSV (statement with, Pert-04)."""
        toko = seller.tokoSaya
        semuaOrder = self.daftarOrderSeller(seller)
        if not semuaOrder:
            raise DataTidakDitemukanError("Belum ada order untuk diekspor")
        if namaFile is None:
            namaAman = "".join(k if k.isalnum() else "_" for k in toko.namaToko.lower())
            namaFile = f"laporan_{namaAman}.csv"
        try:
            with open(namaFile, "w", newline="", encoding="utf-8-sig") as berkas:
                penulis = csv.writer(berkas)
                penulis.writerow(["id_order", "tanggal", "status", "buyer", "kota_tujuan",
                                  "kode_produk", "nama_produk", "harga_satuan", "jumlah",
                                  "subtotal_item", "diskon_order", "ongkir_order", "total_order"])
                for order in semuaOrder:
                    for item in order.items:
                        penulis.writerow([order.idOrder, order.tanggal, order.status,
                                          order.buyer.nama, order.buyer.kota,
                                          item.produk.kode, item.namaProduk, item.hargaSatuan,
                                          item.jumlah, item.subtotal, order.diskon,
                                          order.ongkir, order.total])
        except OSError as e:
            raise MarketplaceError(f"Gagal menulis file CSV: {e}")
        return os.path.abspath(namaFile)
