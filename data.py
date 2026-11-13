from .produk import ProdukDigital, ProdukFisik
from .voucher import VoucherGratisOngkir, VoucherNominal, VoucherPersen

AKUN_CONTOH = (
    ("Buyer", "andi", "andi1234"),
    ("Seller", "elektrojaya", "rahasia123"),
    ("Seller", "pustakailmu", "rahasia123"),
)

def isiDataContoh(marketplace):
    seller1 = marketplace.registrasiSeller("elektrojaya", "rahasia123", "Budi Santoso",
                                          "budi@mail.com", "081234567890", "Medan")
    toko1 = marketplace.bukaToko(seller1, "Elektro Jaya")
    toko1.tambahProduk(ProdukFisik("Kipas Angin", 250000, 20, "Elektronik", toko1, 3000))
    toko1.tambahProduk(ProdukFisik("Laptop ASUS Vivobook", 7000000, 5, "Elektronik", toko1, 1800))
    toko1.tambahProduk(ProdukFisik("Mouse Wireless", 85000, 3, "Aksesoris Komputer", toko1, 150))
    toko1.tambahProduk(ProdukDigital("Antivirus 1 Tahun", 150000, 50, "Software", toko1, "Lisensi"))
    toko1.tambahVoucher(VoucherPersen("ELEKTRO10", 10, 100000, minBelanja=500000, kuota=20))
    seller2 = marketplace.registrasiSeller("pustakailmu", "rahasia123", "Siti Aminah",
                                          "siti@mail.com", "082233445566", "Jakarta")
    toko2 = marketplace.bukaToko(seller2, "Pustaka Ilmu")
    toko2.tambahProduk(ProdukFisik("Buku Pemrograman Python", 120000, 15, "Buku", toko2, 500))
    toko2.tambahProduk(ProdukFisik("Pulpen Gel Isi 12", 36000, 40, "Alat Tulis", toko2, 200))
    toko2.tambahProduk(ProdukDigital("E-book Belajar OOP", 50000, 100, "Buku", toko2, "PDF"))
    toko2.tambahProduk(ProdukFisik("Buku Struktur Data", 95000, 0, "Buku", toko2, 450))
    toko2.tambahVoucher(VoucherNominal("HEMAT15", 15000, minBelanja=100000, kuota=10))
    toko2.tambahVoucher(VoucherGratisOngkir("ONGKIR0", 20000, minBelanja=50000, kuota=5))
    marketplace.registrasiBuyer("andi", "andi1234", "Andi Wijaya", "andi@mail.com",
                                "081311112222", "Medan", "Jl. Gatot Subroto No. 10")
