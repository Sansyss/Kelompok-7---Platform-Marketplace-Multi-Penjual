"""Data contoh supaya program bisa langsung dicoba."""
from marketplace import VoucherPersen, VoucherNominal


def isiDataAwal(mp):
    # ---------------- seller & produk ----------------
    s1 = mp.registrasiSeller("Rina Siregar", "rina@toko.com", "081234567801", "seller123")
    t1 = s1.buatToko("Rina Gadget", "Medan")
    t1.tambahProduk("ELK001", "Earphone Bluetooth", 150000, 25, "Elektronik", 200)
    t1.tambahProduk("ELK002", "Power Bank 10000mAh", 225000, 8, "Elektronik", 350)
    t1.tambahProduk("ELK003", "Mouse Wireless", 95000, 40, "Elektronik", 150)
    t1.tambahProduk("KSH001", "Hand Sanitizer 500ml", 35000, 50, "Kesehatan", 550)

    s2 = mp.registrasiSeller("Budi Santoso", "budi@toko.com", "081234567802", "seller123")
    t2 = s2.buatToko("Budi Otomotif", "Jakarta")
    t2.tambahProduk("OTO001", "Ban Mobil Ring 15", 850000, 12, "Otomotif", 9000)
    t2.tambahProduk("OTO002", "Oli Mesin 1 Liter", 75000, 30, "Otomotif", 1000)
    t2.tambahProduk("ELK004", "Charger Mobil USB", 60000, 15, "Elektronik", 100)

    s3 = mp.registrasiSeller("Sari Lubis", "sari@toko.com", "081234567803", "seller123")
    t3 = s3.buatToko("Sari Fresh & Baby", "Medan")
    t3.tambahProduk("BUA001", "Jeruk Medan 1kg", 28000, 60, "Buah", 1000)
    t3.tambahProduk("BUA002", "Apel Fuji 1kg", 45000, 9, "Buah", 1000)
    t3.tambahProduk("BAY001", "Botol Minum Bayi", 65000, 20, "Ibu & Bayi", 250)
    t3.tambahProduk("FSH001", "Kain Ulos Batak", 350000, 5, "Fashion", 600)

    # ---------------- buyer ----------------
    mp.registrasiBuyer("Andi Pratama", "andi@mail.com", "081298765401", "buyer123",
                       "Jl. Gatot Subroto No. 10", "Medan")
    mp.registrasiBuyer("Dewi Lestari", "dewi@mail.com", "+6281298765402", "buyer123",
                       "Jl. Sudirman No. 5", "Jakarta")

    # ---------------- voucher ----------------
    mp.tambahVoucher(VoucherPersen("HEMAT10", 10, maksDiskon=50000, minBelanja=100000, kuota=50))
    mp.tambahVoucher(VoucherNominal("DISKON25K", 25000, minBelanja=200000, kuota=20))


AKUN_DEMO = [
    ("Seller", "rina@toko.com", "seller123", "Rina Gadget - Medan"),
    ("Seller", "budi@toko.com", "seller123", "Budi Otomotif - Jakarta"),
    ("Seller", "sari@toko.com", "seller123", "Sari Fresh & Baby - Medan"),
    ("Buyer", "andi@mail.com", "buyer123", "Medan"),
    ("Buyer", "dewi@mail.com", "buyer123", "Jakarta"),
]
