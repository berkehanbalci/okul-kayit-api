from pydantic import BaseModel, EmailStr

class Ogrenci(BaseModel):
    ogrenci_id: int
    ad: str
    soyad: str
    telefon_no: str 
    mail: EmailStr
    fakulte_id: int
    bolum_id: int
    guncel_donem: str

class Ogretmen(BaseModel):
    ogretmen_id: int
    ad: str
    soyad: str
    telefon_no: str
    mail: EmailStr
    fakulte_id: int
    bolum_id: int

class Yonetici(BaseModel):
    kullanici_adi: str
    sifre: str    

class Fakulte(BaseModel):
    ad: str

class Bolum(BaseModel):
    ad: str
    fakulte_id: int