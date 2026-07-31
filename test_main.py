def test_ana_sayfa(client):

    cevap = client.get("/")

    assert cevap.status_code == 200
    assert cevap.json() == {"mesaj": "Okul Kayıt API Çalışıyor!"}

def test_bos_ogrenci_listesi(client):

    cevap = client.get("/ogrenciler")

    assert cevap.status_code == 200
    assert cevap.json() == []

def test_fakulte_ekle(client, token):

    cevap = client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    assert cevap.status_code == 200
    assert "eklendi" in cevap.json()["mesaj"]

def test_ayni_fakulte_iki_kez_eklenemez(client, token):
    client.post("/fakulteler",
        json = {"ad": "Tıp"},
        headers=token
    )

    cevap = client.post("/fakulteler",
        json = {"ad": "Tıp"},
        headers=token
    )

    assert cevap.status_code == 409

def test_bolum_ekle(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    cevap = client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    assert cevap.status_code == 200
    assert "eklendi" in cevap.json()["mesaj"]

def test_geçerli_olmayan_fakulteye__bolum_eklenemez(client, token):

    cevap = client.post("/bolumler",
        json = {"ad": "Rastgele Bölüm", "fakulte_id": 9999},
        headers=token
    )

    assert cevap.status_code == 404

def test_ayni_bolum_iki_kez_eklenemez(client, token):
    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Test Bölüm", "fakulte_id": 1},
        headers=token
    )

    cevap = client.post("/bolumler",
        json = {"ad": "Test Bölüm", "fakulte_id": 1},
        headers=token
    )

    assert cevap.status_code == 409

def test_ogrenci_ekle(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    cevap = client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1,
            "guncel_donem": "1"
        },
        headers=token
    )

    assert cevap.status_code == 200
    assert "eklendi" in cevap.json()["mesaj"]

def test_ayni_ogrenci_id_iki_kez_eklenemez(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1,
            "guncel_donem": "1"
        },
        headers=token
    )

    cevap = client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1,
            "guncel_donem": "1"
        },
        headers=token
    )

    assert cevap.status_code == 409

def test_ogrenci_gecersiz_fakulteye_eklenemez(client, token):

    cevap = client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 9999,
            "bolum_id": 1,
            "guncel_donem": "1"
        },
        headers=token 
    )

    assert cevap.status_code == 404

def test_ogrenci_gecersiz_bolume_eklenemez(client, token):
    
    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    cevap = client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 9999,
            "guncel_donem": "1"
        },
        headers=token
    )

    assert cevap.status_code == 404

def test_ogretmen_ekle(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    cevap = client.post("/ogretmenler",
        json = {
            "ogretmen_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1
        },
        headers=token
    )

    assert cevap.status_code == 200
    assert "eklendi" in cevap.json()["mesaj"]

def test_ayni_ogretmen_id_iki_kez_eklenemez(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    client.post("/ogretmenler",
        json = {
            "ogretmen_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1
        },
        headers=token
    )

    cevap = client.post("/ogretmenler",
        json = {
            "ogretmen_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1
        },
        headers=token
    )

    assert cevap.status_code == 409

def test_ogretmen_gecersiz_fakulteye_eklenemez(client, token):

    cevap = client.post("/ogretmenler",
        json = {
            "ogretmen_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 9999,
            "bolum_id": 1
        },
        headers=token 
    )

    assert cevap.status_code == 404

def test_ogretmen_gecersiz_bolume_eklenemez(client, token):
    
    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    cevap = client.post("/ogretmenler",
        json = {
            "ogretmen_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 9999
        },
        headers=token
    )

    assert cevap.status_code == 404

def test_fakulte_sil(client ,token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    cevap = client.delete("/fakulte/sil?fakulte_id=1", headers=token)
    

    assert cevap.status_code == 200

    tekrar = client.delete("/fakulte/sil?fakulte_id=1", headers=token)
    assert tekrar.status_code == 404

def test_fakultenin_icinde_bolum_varsa_silinemez(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    cevap = client.delete("/fakulte/sil?fakulte_id=1", headers=token)

    assert cevap.status_code == 409

def test_fakultenin_icinde_ogrenci_varsa_silinemez(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    client.post("/ogrenciler",
        json = {
            "ogrenci_id": 1001,
            "ad": "Ahmet",
            "soyad": "Yılmaz",
            "telefon_no": "05551112233",
            "mail": "ahmet@ornek.com",
            "fakulte_id": 1,
            "bolum_id": 1,
            "guncel_donem": "1"
        },
        headers=token
    )

    cevap = client.delete("/fakulte/sil?fakulte_id=1", headers=token)

    assert cevap.status_code == 409

def test_bolum_sil(client, token):

    client.post("/fakulteler",
        json = {"ad": "Mühendislik Fakültesi"},
        headers=token
    )

    client.post("/bolumler",
        json = {"ad": "Bilgisiyar Mühendisliği", "fakulte_id": "1"},
        headers=token
    )

    cevap = client.delete("/bolum/sil?bolum_id=1", headers=token)

    assert cevap.status_code == 200

    tekrar = client.delete("/bolum/sil?bolum_id=1", headers=token)
    assert tekrar.status_code == 404



