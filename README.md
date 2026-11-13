## Cara menjalankan

```
python main.py   # aplikasi interaktif (menu Buyer & Seller)
python demo.py   # driver code: bukti inheritance, encapsulation, polymorphism, iterator, exception
```

Akun contoh (otomatis terisi):

| Peran  | Username    | Password   |
|--------|-------------|------------|
| Buyer  | andi        | andi1234   |
| Seller | elektrojaya | rahasia123 |
| Seller | pustakailmu | rahasia123 |

## Struktur

```
main.py                  Menu interaktif (Sesi, SesiBuyer, SesiSeller - Template Method)
demo.py                  Driver code
marketplace/
  pengguna.py            Pengguna (abstract) -> Buyer, Seller
  produk.py              Produk (abstract) -> ProdukFisik, ProdukDigital; Review
  toko.py                Toko
  keranjang.py           Keranjang, ItemKeranjang
  order.py               Order, ItemOrder, StatusOrder
  voucher.py             Voucher (abstract) -> VoucherPersen, VoucherNominal, VoucherGratisOngkir
  kurir.py               Kurir (abstract) -> KurirReguler, KurirEkspres, AmbilDiToko
  iterator.py            ProdukIterator, KatalogIterator (__iter__/__next__), generator bagiHalaman
  exceptions.py          MarketplaceError + 8 custom exception
  sistem.py              Marketplace (registrasi, login, pencarian, checkout, status, laporan, CSV)
  tampilan.py            Fungsi tampilan terminal
  utilitas.py            Validasi & format Rupiah
  data_contoh.py         Data contoh
diagram/
  class_diagram.mmd/.png
  exception_diagram.mmd/.png
```

## Fitur

- F1 Registrasi & login Buyer/Seller (inheritance dari Pengguna)
- F2 Seller membuat toko, menambah produk (nama, harga, stok, kategori), mengubah harga/stok
- F3 Pencarian berdasarkan nama/kategori, filter harga, 6 pilihan urutan
- F4 Keranjang, checkout, stok, order
- F5 Update status order, review, wishlist, voucher, ongkir, laporan penjualan, pembatalan order, ekspor CSV
- F6 Checkout menghasilkan satu order per seller dan mengurangi stok otomatis
- F7 Daftar order buyer beserta status dan riwayatnya
