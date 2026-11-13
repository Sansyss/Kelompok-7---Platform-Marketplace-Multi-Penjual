class ProdukIterator:
    def __init__(self, daftarProduk, hanyaTersedia=False):
        self.__daftarProduk = daftarProduk
        self.__hanyaTersedia = hanyaTersedia
        self.__indeks = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.__indeks < len(self.__daftarProduk):
            produk = self.__daftarProduk[self.__indeks]
            self.__indeks += 1
            if not self.__hanyaTersedia or produk.stok > 0:
                return produk
        raise StopIteration

class KatalogIterator:
    def __init__(self, daftarToko, saring=None):
        self.__daftarToko = daftarToko
        self.__saring = saring
        self.__indeksToko = 0
        self.__iteratorProduk = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.__iteratorProduk is None:
                if self.__indeksToko >= len(self.__daftarToko):
                    raise StopIteration
                self.__iteratorProduk = iter(self.__daftarToko[self.__indeksToko])
                self.__indeksToko += 1
            try:
                produk = next(self.__iteratorProduk)
            except StopIteration:
                self.__iteratorProduk = None
                continue
            if self.__saring is None or self.__saring(produk):
                return produk

def bagiHalaman(iterable, ukuran):
    halaman = []
    for item in iterable:
        halaman.append(item)
        if len(halaman) == ukuran:
            yield halaman
            halaman = []
    if halaman:
        yield halaman
