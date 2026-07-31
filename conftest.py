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
def temiz_veritaban(monkeypatch):

    orijinal_baglan = database.veritabani_baglan
    def test_baglan(dbname=None):
        return orijinal_baglan(TEST_DB)

    monkeypatch.setattr(database, "veritabani_baglan", test_baglan)
    monkeypatch.setattr(main, "veritabani_baglan", test_baglan)    

    baglanti = orijinal_baglan(TEST_DB)
    imlec = baglanti.cursor()

    imlec.execute("""
    DROP TABLE IF EXISTS ogrenciler, ogretmenler, fakulteler, bolumler, yoneticiler CASCADE""")
    
    baglanti.commit()
    baglanti.close()

    orijinal_hazirla = veritabani_hazirla
    orijinal_hazirla(TEST_DB)

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