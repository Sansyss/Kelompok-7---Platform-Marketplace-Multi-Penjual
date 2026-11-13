class MarketplaceError(Exception):
    pass

class ValidasiError(MarketplaceError):
    pass

class AutentikasiError(MarketplaceError):
    pass

class AksesDitolakError(MarketplaceError):
    pass

class DataTidakDitemukanError(MarketplaceError):
    pass

class StokTidakCukupError(MarketplaceError):
    def __init__(self, namaProduk, stokTersedia, diminta):
        self.namaProduk = namaProduk
        self.stokTersedia = stokTersedia
        self.diminta = diminta
        super().__init__(f"Stok '{namaProduk}' tidak cukup (tersedia {stokTersedia}, diminta {diminta}).")

class KeranjangKosongError(MarketplaceError):
    def __init__(self):
        super().__init__("Keranjang masih kosong, tambahkan produk terlebih dahulu.")

class VoucherTidakValidError(MarketplaceError):
    pass

class StatusOrderError(MarketplaceError):
    def __init__(self, statusLama, statusBaru):
        self.statusLama = statusLama
        self.statusBaru = statusBaru
        super().__init__(f"Status order tidak bisa diubah dari '{statusLama.value}' ke '{statusBaru.value}'.")
