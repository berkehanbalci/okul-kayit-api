import os
import pytest
from fastapi.testclient import TestClient
from database import veritabani_baglan, veritabani_hazirla
import main

TEST_DB = "okul_kayit_test_db"

if "test" not in TEST_DB:
    raise RuntimeError("Test veritabanı adında 'test' kelimesi geçmeli! Gerçek db koruması!")

@pytest.fixture
def client():
    return TestClient(main.app)

@pytest.fixture(autouse=True)
def temiz_veritaban():
    baglanti = veritabani_baglan(TEST_DB)
    imlec = baglanti.cursor()

    imlec.execute("""
    DROP TABLE IF EXISTS ogrenciler, ogretmenler, fakulteler, bolumler, yoneticiler CASCADE""")
    
    baglanti.commit()
    baglanti.close()

    veritabani_hazirla(TEST_DB)

    yield

@pytest.fixture
def token(client):
    client.post("/kayit", json={
        "kullanici_adi": "test_admin",
        "sifre": "test1234"
    })

    cevap = client.post("/giris", json={
        "kullanici_adi": "test_admin",
        "sifre": "test1234"
    })

    access_token = cevap.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}    