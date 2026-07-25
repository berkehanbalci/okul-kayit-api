import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def veritabani_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def veritabani_hazirla():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()
    
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler(
            id INTEGER PRIMARY KEY,
            ad TEXT,
            soyad TEXT,
            telefon_no VARCHAR,
            mail TEXT,
            fakulte TEXT,
            bolum TEXT,
            guncel_donem INTEGER
        )
    """)

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS ogretmenler(
            id INTEGER PRIMARY KEY,
            ad TEXT,
            soyad TEXT,
            telefon_no VARCHAR,
            mail TEXT,
            fakulte TEXT,
            bolum TEXT)
    """)

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS yoneticiler(
            id INTEGER PRIMARY KEY,
            kullanici_adi TEXT UNIQUE,
            sifre_hash TEXT)
    """)

    baglanti.commit()
    baglanti.close()
