from pydantic import BaseModel

class Urun(BaseModel):
    isim: str
    fiyat: float
    stok_durumu: bool = True

class UrunCikti(Urun):
    id: int
