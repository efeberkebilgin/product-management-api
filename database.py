import sqlite3

DB_NAME = "veritabani.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def veritabani_kurulumu():
    connected = get_connection()
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