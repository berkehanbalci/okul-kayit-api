from pydantic import BaseModel, EmailStr

class Ogrenci(BaseModel):
    ogrenci_id: int
    ad: str
    soyad: str
    telefon_no: str 
    mail: EmailStr
    fakulte: str
    bolum: str
    guncel_donem: int

class Ogretmen(BaseModel):
    ogretmen_id: int
    ad: str
    soyad: str
    telefon_no: str
    mail: EmailStr
    fakulte: str
    bolum: str

class Yonetici(BaseModel):
    kullanici_adi: str
    sifre: str    

