from database import veritabani_hazirla, veritabani_baglan
from models import Ogrenci, Ogretmen
from fastapi import FastAPI, HTTPException, Depends
from auth import router as auth_router, token_dogrula

app = FastAPI()

veritabani_hazirla()

app.include_router(auth_router)

@app.get("/")
def ana_sayfa():
    return {"mesaj": "Okul Kayıt API Çalışıyor!"}

@app.get("/ogrenciler")
def ogrencileri_listele():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()
    imlec.execute("""
        SELECT ogrci.id, ogrci.ad, ogrci.soyad, ogrci.telefon_no, ogrci.mail, f.ad AS fakulte_adi, b.ad AS bolum_adi, ogrci.guncel_donem
        FROM ogrenciler ogrci
        INNER JOIN fakulteler f ON ogrci.fakulte = f.ad
        INNER JOIN bolumler b ON ogrci.bolum = b.ad
    """)
    satirlar = imlec.fetchall()
    baglanti.close()

    ogrenciler = []
    for satir in satirlar:
        ogrenci = {
            "id" : satir[0],
            "ad" : satir[1],
            "soyad" : satir[2],
            "telefon_no" : satir[3],
            "mail" : satir[4],
            "fakulte" : satir[5],
            "bolum" : satir[6],
            "guncel_donem": satir[7]
        }
        ogrenciler.append(ogrenci)
    return ogrenciler    

@app.get("/ogretmenler")
def ogretmenleri_listele():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()
    
    imlec.execute("""
        SELECT ogrme.id, ogrme.ad, ogrme.soyad, ogrme.telefon_no, ogrme.mail, f.ad AS fakulte_adi, b.ad AS bolum_adi
        FROM ogretmenler ogrme
        INNER JOIN fakulteler f ON ogrme.fakulte = f.ad
        INNER JOIN bolumler b ON ogrme.bolum = b.ad
    """)
    satirlar = imlec.fetchall()
    baglanti.close()

    ogretmenler = []

    for satir in satirlar:
        ogretmen = {
            "id" : satir[0],
            "ad" : satir[1],
            "soyad" : satir[2],
            "telefon_no" : satir[3],
            "mail" : satir[4],
            "fakulte" : satir[5],
            "bolum" : satir[6]
        }
        ogretmenler.append(ogretmen)
    return ogretmenler

@app.get("/ogrenciler/{ogrenci_id}")
def ogrenci_bilgisi(ogrenci_id: int):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT ogrci.id, ogrci.ad, ogrci.soyad, ogrci.telefon_no, ogrci.mail, f.ad AS fakulte_adi, b.ad AS bolum_adi, ogrci.guncel_donem
        FROM ogrenciler ogrci
        INNER JOIN fakulteler f ON ogrci.fakulte = f.ad
        INNER JOIN bolumler b ON ogrci.bolum = b.ad
        WHERE ogrci.id = %s
    """, (ogrenci_id,))
    satir = imlec.fetchone()
    baglanti.close()

    if satir is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı!")

    return {
            "id" : satir[0],
            "ad" : satir[1],
            "soyad" : satir[2],
            "telefon_no" : satir[3],
            "mail" : satir[4],
            "fakulte" : satir[5],
            "bolum" : satir[6],
            "guncel_donem": satir[7]
    }

@app.get("/ogretmenler/{ogretmen_id}")
def ogretmen_bilgisi(ogretmen_id: int):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT ogrme.id, ogrme.ad, ogrme.soyad, ogrme.telefon_no, ogrme.mail, f.ad AS fakulte_adi, b.ad AS bolum_adi
        FROM ogretmenler ogrme
        INNER JOIN fakulteler f ON ogrme.fakulte = f.ad
        INNER JOIN bolumler b ON ogrme.bolum = b.ad
        WHERE ogrme.id = %s
    """, (ogretmen_id,))

    satir = imlec.fetchone()
    baglanti.close()

    if satir is None:
        raise HTTPException(status_code=404, detail("Öğretmen bulunamadı!"))

    return {
        "id" : satir[0],
        "ad" : satir[1],
        "soyad" : satir[2],
        "telefon_no" : satir[3],
        "mail" : satir[4],
        "fakulte" : satir[5],
        "bolum" : satir[6]
    }    

@app.get("/ogrenci-fakulte-bolum-raporu")
def detayli_ogrenci_fakulte_raporu():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()
    imlec.execute("""
        SELECT f.id AS fakulte_id, f.ad AS fakulte_adi, b.id AS bolum_id, b.ad AS bolum_adi, COUNT(ogrci.id) AS toplam_ogrenci
        FROM ogrenciler ogrci
        INNER JOIN fakulteler f ON ogrci.fakulte = f.ad
        INNER JOIN bolumler b ON ogrci.bolum = b.ad
        GROUP BY f.id, f.ad, b.id, b.ad
        ORDER BY f.ad ASC
    """)

    satirlar = imlec.fetchall()
    baglanti.close()

    gecici_rapor = {}

    for satir in satirlar:
        fakulte_id = satir[0]
        fakulte = satir[1]
        bolum_id = satir[2]
        bolum = satir [3]
        sayi = satir[4]

        if fakulte not in gecici_rapor:
            gecici_rapor[fakulte] = {
                "fakulte_id" : fakulte_id,
                "fakulte_toplam" : 0,
                "bolumler_listesi": []
            }

        gecici_rapor[fakulte]["fakulte_toplam"] += sayi

        gecici_rapor[fakulte]["bolumler_listesi"].append({
            "bolum_id": bolum_id,
            "bolum_adi": bolum,
            "bolumdeki_toplam_ogrenci": sayi
        })

    nihai_rapor = []

    for fakulte_adi, fakulte_verisi in gecici_rapor.items():

        rapor = {
            "fakulte_id": fakulte_verisi["fakulte_id"],
            "fakulte_adi": fakulte_adi,
            "fakulte_toplam_ogreci": fakulte_verisi["fakulte_toplam"],
            "bolumler_ve_toplam_ogrenci_sayisi": fakulte_verisi["bolumler_listesi"]
        }

        nihai_rapor.append(rapor)

    return nihai_rapor      

