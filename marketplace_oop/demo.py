import os
from marketplace.data import isiDataContoh
from marketplace.exceptions import MarketplaceError
from marketplace.iterator import bagiHalaman
from marketplace.kurir import DAFTAR_KURIR, KurirEkspres
from marketplace.order import StatusOrder
from marketplace.pengguna import Buyer, Pengguna, Seller
from marketplace.sistem import Marketplace
from marketplace.tampilan import cetakPasangan, cetakTabel, judul, subjudul
from marketplace.utilitas import formatRupiah

def coba(keterangan, aksi):
    try:
        aksi()
        print(f"  [?] {keterangan}: tidak terjadi error")
    except MarketplaceError as e:
        print(f"  [X] {keterangan}: {type(e).__name__} -> {e}")
    except (AttributeError, TypeError) as e:
        print(f"  [X] {keterangan}: {type(e).__name__} -> {e}")

def demoInheritance(mp):
    judul("1. INHERITANCE")

    for kelas in (Buyer, Seller):
        print(f"  {kelas.__name__}.__mro__ = {[k.__name__ for k in kelas.__mro__]}")

    for pengguna in mp.daftarPengguna():
        print(f"  {pengguna.username:<12} -> {type(pengguna).__name__:<7} "
              f"isinstance(Pengguna)={isinstance(pengguna, Pengguna)}")
        
    coba("Membuat objek dari abstract class Pengguna", lambda: Pengguna("x", "y", "z", "a", "b", "c"))

def demoEncapsulation(mp):
    judul("2. ENCAPSULATION")
    buyer = mp.login("andi", "andi1234")
    produk = mp.cariProdukById(1)
    print(f"  buyer.username (property read-only) = {buyer.username}")
    print(f"  buyer.cekPassword('andi1234') = {buyer.cekPassword('andi1234')}")
    coba("Membaca buyer.__password dari luar kelas", lambda: buyer.__password)
    coba("Mengubah buyer.username", lambda: setattr(buyer, "username", "baru"))
    coba("Mengisi produk.harga = -5000", lambda: setattr(produk, "harga", -5000))
    coba("Mengisi buyer.email = 'salah'", lambda: setattr(buyer, "email", "salah"))
    print(f"  produk.harga tetap {formatRupiah(produk.harga)}, buyer.email tetap {buyer.email}")

def demoPolymorphism(mp):
    judul("3. POLYMORPHISM (METHOD OVERRIDING)")
    subjudul("Pengguna.peran & infoProfil() dipanggil dengan cara yang sama")

    for pengguna in mp.daftarPengguna():
        print(f"\n  >> {pengguna}")
        cetakPasangan(pengguna.infoProfil())
        
    subjudul("Produk.jenis, beratTotal(2), infoTambahan()")
    cetakTabel(["Produk", "Kelas", "jenis", "beratTotal(2)", "infoTambahan()"],
               [[p.nama, type(p).__name__, p.jenis, f"{p.beratTotal(2)} g", p.infoTambahan()] for p in mp])
    subjudul("Kurir.hitungOngkir(2500 g, Jakarta -> Medan)")
    cetakTabel(["Kurir", "Kelas", "Ongkir", "Estimasi"],
               [[k.nama, type(k).__name__, formatRupiah(k.hitungOngkir(2500, "Jakarta", "Medan")), k.estimasi]
                for k in DAFTAR_KURIR])
    subjudul("Voucher.hitungPotongan(subtotal 600.000, ongkir 24.000)")
    semuaVoucher = [v for p in mp.daftarPengguna() if isinstance(p, Seller) for v in p.toko.daftarVoucher]
    cetakTabel(["Kode", "Kelas", "Keterangan", "Potongan"],
               [[v.kode, type(v).__name__, v.deskripsi(), formatRupiah(v.hitungPotongan(600000, 24000))]
                for v in semuaVoucher])

def demoIterator(mp):
    judul("4. ITERATOR PATTERN")
    subjudul("KatalogIterator dipanggil manual dengan next()")
    iterator = mp.katalog()
    print(f"  type = {type(iterator).__name__}")

    for _ in range(3):
        print(f"  next() -> {next(iterator)}")

    subjudul("Iterator dengan filter (hanya kategori Buku) di for loop")

    for produk in mp.katalog(lambda p: p.kategori == "Buku"):
        print(f"  {produk} - stok {produk.stok}")

    subjudul("Iterator habis -> StopIteration")
    iteratorKosong = mp.katalog(lambda p: p.harga > 100000000)

    try:
        next(iteratorKosong)
    except StopIteration:
        print("  StopIteration tertangkap: tidak ada produk di atas Rp 100.000.000")
    subjudul("Generator bagiHalaman(mp, 3)")

    for nomor, halaman in enumerate(bagiHalaman(mp, 3), start=1):
        print(f"  Halaman {nomor}: {[p.nama for p in halaman]}")

def demoExceptionDanTransaksi(mp):
    judul("5. EXCEPTION & ALUR TRANSAKSI MULTI-SELLER")
    buyer = mp.login("andi", "andi1234")
    sellerElektro = mp.login("elektrojaya", "rahasia123")
    sellerBuku = mp.login("pustakailmu", "rahasia123")
    subjudul("Custom exception yang ditangkap")
    coba("Registrasi username yang sudah ada",
         lambda: mp.registrasiBuyer("andi", "abcdef", "Andi 2", "a@b.com", "08123456789", "Medan", "Jl. X"))
    coba("Login dengan password salah", lambda: mp.login("andi", "salah"))
    coba("Checkout dengan keranjang kosong", lambda: mp.checkout(buyer))
    coba("Tambah 10 Mouse Wireless (stok 3)", lambda: buyer.keranjang.tambah(mp.cariProdukById(3), 10))
    coba("Cari produk ID 999", lambda: mp.cariProdukById(999))
    subjudul("F3: filter kategori Buku, urut harga termurah")

    for produk in mp.cariProduk(kategori="Buku", urutan="harga_termurah"):
        print(f"  {produk} {formatRupiah(produk.harga)}")

    subjudul("F4: isi keranjang dari 2 toko berbeda")
    kipas = mp.cariProdukById(1)
    bukuPython = mp.cariProdukById(5)
    ebook = mp.cariProdukById(7)
    buyer.keranjang.tambah(kipas, 2)
    buyer.keranjang.tambah(bukuPython, 1)
    buyer.keranjang.tambah(ebook, 1)
    print(f"  Stok sebelum checkout: Kipas={kipas.stok}, Buku Python={bukuPython.stok}, E-book={ebook.stok}")
    tokoElektro = sellerElektro.toko
    tokoBuku = sellerBuku.toko
    coba("Voucher ELEKTRO10 dipakai di toko Pustaka Ilmu",
         lambda: mp.checkout(buyer, {tokoBuku: (DAFTAR_KURIR[0], "ELEKTRO10")}))
    subjudul("F6: checkout -> 1 order per seller, stok berkurang otomatis")
    pilihan = {tokoElektro: (KurirEkspres(), "ELEKTRO10"), tokoBuku: (DAFTAR_KURIR[0], "HEMAT15")}
    daftarOrder = mp.checkout(buyer, pilihan)

    for order in daftarOrder:
        print(f"  {order.id} | {order.toko.nama:<13} | subtotal {formatRupiah(order.subtotal):>12} | "
              f"ongkir {formatRupiah(order.ongkir):>9} | potongan {formatRupiah(order.potongan):>9} | "
              f"total {formatRupiah(order.total)}")
        
    print(f"  Stok sesudah checkout: Kipas={kipas.stok}, Buku Python={bukuPython.stok}, E-book={ebook.stok}")
    print(f"  Isi keranjang sekarang: {len(buyer.keranjang)} produk")
    orderElektro, orderBuku = daftarOrder
    subjudul("F5: update status order + validasi transisi")
    coba("Buyer konfirmasi diterima padahal belum dikirim", lambda: mp.konfirmasiDiterima(buyer, orderElektro))
    coba("Seller buku mengubah order toko elektro",
         lambda: mp.ubahStatusOlehSeller(sellerBuku, orderElektro, StatusOrder.DIPROSES))
    mp.ubahStatusOlehSeller(sellerElektro, orderElektro, StatusOrder.DIPROSES)
    mp.ubahStatusOlehSeller(sellerElektro, orderElektro, StatusOrder.DIKIRIM)
    mp.konfirmasiDiterima(buyer, orderElektro)
    print(f"  {orderElektro.id}: " + " -> ".join(s.value for s, _ in orderElektro.riwayat))
    coba("Buyer membatalkan order yang sudah Selesai", lambda: mp.batalkanOlehBuyer(buyer, orderElektro))
    subjudul("F5: pembatalan order mengembalikan stok")
    mp.batalkanOlehBuyer(buyer, orderBuku)
    print(f"  {orderBuku.id}: {orderBuku.status.value}, stok Buku Python kembali = {bukuPython.stok}")
    subjudul("F5: review, wishlist, laporan, ekspor CSV")
    coba("Review produk dari order yang dibatalkan", lambda: mp.beriReview(buyer, bukuPython, 5, "Bagus"))
    mp.beriReview(buyer, kipas, 5, "Anginnya kencang, pengiriman cepat")
    print(f"  Rating Kipas Angin = {kipas.rataRating} dari {len(kipas.daftarReview)} review")
    buyer.tambahWishlist(mp.cariProdukById(2))
    coba("Menambahkan produk yang sama ke wishlist", lambda: buyer.tambahWishlist(mp.cariProdukById(2)))
    laporan = mp.laporanPenjualan(sellerElektro)
    print(f"  Laporan {tokoElektro.nama}: {laporan['orderSelesai']} order selesai, "
          f"pendapatan {formatRupiah(laporan['pendapatan'])}")
    lokasi = mp.eksporCsv(sellerElektro, "laporan_demo.csv")
    print(f"  CSV diekspor ke {os.path.basename(lokasi)}")
    subjudul("F7: daftar order buyer dan statusnya")
    
    for order in buyer.daftarOrderTerkait():
        print(f"  {order.id} | {order.toko.nama:<13} | {formatRupiah(order.total):>12} | {order.status.value}")

def main():
    mp = Marketplace("MikroMarket")
    isiDataContoh(mp)
    demoInheritance(mp)
    demoEncapsulation(mp)
    demoPolymorphism(mp)
    demoIterator(mp)
    demoExceptionDanTransaksi(mp)

if __name__ == "__main__":
    main()
