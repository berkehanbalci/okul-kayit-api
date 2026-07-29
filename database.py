import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def veritabani_baglan(dbname: str = None):
  
    if dbname is None:
        dbname = os.getenv("DB_NAME")
 
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=dbname,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
 
 
def veritabani_hazirla(dbname: str = None):
    baglanti = veritabani_baglan(dbname)
    imlec = baglanti.cursor()
    
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS fakulteler(
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100) UNIQUE)
    """)

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS bolumler(
            id SERIAL PRIMARY KEY,
            ad VARCHAR(100) UNIQUE,
            fakulte_id INTEGER REFERENCES fakulteler(id))
    """)

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS yoneticiler(
            id SERIAL PRIMARY KEY,
            kullanici_adi TEXT UNIQUE,
            sifre_hash TEXT)
    """)
    
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler(
            id INTEGER PRIMARY KEY,
            ad VARCHAR(100),
            soyad VARCHAR(100),
            telefon_no VARCHAR(11),
            mail VARCHAR(100),
            fakulte_id INTEGER REFERENCES fakulteler(id),
            bolum_id INTEGER REFERENCES bolumler(id),
            guncel_donem VARCHAR(20)
        )
    """)

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS ogretmenler(
            id INTEGER PRIMARY KEY,
            ad VARCHAR(100),
            soyad VARCHAR(100),
            telefon_no VARCHAR(11),
            mail VARCHAR(100),
            fakulte_id INTEGER REFERENCES fakulteler(id),
            bolum_id  INTEGER REFERENCES bolumler(id)
            )
    """)

    
    baglanti.commit()
    baglanti.close()
