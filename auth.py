import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from models import Yonetici
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from fastapi import Depends
from database import veritabani_baglan

guvenlik_semasi = HTTPBearer()

load_dotenv()
GIZLI_ANAHTAR = os.getenv("GIZLI_ANAHTAR")
ALGORITMA = "HS256"
TOKEN_GECERLILIK_SURESI = 60

router = APIRouter()
sifreleme = CryptContext(schemes=["bcrypt"], deprecated="auto")


def token_olustur(kullanici_adi: str):
    son_kullanma = datetime.utcnow() + timedelta(minutes=TOKEN_GECERLILIK_SURESI)
    veri = {
        "sub": kullanici_adi,
        "exp": son_kullanma
    }

    token = jwt.encode(veri, GIZLI_ANAHTAR, algorithm = ALGORITMA)
    return token

def token_dogrula(kimlik: HTTPAuthorizationCredentials = Depends(guvenlik_semasi)):
    token = kimlik.credentials

    try:
        veri = jwt.decode(token, GIZLI_ANAHTAR, algorithms= [ALGORITMA])
        kullanici_adi = veri.get("sub")
        if kullanici_adi is None:
            raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token!")
        return kullanici_adi
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token!")

@router.post("/kayit")

def kayit_ol(yonetici: Yonetici):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT id
        FROM yoneticiler
        WHERE kullanici_adi = %s
    """, (yonetici.kullanici_adi,))
    sonuc = imlec.fetchone()

    if sonuc:
        baglanti.close()
        raise HTTPException(status_code=409, detail="Bu kullanıcı adı zaten alınmış!")

    sifre_hash = sifreleme.hash(yonetici.sifre)
    imlec.execute(
        "INSERT INTO yoneticiler (kullanici_adi, sifre_hash) VALUES(%s, %s)",(yonetici.kullanici_adi, sifre_hash)
    )

    baglanti.commit()
    baglanti.close()
    return{"mesaj": f"{yonetici.kullanici_adi} kaydedildi"}

@router.post("/giris")
def giris_yap(yonetici: Yonetici):
    baglanti = veritabani_baglan()
    imlec = baglanti.cursor()

    imlec.execute("""
        SELECT sifre_hash
        FROM yoneticiler
        WHERE kullanici_adi = %s
    """, (yonetici.kullanici_adi,)
    )

    sonuc = imlec.fetchone()
    if sonuc is None:
        baglanti.close()
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre geçersiz!")

    kayitli_hash = sonuc[0]

    if not sifreleme.verify(yonetici.sifre, kayitli_hash):
        baglanti.close()
        raise  HTTPException(status_code=401, detail="Kullanıcı adı veya şifre geçersiz!")

    token = token_olustur(yonetici.kullanici_adi)
    return {"access_token": token, "token_type": "bearer"}