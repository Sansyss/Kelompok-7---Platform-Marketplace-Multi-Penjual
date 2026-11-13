from abc import ABC, abstractmethod
from marketplace.data import AKUN_CONTOH, isiDataContoh
from marketplace.exceptions import MarketplaceError, VoucherTidakValidError
from marketplace.kurir import DAFTAR_KURIR
from marketplace.order import StatusOrder, hitungBiaya
from marketplace.pengguna import Buyer, Seller
from marketplace.produk import ProdukDigital, ProdukFisik
from marketplace.sistem import Marketplace
from marketplace.tampilan import (bersihkanLayar, cetakPasangan, cetakTabel, galat, info, jeda, judul,
                                  konfirmasi, pilihDari, subjudul, sukses, tampilkanDetailOrder,
                                  tampilkanProduk, tanya, tanyaAngka, tanyaValid)
from marketplace.utilitas import (formatRupiah, validasiEmail, validasiNoHp, validasiPassword, wajibIsi)
from marketplace.voucher import VoucherGratisOngkir, VoucherNominal, VoucherPersen

class Sesi(ABC):
    def __init__(self, marketplace, pengguna):
        self._mp = marketplace
        self._pengguna = pengguna

    @abstractmethod
    def opsi(self):
        pass

    def jalankan(self):
        while True:
            bersihkanLayar()
            judul(f"{self._mp.nama} - Menu {self._pengguna.peran}")
            info(f"Login sebagai {self._pengguna}")
            daftarOpsi = self.opsi()
            for nomor, (label, _) in enumerate(daftarOpsi, start=1):
                print(f"   {nomor}. {label}")
            print("   0. Logout")
            pilihan = tanyaAngka("Pilih menu: ", 0, len(daftarOpsi))
            if pilihan == 0:
                return
            try:
                daftarOpsi[pilihan - 1][1]()
            except MarketplaceError as e:
                galat(str(e))
            jeda()

    def lihatProfil(self):
        subjudul("Profil Saya")
        cetakPasangan(self._pengguna.infoProfil())

    def tabelOrder(self, daftarOrder):
        cetakTabel(["ID", "Tanggal", "Pembeli", "Toko", "Barang", "Total", "Status"],
                   [[o.id, o.tanggal.strftime("%d-%m-%Y %H:%M"), o.buyer.nama, o.toko.nama,
                     o.jumlahBarang, formatRupiah(o.total), o.status.value] for o in daftarOrder])

class SesiBuyer(Sesi):
    def opsi(self):
        return [
            ("Cari & filter produk", self.cariProduk),
            ("Detail produk & review", self.detailProduk),
            ("Tambah ke keranjang", self.tambahKeKeranjang),
            ("Keranjang saya", self.kelolaKeranjang),
            ("Checkout", self.checkout),
            ("Pesanan saya", self.pesananSaya),
            ("Beri review", self.beriReview),
            ("Wishlist", self.kelolaWishlist),
            ("Profil saya", self.lihatProfil),
        ]

    def cariProduk(self):
        subjudul("Cari & Filter Produk")
        kataKunci = tanya("Kata kunci nama (Enter = semua): ", wajib=False)
        daftarKategori = self._mp.daftarKategori()
        indeks = pilihDari("Kategori", ["Semua kategori"] + daftarKategori)
        kategori = None if indeks == 0 else daftarKategori[indeks - 1]
        hargaMin = tanyaAngka("Harga minimum (Enter = bebas): ", 0, bolehKosong=True)
        hargaMax = tanyaAngka("Harga maksimum (Enter = bebas): ", 0, bolehKosong=True)
        labelUrutan = ["Relevan", "Harga termurah", "Harga termahal", "Nama A-Z", "Rating tertinggi", "Terlaris"]
        kodeUrutan = ["relevan", "harga_termurah", "harga_termahal", "nama", "rating", "terlaris"]
        urutan = kodeUrutan[pilihDari("Urutkan berdasarkan", labelUrutan)]
        hasil = self._mp.cariProduk(kataKunci, kategori, hargaMin, hargaMax, urutan)
        if not hasil:
            info("Tidak ada produk yang cocok.")
            return
        info(f"Ditemukan {len(hasil)} produk.")
        tampilkanProduk(hasil)

    def detailProduk(self):
        subjudul("Detail Produk")
        produk = self._mp.cariProdukById(tanyaAngka("ID produk: ", 1))
        cetakPasangan([
            ("Nama", produk.nama),
            ("Toko", str(produk.toko)),
            ("Kategori", produk.kategori),
            ("Jenis", produk.jenis),
            ("Keterangan", produk.infoTambahan()),
            ("Harga", formatRupiah(produk.harga)),
            ("Stok", produk.stok),
            ("Terjual", produk.terjual),
            ("Rating", f"{produk.rataRating:.1f} dari {len(produk.daftarReview)} review"),
        ])
        if not produk.daftarReview:
            info("Belum ada review.")
            return
        subjudul("Review")
        for review in produk.daftarReview:
            print(f"  {'*' * review.rating}{'-' * (5 - review.rating)}  {review.buyer.nama}: {review.komentar}")

    def tambahKeKeranjang(self):
        subjudul("Tambah ke Keranjang")
        produk = self._mp.cariProdukById(tanyaAngka("ID produk: ", 1))
        info(f"{produk.nama} - {formatRupiah(produk.harga)} (stok {produk.stok})")
        jumlah = tanyaAngka("Jumlah: ", 1)
        self._pengguna.keranjang.tambah(produk, jumlah)
        sukses(f"{jumlah} x {produk.nama} masuk ke keranjang.")

    def tampilkanKeranjang(self):
        keranjang = self._pengguna.keranjang
        cetakTabel(["ID", "Produk", "Toko", "Harga", "Jumlah", "Subtotal"],
                   [[i.produk.id, i.produk.nama, i.produk.toko.nama, formatRupiah(i.produk.harga),
                     i.jumlah, formatRupiah(i.subtotal)] for i in keranjang])
        info(f"Total belanja: {formatRupiah(keranjang.total)}")

    def kelolaKeranjang(self):
        subjudul("Keranjang Saya")
        keranjang = self._pengguna.keranjang
        if len(keranjang) == 0:
            info("Keranjang masih kosong.")
            return
        self.tampilkanKeranjang()
        aksi = pilihDari("Aksi", ["Kembali", "Ubah jumlah", "Hapus produk", "Kosongkan keranjang"])
        if aksi == 1:
            idProduk = tanyaAngka("ID produk: ", 1)
            keranjang.ubahJumlah(idProduk, tanyaAngka("Jumlah baru: ", 1))
            sukses("Jumlah diperbarui.")
        elif aksi == 2:
            keranjang.hapus(tanyaAngka("ID produk: ", 1))
            sukses("Produk dihapus dari keranjang.")
        elif aksi == 3 and konfirmasi("Yakin mengosongkan keranjang?"):
            keranjang.kosongkan()
            sukses("Keranjang dikosongkan.")

    def pilihVoucher(self, toko, items):
        if not toko.daftarVoucher:
            return None
        info("Voucher toko: " + ", ".join(f"{v.kode} ({v.deskripsi()})" for v in toko.daftarVoucher))
        while True:
            kode = tanya("Kode voucher (Enter = lewati): ", wajib=False)
            if not kode:
                return None
            try:
                voucher = toko.ambilVoucher(kode)
                voucher.validasi(sum(item.subtotal for item in items))
                return voucher
            except VoucherTidakValidError as e:
                galat(str(e))

    def checkout(self):
        subjudul("Checkout")
        buyer = self._pengguna
        kelompok = self._mp.siapkanCheckout(buyer)
        info(f"Pesanan dipecah menjadi {len(kelompok)} order (satu order per toko).")
        pilihan = {}
        totalBayar = 0
        for toko, items in kelompok.items():
            print(f"\n  Toko: {toko}")
            cetakTabel(["Produk", "Harga", "Jumlah", "Subtotal"],
                       [[i.produk.nama, formatRupiah(i.produk.harga), i.jumlah, formatRupiah(i.subtotal)]
                        for i in items])
            berat = sum(i.produk.beratTotal(i.jumlah) for i in items)
            labelKurir = [f"{k.nama} - {formatRupiah(k.hitungOngkir(berat, toko.kota, buyer.kota))} ({k.estimasi})"
                          for k in DAFTAR_KURIR]
            kurir = DAFTAR_KURIR[pilihDari("Pilih kurir", labelKurir)]
            voucher = self.pilihVoucher(toko, items)
            pilihan[toko] = (kurir, voucher.kode if voucher else "")
            subtotal, ongkir, potongan = hitungBiaya(items, toko.kota, buyer.kota, kurir, voucher)
            cetakPasangan([
                ("Subtotal", formatRupiah(subtotal)),
                ("Ongkir", formatRupiah(ongkir)),
                ("Potongan", "- " + formatRupiah(potongan)),
                ("Total order", formatRupiah(subtotal + ongkir - potongan)),
            ])
            totalBayar += subtotal + ongkir - potongan
        print()
        info(f"Total yang harus dibayar: {formatRupiah(totalBayar)}")
        if not konfirmasi("Buat pesanan sekarang?"):
            info("Checkout dibatalkan.")
            return
        for order in self._mp.checkout(buyer, pilihan):
            sukses(f"{order.id} untuk toko {order.toko.nama} dibuat - total {formatRupiah(order.total)}")
        info("Stok produk otomatis berkurang dan keranjang dikosongkan.")

    def pesananSaya(self):
        subjudul("Pesanan Saya")
        daftarOrder = self._pengguna.daftarOrderTerkait()
        if not daftarOrder:
            info("Belum ada pesanan.")
            return
        self.tabelOrder(daftarOrder)
        idOrder = tanya("ID order untuk detail (Enter = kembali): ", wajib=False)
        if not idOrder:
            return
        order = self._mp.cariOrder(self._pengguna, idOrder)
        tampilkanDetailOrder(order)
        aksi = []
        if order.status is StatusOrder.MENUNGGU:
            aksi.append(("Batalkan pesanan", self._mp.batalkanOlehBuyer))
        if order.status is StatusOrder.DIKIRIM:
            aksi.append(("Konfirmasi pesanan diterima", self._mp.konfirmasiDiterima))
        if not aksi:
            return
        indeks = pilihDari("Aksi", ["Kembali"] + [label for label, _ in aksi])
        if indeks > 0:
            aksi[indeks - 1][1](self._pengguna, order)
            sukses(f"Status {order.id} sekarang: {order.status.value}")

    def beriReview(self):
        subjudul("Beri Review")
        bisaDireview = list(self._mp.produkBisaDireview(self._pengguna))
        if not bisaDireview:
            info("Belum ada produk dari pesanan Selesai yang bisa direview.")
            return
        tampilkanProduk(bisaDireview)
        produk = self._mp.cariProdukById(tanyaAngka("ID produk yang direview: ", 1))
        rating = tanyaAngka("Rating (1-5): ", 1, 5)
        komentar = tanya("Komentar: ", wajib=False)
        self._mp.beriReview(self._pengguna, produk, rating, komentar)
        sukses(f"Review untuk '{produk.nama}' tersimpan.")

    def kelolaWishlist(self):
        subjudul("Wishlist")
        if self._pengguna.wishlist:
            tampilkanProduk(self._pengguna.wishlist)
        else:
            info("Wishlist masih kosong.")
        aksi = pilihDari("Aksi", ["Kembali", "Tambah produk", "Hapus produk", "Pindahkan ke keranjang"])
        if aksi == 0:
            return
        produk = self._mp.cariProdukById(tanyaAngka("ID produk: ", 1))
        if aksi == 1:
            self._pengguna.tambahWishlist(produk)
            sukses(f"'{produk.nama}' masuk wishlist.")
        elif aksi == 2:
            self._pengguna.hapusWishlist(produk)
            sukses(f"'{produk.nama}' dihapus dari wishlist.")
        else:
            self._pengguna.keranjang.tambah(produk, 1)
            self._pengguna.hapusWishlist(produk)
            sukses(f"'{produk.nama}' dipindahkan ke keranjang.")

class SesiSeller(Sesi):
    def opsi(self):
        if self._pengguna.toko is None:
            return [("Buat toko", self.buatToko), ("Profil saya", self.lihatProfil)]
        return [
            ("Tambah produk", self.tambahProduk),
            ("Produk saya", self.produkSaya),
            ("Ubah harga/stok produk", self.ubahProduk),
            ("Pesanan masuk & update status", self.pesananMasuk),
            ("Kelola voucher", self.kelolaVoucher),
            ("Laporan penjualan", self.laporanPenjualan),
            ("Ekspor laporan ke CSV", self.eksporCsv),
            ("Profil saya", self.lihatProfil),
        ]

    def buatToko(self):
        subjudul("Buat Toko")
        toko = self._mp.bukaToko(self._pengguna, tanya("Nama toko: "))
        sukses(f"Toko '{toko.nama}' berhasil dibuka di {toko.kota}.")

    def tambahProduk(self):
        subjudul("Tambah Produk")
        toko = self._pengguna.wajibPunyaToko()
        jenis = pilihDari("Jenis produk", ["Fisik (dikirim kurir)", "Digital (dikirim lewat email)"])
        nama = tanya("Nama produk: ")
        harga = tanyaAngka("Harga (Rp): ", 1)
        stok = tanyaAngka("Stok: ", 0)
        kategoriAda = self._mp.daftarKategori()
        if kategoriAda:
            info("Kategori yang sudah ada: " + ", ".join(kategoriAda))
        kategori = tanya("Kategori: ")
        if jenis == 0:
            produk = ProdukFisik(nama, harga, stok, kategori, toko, tanyaAngka("Berat per item (gram): ", 1))
        else:
            produk = ProdukDigital(nama, harga, stok, kategori, toko, tanya("Format file (mis. PDF): "))
        toko.tambahProduk(produk)
        sukses(f"Produk '{produk.nama}' ditambahkan dengan ID {produk.id}.")

    def produkSaya(self):
        subjudul("Produk Saya")
        tampilkanProduk(self._pengguna.wajibPunyaToko())

    def ubahProduk(self):
        subjudul("Ubah Harga/Stok")
        produk = self._pengguna.wajibPunyaToko().cariProduk(tanyaAngka("ID produk: ", 1))
        info(f"{produk.nama}: harga {formatRupiah(produk.harga)}, stok {produk.stok}")
        hargaBaru = tanyaAngka("Harga baru (Enter = tetap): ", 1, bolehKosong=True)
        stokBaru = tanyaAngka("Stok baru (Enter = tetap): ", 0, bolehKosong=True)
        if hargaBaru is not None:
            produk.harga = hargaBaru
        if stokBaru is not None:
            produk.stok = stokBaru
        sukses(f"{produk.nama}: harga {formatRupiah(produk.harga)}, stok {produk.stok}")

    def pesananMasuk(self):
        subjudul("Pesanan Masuk")
        toko = self._pengguna.wajibPunyaToko()
        if not toko.daftarOrder:
            info("Belum ada pesanan masuk.")
            return
        daftarStatus = list(StatusOrder)
        indeks = pilihDari("Tampilkan", ["Semua status"] + [s.value for s in daftarStatus])
        status = None if indeks == 0 else daftarStatus[indeks - 1]
        daftarOrder = list(toko.orderBerstatus(status))
        if not daftarOrder:
            info("Tidak ada pesanan dengan status tersebut.")
            return
        self.tabelOrder(daftarOrder)
        idOrder = tanya("ID order untuk detail/update (Enter = kembali): ", wajib=False)
        if not idOrder:
            return
        order = self._mp.cariOrder(self._pengguna, idOrder)
        tampilkanDetailOrder(order)
        tujuan = [s for s in order.statusBerikutnya() if s is not StatusOrder.SELESAI]
        if not tujuan:
            info("Status order ini tidak bisa diubah oleh seller.")
            return
        indeks = pilihDari("Ubah status menjadi", ["Kembali"] + [s.value for s in tujuan])
        if indeks > 0:
            self._mp.ubahStatusOlehSeller(self._pengguna, order, tujuan[indeks - 1])
            sukses(f"Status {order.id} sekarang: {order.status.value}")

    def kelolaVoucher(self):
        subjudul("Kelola Voucher")
        toko = self._pengguna.wajibPunyaToko()
        if toko.daftarVoucher:
            cetakTabel(["Kode", "Jenis", "Keterangan", "Min. Belanja", "Sisa Kuota"],
                       [[v.kode, v.jenis, v.deskripsi(), formatRupiah(v.minBelanja), v.kuota]
                        for v in toko.daftarVoucher])
        else:
            info("Belum ada voucher.")
        if not konfirmasi("Buat voucher baru?"):
            return
        jenis = pilihDari("Jenis voucher", ["Diskon persen", "Potongan nominal", "Gratis ongkir"])
        kode = tanya("Kode voucher: ")
        minBelanja = tanyaAngka("Minimal belanja (Rp): ", 0)
        kuota = tanyaAngka("Kuota pemakaian: ", 1)
        if jenis == 0:
            voucher = VoucherPersen(kode, tanyaAngka("Persen diskon (1-100): ", 1, 100),
                                    tanyaAngka("Maksimal potongan (Rp): ", 1), minBelanja, kuota)
        elif jenis == 1:
            voucher = VoucherNominal(kode, tanyaAngka("Nominal potongan (Rp): ", 1), minBelanja, kuota)
        else:
            voucher = VoucherGratisOngkir(kode, tanyaAngka("Maksimal potongan ongkir (Rp): ", 1),
                                          minBelanja, kuota)
        toko.tambahVoucher(voucher)
        sukses(f"Voucher {voucher.kode} dibuat: {voucher.deskripsi()}")

    def laporanPenjualan(self):
        subjudul("Laporan Penjualan")
        laporan = self._mp.laporanPenjualan(self._pengguna)
        cetakPasangan([
            ("Total order", laporan["totalOrder"]),
            ("Order selesai", laporan["orderSelesai"]),
            ("Order berjalan", laporan["orderBerjalan"]),
            ("Order dibatalkan", laporan["orderDibatalkan"]),
            ("Pendapatan (order selesai)", formatRupiah(laporan["pendapatan"])),
        ])
        if laporan["perProduk"]:
            cetakTabel(["Produk", "Terjual", "Pendapatan"],
                       [[nama, jumlah, formatRupiah(total)] for nama, (jumlah, total) in laporan["perProduk"]])
        else:
            info("Belum ada order yang selesai.")

    def eksporCsv(self):
        subjudul("Ekspor Laporan CSV")
        lokasi = self._mp.eksporCsv(self._pengguna)
        sukses(f"Laporan diekspor ke {lokasi}")

SESI_PER_PERAN = {Buyer: SesiBuyer, Seller: SesiSeller}

def registrasi(mp, peran):
    subjudul(f"Registrasi {peran}")
    username = tanyaValid("Username: ", mp.cekUsernameTersedia)
    password = tanyaValid("Password (min. 6 karakter): ", validasiPassword)
    nama = tanyaValid("Nama lengkap: ", lambda teks: wajibIsi(teks, "Nama"))
    email = tanyaValid("Email: ", validasiEmail)
    noHp = tanyaValid("No HP: ", validasiNoHp)
    kota = tanyaValid("Kota: ", lambda teks: wajibIsi(teks, "Kota"))
    if peran == "Buyer":
        alamat = tanyaValid("Alamat lengkap: ", lambda teks: wajibIsi(teks, "Alamat"))
        pengguna = mp.registrasiBuyer(username, password, nama, email, noHp, kota, alamat)
    else:
        pengguna = mp.registrasiSeller(username, password, nama, email, noHp, kota)
    sukses(f"Registrasi berhasil: {pengguna}. Silakan login.")

def login(mp):
    subjudul("Login")
    pengguna = mp.login(tanya("Username: "), tanya("Password: "))
    SESI_PER_PERAN[type(pengguna)](mp, pengguna).jalankan()
    info(f"{pengguna.nama} telah logout.")

def lihatKatalog(mp):
    subjudul("Katalog Semua Produk")
    tampilkanProduk(mp)

def menuUtama(mp):
    pilihanMenu = {
        "1": lambda: registrasi(mp, "Buyer"),
        "2": lambda: registrasi(mp, "Seller"),
        "3": lambda: login(mp),
        "4": lambda: lihatKatalog(mp),
    }
    while True:
        bersihkanLayar()
        judul(f"{mp.nama} - Platform Marketplace Multi-Penjual")
        info("Akun contoh: " + "; ".join(f"{peran} {u}/{p}" for peran, u, p in AKUN_CONTOH))
        print("   1. Registrasi Buyer")
        print("   2. Registrasi Seller")
        print("   3. Login")
        print("   4. Lihat katalog (tanpa login)")
        print("   0. Keluar")
        pilihan = input("Pilih menu: ").strip()
        if pilihan == "0":
            print("\n  [i]  Terima kasih telah menggunakan aplikasi. Sampai jumpa!")
            break
        if pilihan not in pilihanMenu:
            galat("Menu tidak valid. Pilih 0 - 4.")
        else:
            try:
                pilihanMenu[pilihan]()
            except MarketplaceError as e:
                galat(str(e))
        jeda()

def main():
    mp = Marketplace("MikroMarket")
    isiDataContoh(mp)
    menuUtama(mp)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  [i]  Program dihentikan.")
