from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List

app = FastAPI()

# -------------------------------
# VERİTABANI KURULUMU
# -------------------------------
def veritabani_kurulumu():
    connected = sqlite3.connect("veritabani.db")
    c = connected.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urunler(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            fiyat REAL,
            stok_durumu BOOLEAN DEFAULT 1
        )
    """)
    connected.commit()
    connected.close()

veritabani_kurulumu()

# -------------------------------
# MODELLER
# -------------------------------
class Urun(BaseModel):
    isim: str
    fiyat: float
    stok_durumu: bool = True

class UrunCikti(Urun):
    id: int

# -------------------------------
# VALIDATION 
# -------------------------------
def fiyat_kontrol(fiyat: float):
    if fiyat <= 0:
        raise HTTPException(status_code=400, detail="Fiyat 0'dan büyük olmalı")

# -------------------------------
# ÜRÜN EKLE
# -------------------------------
@app.post("/urun_ekle", response_model=UrunCikti)
def urun_ekle(urun: Urun):

    fiyat_kontrol(urun.fiyat)

    connected = sqlite3.connect("veritabani.db")
    c = connected.cursor()

    try:
        c.execute(
            "INSERT INTO urunler (isim, fiyat, stok_durumu) VALUES (?, ?, ?)",
            (urun.isim, urun.fiyat, urun.stok_durumu)
        )
        connected.commit()

        return {
            "id": c.lastrowid,
            **urun.dict()
        }

    finally:
        connected.close()

# -------------------------------
# TÜM ÜRÜNLERİ LİSTELE
# -------------------------------
@app.get("/urunler", response_model=List[UrunCikti])
def urunleri_listele():

    connected = sqlite3.connect("veritabani.db")
    connected.row_factory = sqlite3.Row
    c = connected.cursor()

    try:
        c.execute("SELECT * FROM urunler")
        rows = c.fetchall()
        return [dict(row) for row in rows]

    finally:
        connected.close()

# -------------------------------
# ÜRÜN SİL 
# -------------------------------
@app.delete("/urun/{id}")
def urun_sil(id: int):

    connected = sqlite3.connect("veritabani.db")
    c = connected.cursor()

    c.execute("SELECT * FROM urunler WHERE id = ?", (id,))
    urun = c.fetchone()

    if not urun:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    c.execute("DELETE FROM urunler WHERE id = ?", (id,))
    connected.commit()
    connected.close()

    return {"message": "Ürün silindi"}

# -------------------------------
# ÜRÜN GÜNCELLE 
# -------------------------------
@app.put("/urun/{id}")
def urun_guncelle(id: int, urun: Urun):

    fiyat_kontrol(urun.fiyat)

    connected = sqlite3.connect("veritabani.db")
    c = connected.cursor()

    c.execute("SELECT * FROM urunler WHERE id = ?", (id,))
    mevcut = c.fetchone()

    if not mevcut:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    c.execute("""
        UPDATE urunler 
        SET isim = ?, fiyat = ?, stok_durumu = ?
        WHERE id = ?
    """, (urun.isim, urun.fiyat, urun.stok_durumu, id))

    connected.commit()
    connected.close()

    return {"message": "Ürün güncellendi"}