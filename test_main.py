def test_ana_sayfa(client):

    cevap = client.get("/")

    assert cevap.status_code == 200
    assert cevap.json() == {"mesaj": "Okul Kayıt API Çalışıyor!"}

def test_bos_ogrenci_listesi(client):

    cevap = client.get("/ogrenciler")

    assert cevap.status_code == 200
    assert cevap.json() == []
