from database import veritabani_hazirla, veritabani_baglan
from models import Ogrenci, Ogretmen, Fakulte, Bolum
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
        INNER JOIN fakulteler f ON ogrci.fakulte_id = f.id
        INNER JOIN bolumler b ON ogrci.bolum_id = b.id
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
        INNER JOIN fakulteler f ON ogrme.fakulte_id = f.id
        INNER JOIN bolumler b ON ogrme.bolum_id = b.id
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
        INNER JOIN fakulteler f ON ogrci.fakulte_id = f.id
        INNER JOIN bolumler b ON ogrci.bolum_id = b.id
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
        INNER JOIN fakulteler f ON ogrme.fakulte_id = f.id
        INNER JOIN bolumler b ON ogrme.bolum_id = b.id
        WHERE ogrme.id = %s
    """, (ogretmen_id,))

    satir = imlec.fetchone()
    baglanti.close()

    if satir is None:
        raise HTTPException(status_code=404, detail="Öğretmen bulunamadı!")

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
        FROM fakulteler f
        LEFT JOIN bolumler b ON b.fakulte_id = f.id
        LEFT JOIN ogrenciler ogrci ON ogrci.bolum_id = b.id
        GROUP BY f.id, f.ad, b.id, b.ad
        ORDER BY f.ad ASC
    """)

    satirlar = imlec.fetchall()
    baglanti.close()

    gecici_rapor = {}

    for satir in satirlar:
        fakulte_id = satir[0]
        fakulte_ad = satir[1]
        bolum_id = satir[2]
        bolum = satir [3]
        sayi = satir[4]

        if fakulte_ad not in gecici_rapor:
            gecici_rapor[fakulte_ad] = {
                "fakulte_id" : fakulte_id,
                "fakulte_toplam" : 0,
                "bolumler_listesi": []
            }

        gecici_rapor[fakulte_ad]["fakulte_toplam"] += sayi

        gecici_rapor[fakulte_ad]["bolumler_listesi"].append({
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

@app.get("/ogretmen-fakulte_bolum_raporu")
def detayli_ogretmen_fakulte_raporu():
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT f.id AS fakulte_id, f.ad AS fakulte_adi, b.id AS bolum_id, b.ad AS bolum_adi, COUNT(ogrme.id) AS toplam_ogretmen
        FROM fakulteler f
        LEFT JOIN bolumler b ON b.fakulte_id = f.id
        LEFT JOIN ogretmenler ogrme ON ogrme.bolum_id = b.id
        GROUP BY f.id, f.ad, b.id, b.ad
        ORDER BY f.ad ASC
    """)

    satirlar = imlec.fetchall()
    baglanti.close()

    gecici_rapor = {}

    for satir in satirlar:
        fakulte_id = satir[0]
        fakulte_ad = satir[1]
        bolum_id = satir[2]
        bolum_ad = satir[3]
        sayi = satir[4]

        if fakulte_ad not in gecici_rapor:
            gecici_rapor[fakulte_ad] = {
                "fakulte_id": fakulte_id,
                "fakulte_toplam" : 0,
                "bolumler_listesi" : []
            }

        gecici_rapor[fakulte_ad]["fakulte_toplam"] +=  sayi 

        gecici_rapor[fakulte_ad]["bolumler_listesi"].append({
            "bolum_id": bolum_id,
            "bolum_ad": bolum_ad,
            "bolumdeki_toplam_ogretmen": sayi
        })

    nihai_rapor = []

    for fakulte_adi, fakulte_verisi in gecici_rapor.items():
        rapor = {
            "fakulte_id": fakulte_verisi["fakulte_id"],
            "fakulte_ad": fakulte_adi,
            "fakulte_toplam_ogretmen": fakulte_verisi["fakulte_toplam"],
            "bolumler_ve_toplam_ogretmen_sayisi": fakulte_verisi["bolumler_listesi"]
        }

        nihai_rapor.append(rapor)

    return nihai_rapor 

@app.post("/ogrenciler")
def yeni_ogrenci_ekle(ogrenci: Ogrenci, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogrenciler
        WHERE id = %s
    """,(ogrenci.ogrenci_id,)
    )

    sonuc = imlec.fetchone()        

    if sonuc:
        baglanti.close()
        raise HTTPException(status_code=409, detail=f"{ogrenci.ogrenci_id} numarası zaten kullanımda!")

    else:
        imlec.execute("""
            SELECT id
            FROM fakulteler 
            WHERE id = %s

        """, (ogrenci.fakulte_id,)
        )

        ogrenci_fakulte_sonuc = imlec.fetchone()

        if ogrenci_fakulte_sonuc:
            ogrenci_fakulte_id = ogrenci_fakulte_sonuc[0]

            imlec.execute("""
                SELECT id
                FROM bolumler
                WHERE id = %s AND fakulte_id = %s
            """, (ogrenci.bolum_id, ogrenci.fakulte_id)
            )
            ogrenci_bolum_sonuc = imlec.fetchone()

            if ogrenci_bolum_sonuc:
                ogrenci_bolum_id = ogrenci_bolum_sonuc[0]
                imlec.execute(
                    """INSERT INTO ogrenciler (id, ad, soyad, telefon_no, mail, fakulte_id, bolum_id, guncel_donem)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (ogrenci.ogrenci_id, ogrenci.ad, ogrenci.soyad, ogrenci.telefon_no, ogrenci.mail, ogrenci_fakulte_id, ogrenci_bolum_id, ogrenci.guncel_donem)
                )
                mesaj = f"{ogrenci.ogrenci_id} numaralı öğrenci sisteme eklendi"
            else:
                baglanti.close()
                raise HTTPException(status_code=404, detail=f"{ogrenci.bolum_id} id'li bölüm bu fakülteye ait değil veya bulunamadı!")  
        
        else:
            baglanti.close()
            raise HTTPException(status_code=404, detail=f"{ogrenci.fakulte_id} id numaralı fakülte bulunamadı!")
    
    baglanti.commit()
    baglanti.close()
    return{"mesaj": mesaj}

@app.post("/ogretmenler")
def yeni_ogretmen_ekle(ogretmen: Ogretmen, kullanici_adi: str = Depends(token_dogrula)):
    
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogretmenler
        WHERE id = %s
    """, (ogretmen.ogretmen_id,))

    sonuc = imlec.fetchone()

    if sonuc:
        baglanti.close()
        raise HTTPException(status_code=409, detail=f"{ogretmen.ogretmen_id} numarası zaten kullanımda")

    else:
        imlec.execute("""
            SELECT id
            FROM fakulteler
            WHERE id = %s
        """, (ogretmen.fakulte_id,))

        ogretmen_fakulte_sonuc = imlec.fetchone()

        if ogretmen_fakulte_sonuc:
            ogretmen_fakulte_id = ogretmen_fakulte_sonuc[0]

            imlec.execute("""
                SELECT id
                FROM bolumler
                WHERE id = %s AND fakulte_id = %s
                """, (ogretmen.bolum_id, ogretmen.fakulte_id)
            )

            ogretmen_bolum_sonuc = imlec.fetchone()

            if ogretmen_bolum_sonuc:
                ogretmen_bolum_id = ogretmen_bolum_sonuc[0]

                imlec.execute(
                    """INSERT INTO ogretmenler (id, ad, soyad, telefon_no, mail, fakulte_id, bolum_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (ogretmen.ogretmen_id, ogretmen.ad, ogretmen.soyad, ogretmen.telefon_no, ogretmen.mail, ogretmen_fakulte_id, ogretmen_bolum_id)
                )
                mesaj = f"{ogretmen.ogretmen_id} numaralı öğretmen sisteme eklendi"
            else:
                baglanti.close()
                raise HTTPException(status_code=404, detail=f"{ogretmen.bolum_id} id'li bölüm bu fakülteye ait değil veya bulunamadı!")
        
        else:
            baglanti.close()
            raise HTTPException(status_code=404, detail=f"{ogretmen.fakulte_id} id numaralı fakülte bulunamadı!")

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.post("/fakulteler")
def fakulte_ekle(fakulte: Fakulte, kullanici_adi: str = Depends(token_dogrula)):

    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM fakulteler
        WHERE ad = %s
    """, (fakulte.ad,))

    fakulte_ekle_sonuc = imlec.fetchone()

    if fakulte_ekle_sonuc:
        baglanti.close()
        raise HTTPException(status_code=409, detail=f"{fakulte.ad} fakültesi zaten mevcut!")

    else:
        imlec.execute("""
        INSERT INTO fakulteler (ad) VALUES (%s)""", (fakulte.ad,))

        mesaj = f"{fakulte.ad} fakültesi sisteme eklendi"   

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.post("/bolumler")
def bolum_ekle(bolum: Bolum, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM bolumler
        WHERE ad = %s
    """, (bolum.ad, ))

    bolum_ekle_sonuc = imlec.fetchone()

    if bolum_ekle_sonuc:
        baglanti.close()
        raise HTTPException(status_code=409, detail=f"{bolum.ad} bölümü zaten mevcut!")

    imlec.execute("SELECT id FROM fakulteler WHERE id = %s", (bolum.fakulte_id,))
    if imlec.fetchone() is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{bolum.fakulte_id} id numaralı fakülte bulunamadı!")
    
    imlec.execute("""
    INSERT INTO bolumler (ad, fakulte_id) VALUES (%s, %s)""", (bolum.ad, bolum.fakulte_id))

    mesaj = f"{bolum.ad} bölümü sisteme eklendi"

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.put("/ogrenciler/guncelle")
def ogrenci_guncelle(ogrenci: Ogrenci, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogrenciler
        Where id = %s
    """, (ogrenci.ogrenci_id,))

    sonuc = imlec.fetchone()

    if sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogrenci.ogrenci_id} numaralı öğrenci bulunamadı!")

    imlec.execute("""
        SELECT id
        FROM fakulteler
        WHERE id = %s
    """, (ogrenci.fakulte_id,))    

    fakulte_sonuc = imlec.fetchone()

    if fakulte_sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogrenci.fakulte_id} numaralı fakulte id'si mevcut değildir!")

    fakulte_id = fakulte_sonuc[0]
    imlec.execute("""
        SELECT id
        FROM bolumler
        WHERE id = %s AND fakulte_id = %s
        """, (ogrenci.bolum_id, ogrenci.fakulte_id))

    bolum_sonuc = imlec.fetchone()

    if bolum_sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogrenci.bolum_id} id'li bölüm bu fakülteye ait değil veya bulunamadı!")

    bolum_id = bolum_sonuc[0]

    imlec.execute("""
    UPDATE ogrenciler SET ad = %s, soyad = %s, telefon_no = %s, mail = %s, fakulte_id = %s, bolum_id = %s, guncel_donem = %s
    WHERE id = %s""", (ogrenci.ad, ogrenci.soyad, ogrenci.telefon_no, ogrenci.mail, fakulte_id, bolum_id, ogrenci.guncel_donem, ogrenci.ogrenci_id))

    mesaj = f"{ogrenci.ogrenci_id} numaralı öğrenci başarıyla güncellendi"

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.put("/ogretmenler/guncelle")
def ogretmen_guncelle(ogretmen: Ogretmen, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogretmenler
        WHERE id = %s
    """, (ogretmen.ogretmen_id,))

    sonuc = imlec.fetchone()

    if sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogretmen.ogretmen_id} numaralı öğretmen bulunamadı")

    imlec.execute("""
        SELECT id
        FROM fakulteler
        WHERE id = %s
    """, (ogretmen.fakulte_id,))

    fakulte_sonuc = imlec.fetchone()

    if fakulte_sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogretmen.fakulte_id} numaralı fakulte id'si mevcut değildir!")

    fakulte_id = fakulte_sonuc[0]

    imlec.execute("""
        SELECT id
        FROM bolumler
        WHERE id = %s AND fakulte_id = %s
        """, (ogretmen.bolum_id, ogretmen.fakulte_id))

    bolum_sonuc = imlec.fetchone()

    if bolum_sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogretmen.bolum_id} id'li bölüm bu fakülteye ait değil veya bulunamadı!")

    bolum_id = bolum_sonuc[0]

    imlec.execute("""
    UPDATE ogretmenler SET ad = %s, soyad = %s, telefon_no = %s, mail = %s, fakulte_id = %s, bolum_id = %s
    WHERE id = %s""", (ogretmen.ad, ogretmen.soyad, ogretmen.telefon_no, ogretmen.mail, fakulte_id, bolum_id, ogretmen.ogretmen_id))

    mesaj = f"{ogretmen.ogretmen_id} numaralı öğretmen başarıyla güncellendi"    

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.delete("/ogrenci/sil")
def ogrenci_sil(ogrenci_id : int, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogrenciler
        WHERE id = %s
    """, (ogrenci_id,))

    sonuc = imlec.fetchone()

    if sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogrenci_id} numaralı öğrenci bulunamadı!")

    imlec.execute("""
    DELETE FROM ogrenciler WHERE id = %s""", (ogrenci_id,))

    mesaj = f"{ogrenci_id} numaralı öğrenci başarıyla silindi"    

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.delete("/ogretmen/sil")
def ogretmen_sil(ogretmen_id: int, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogretmenler
        WHERE id = %s
    """, (ogretmen_id,))

    sonuc = imlec.fetchone()

    if sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=404, detail=f"{ogretmen_id} numaralı öğretmen bulunamadı")

    imlec.execute("""
    DELETE FROM ogretmenler WHERE id = %s""", (ogretmen_id,))

    mesaj = f"{ogretmen_id} numaralı öğretmen başarıyla silindi"

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.delete("/bolum/sil")
def bolum_sil(bolum_id: int, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogrenciler
        WHERE bolum_id = %s
    """, (bolum_id, ))

    ogrenci_icin_sonuc = imlec.fetchone()

    if ogrenci_icin_sonuc is not None:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu bölümde kayıtlı öğrenci var, önce öğrenciyi güncelleyin veya silin!")

    imlec.execute("""
        SELECT id
        FROM ogretmenler
        WHERE bolum_id = %s
    """, (bolum_id,))

    ogretmen_icin_sonuc = imlec.fetchone()

    if ogretmen_icin_sonuc is not None:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu bölümde kayıtlı öğretmen var, önce öğretmeni güncelleyin veya silin!")

    imlec.execute("""
    DELETE FROM bolumler WHERE id = %s""", (bolum_id,))

    mesaj = f"{bolum_id} numaraya sahip bölüm başarıyla silindi"

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}

@app.delete("/fakulte/sil")
def fakulte_sil(fakulte_id: int, kullanici_adi: str = Depends(token_dogrula)):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM ogrenciler
        WHERE fakulte_id = %s
    """, (fakulte_id,))

    ogrenci_icin_sonuc = imlec.fetchone()

    if ogrenci_icin_sonuc is not None:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu fakültede öğrenci var, önce öğrenciyi güncelleyin veya silin!")

    imlec.execute("""
        SELECT id
        FROM ogretmenler
        WHERE fakulte_id = %s
    """, (fakulte_id,))

    ogretmen_icin_sonuc = imlec.fetchone()

    if ogretmen_icin_sonuc is not None:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu fakültede öğretmen var, önce öğretmeni güncelleyin veya silin!")

    imlec.execute("""
        SELECT id
        FROM bolumler
        WHERE fakulte_id = %s
    """, (fakulte_id,))

    bolum_icin_sonuc = imlec.fetchone()

    if bolum_icin_sonuc is not None:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu fakültede bölüm var, önce bölümü güncelleyin veya silin!")

    imlec.execute("""
    DELETE FROM fakulteler WHERE id = %s""", (fakulte_id,))

    mesaj = f"{fakulte_id} numaralı fakülte başarıyla silindi"

    baglanti.commit()
    baglanti.close()
    return {"mesaj": mesaj}      