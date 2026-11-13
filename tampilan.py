import os
from .exceptions import ValidasiError
from .iterator import bagiHalaman
from .utilitas import formatRupiah

def bersihkanLayar():
    os.system("cls" if os.name == "nt" else "clear")

def jeda():
    input("\n  [Enter untuk lanjut...]")

def judul(teks):
    print("=" * 74)
    print(teks.center(74).rstrip())
    print("=" * 74)

def subjudul(teks):
    print(f"\n--- {teks} ---")

def sukses(teks):
    print(f"  [OK] {teks}")

def info(teks):
    print(f"  [i]  {teks}")

def galat(teks):
    print(f"  [X]  {teks}")

def cetakTabel(header, baris):
    baris = [[str(sel) for sel in b] for b in baris]
    lebar = [len(h) for h in header]
    for b in baris:
        for i, sel in enumerate(b):
            lebar[i] = max(lebar[i], len(sel))
    garis = "+" + "+".join("-" * (w + 2) for w in lebar) + "+"

    def formatBaris(isi):
        return "| " + " | ".join(isi[i].ljust(lebar[i]) for i in range(len(isi))) + " |"
    print(garis)
    print(formatBaris(header))
    print(garis)
    for b in baris:
        print(formatBaris(b))
    print(garis)

def cetakPasangan(pasangan):
    lebar = max(len(label) for label, _ in pasangan)
    for label, nilai in pasangan:
        print(f"  {label.ljust(lebar)} : {nilai}")

def tanya(label, wajib=True):
    while True:
        teks = input(label).strip()
        if teks or not wajib:
            return teks
        galat("Input tidak boleh kosong.")

def tanyaAngka(label, minimal=0, maksimal=None, bolehKosong=False):
    while True:
        teks = input(label).strip()
        if not teks and bolehKosong:
            return None
        try:
            angka = int(teks)
            if angka < minimal or (maksimal is not None and angka > maksimal):
                raise ValueError
            return angka
        except ValueError:
            if maksimal is None:
                galat(f"Masukkan bilangan bulat minimal {minimal}.")
            else:
                galat(f"Masukkan angka {minimal} sampai {maksimal}.")

def tanyaValid(label, fungsiValidasi):
    while True:
        try:
            return fungsiValidasi(input(label))
        except ValidasiError as e:
            galat(str(e))

def pilihDari(label, daftarOpsi):
    for nomor, opsi in enumerate(daftarOpsi, start=1):
        print(f"   {nomor}. {opsi}")
    return tanyaAngka(f"{label}: ", 1, len(daftarOpsi)) - 1

def konfirmasi(label):
    return input(f"{label} (y/n): ").strip().lower() == "y"

def barisProduk(produk):
    return [produk.id, produk.nama, produk.toko.nama, produk.kategori, produk.jenis,
            formatRupiah(produk.harga), produk.stok,
            f"{produk.rataRating:.1f} ({len(produk.daftarReview)})"]

def tampilkanProduk(daftarProduk, ukuranHalaman=6):
    header = ["ID", "Nama", "Toko", "Kategori", "Jenis", "Harga", "Stok", "Rating"]
    adaData = False
    for nomor, halaman in enumerate(bagiHalaman(daftarProduk, ukuranHalaman), start=1):
        if nomor > 1 and input("  Enter = halaman berikutnya, q = berhenti: ").strip().lower() == "q":
            break
        adaData = True
        print(f"  Halaman {nomor}")
        cetakTabel(header, [barisProduk(produk) for produk in halaman])
    if not adaData:
        info("Belum ada produk untuk ditampilkan.")

def tampilkanDetailOrder(order):
    cetakPasangan([
        ("ID Order", order.id),
        ("Tanggal", order.tanggal.strftime("%d-%m-%Y %H:%M")),
        ("Pembeli", f"{order.buyer.nama} - {order.buyer.alamat}, {order.buyer.kota}"),
        ("Toko", str(order.toko)),
        ("Kurir", f"{order.kurir.nama} ({order.kurir.estimasi})"),
        ("Status", order.status.value),
    ])
    cetakTabel(["Produk", "Harga", "Jumlah", "Subtotal"],
               [[i.namaProduk, formatRupiah(i.harga), i.jumlah, formatRupiah(i.subtotal)] for i in order])
    cetakPasangan([
        ("Subtotal", formatRupiah(order.subtotal)),
        ("Ongkir", formatRupiah(order.ongkir)),
        ("Voucher", f"{order.voucher.kode} ({order.voucher.deskripsi()})" if order.voucher else "-"),
        ("Potongan", "- " + formatRupiah(order.potongan)),
        ("TOTAL", formatRupiah(order.total)),
    ])
    print("  Riwayat status:")
    for status, waktu in order.riwayat:
        print(f"    {waktu.strftime('%d-%m-%Y %H:%M:%S')}  {status.value}")
