# Okul Kayıt API

Öğrenci, öğretmen, fakülte ve bölüm kayıtlarını yöneten, JWT tabanlı kimlik doğrulama içeren bir REST API. FastAPI ve PostgreSQL ile geliştirilmiştir.

## İçindekiler

- [Özellikler](#özellikler)
- [Teknoloji Yığını](#teknoloji-yığını)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum (Docker ile — Önerilen)](#kurulum-docker-ile--önerilen)
- [Kurulum (Docker olmadan — Yerel)](#kurulum-docker-olmadan--yerel)
- [Ortam Değişkenleri](#ortam-değişkenleri)
- [API Uç Noktaları](#api-uç-noktaları)
- [Kimlik Doğrulama Kullanımı](#kimlik-doğrulama-kullanımı)
- [Testleri Çalıştırma](#testleri-çalıştırma)
- [Veritabanı Yapısı](#veritabanı-yapısı)

## Özellikler

- Öğrenci, öğretmen, fakülte ve bölümler için tam CRUD işlemleri (ekleme, listeleme, güncelleme, silme)
- JWT (JSON Web Token) tabanlı kimlik doğrulama; yazma işlemleri (POST, PUT, DELETE) token korumalı
- Şifreler bcrypt ile hash'lenerek saklanır
- Foreign key (yabancı anahtar) ilişkileriyle veri bütünlüğü koruması: bağlı kayıtları olan bir fakülte veya bölüm silinemez
- Fakülte–bölüm uyum kontrolü: bir öğrenci/öğretmen, yalnızca gerçekten o fakülteye ait olan bir bölüme kaydedilebilir
- LEFT JOIN kullanan rapor uç noktaları: öğrencisi/öğretmeni olmayan fakülte ve bölümler de 0 sayısıyla listelenir
- Kapsamlı otomatik test paketi (37 test, ~%82 kod kapsamı); testler ayrı bir test veritabanında izole çalışır
- Docker ve Docker Compose ile tek komutla ayağa kalkma

## Teknoloji Yığını

- **FastAPI** — web çatısı ve otomatik Swagger dokümantasyonu
- **PostgreSQL** — ilişkisel veritabanı
- **psycopg2** — PostgreSQL sürücüsü (ham SQL sorguları)
- **python-jose** — JWT üretme ve doğrulama
- **passlib + bcrypt** — şifre hash'leme
- **Pydantic** — veri doğrulama ve modelleme (e-posta doğrulaması dahil)
- **python-dotenv** — ortam değişkeni yönetimi
- **pytest + httpx** — test altyapısı
- **Docker + Docker Compose** — konteynerleştirme

## Proje Yapısı

```
okul-kayit-api/
├── main.py              # API uç noktaları (endpoint'ler)
├── models.py            # Pydantic veri modelleri
├── database.py          # Veritabanı bağlantısı ve tablo oluşturma
├── auth.py              # Kayıt, giriş ve JWT token doğrulama
├── conftest.py          # pytest fixture'ları (test istemcisi, test DB, token)
├── test_main.py         # Otomatik testler
├── requirements.txt     # Python bağımlılıkları
├── Dockerfile           # API uygulamasının konteyner tarifi
├── docker-compose.yml   # API + PostgreSQL servislerini birlikte çalıştırır
├── .dockerignore        # Docker imajına dahil edilmeyecek dosyalar
├── .env.example         # Ortam değişkeni şablonu
└── .gitignore           # Git'in yok sayacağı dosyalar
```

## Kurulum (Docker ile — Önerilen)

Bu yöntemle bilgisayarınızda Python veya PostgreSQL kurulu olmasına gerek yoktur; yalnızca Docker Desktop yeterlidir.

**1. Depoyu klonlayın:**

```bash
git clone https://github.com/berkehanbalci/okul-kayit-api.git
cd okul-kayit-api
```

**2. Ortam değişkeni dosyasını oluşturun:**

```bash
cp .env.example .env
```

Ardından `.env` dosyasını açıp `DB_PASSWORD` ve `GIZLI_ANAHTAR` değerlerini kendinize göre doldurun (bkz. [Ortam Değişkenleri](#ortam-değişkenleri)).

**3. Docker Desktop'ın açık olduğundan emin olun, sonra çalıştırın:**

```bash
docker compose up --build
```

Bu komut PostgreSQL veritabanını ve API'yi birlikte ayağa kaldırır. İlk çalıştırmada imajların indirilmesi/derlenmesi birkaç dakika sürebilir.

**4. Tarayıcıdan erişin:**

```
http://localhost:8000/docs
```

Swagger arayüzü üzerinden tüm uç noktaları görebilir ve test edebilirsiniz.

> **Not:** `docker-compose.yml` içinde PostgreSQL, ana bilgisayarda yerel bir PostgreSQL ile çakışmayı önlemek için dış `5434` portuna yönlendirilmiştir. Veritabanına bir istemciyle (örneğin pgAdmin) dışarıdan bağlanmak isterseniz `localhost:5434` kullanın.

Durdurmak için `Ctrl+C`, konteynerleri kaldırmak için `docker compose down`, veritabanı verisini de sıfırlamak için `docker compose down -v` komutlarını kullanabilirsiniz.

## Kurulum (Docker olmadan — Yerel)

**1. PostgreSQL'in kurulu ve çalışır durumda olduğundan emin olun.** Ardından bir veritabanı oluşturun:

```sql
CREATE DATABASE okul_kayit_db;
```

**2. Bağımlılıkları kurun:**

```bash
pip install -r requirements.txt
```

**3. `.env` dosyasını oluşturun** ve yerel PostgreSQL bilgilerinize göre doldurun. Yerel çalıştırmada `DB_HOST=localhost` olmalıdır:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=okul_kayit_db
DB_USER=postgres
DB_PASSWORD=kendi_sifreniz
GIZLI_ANAHTAR=rastgele_uzun_bir_anahtar
```

**4. Uygulamayı başlatın:**

```bash
uvicorn main:app --reload
```

**5. Tarayıcıdan erişin:** `http://localhost:8000/docs`

## Ortam Değişkenleri

| Değişken | Açıklama | Docker'da | Yerelde |
|---|---|---|---|
| `DB_HOST` | Veritabanı sunucusunun adresi | `db` (compose tarafından otomatik verilir) | `localhost` |
| `DB_PORT` | Veritabanı portu | `5432` | `5432` |
| `DB_NAME` | Veritabanı adı | `okul_kayit_db` | `okul_kayit_db` |
| `DB_USER` | Veritabanı kullanıcısı | `postgres` | `postgres` |
| `DB_PASSWORD` | Veritabanı şifresi | `.env`'den okunur | `.env`'den okunur |
| `GIZLI_ANAHTAR` | JWT imzalama anahtarı | `.env`'den okunur | `.env`'den okunur |

Docker ile çalıştırırken `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` değerleri `docker-compose.yml` tarafından sağlanır; `.env` dosyasında yalnızca `DB_PASSWORD` ve `GIZLI_ANAHTAR` doldurmanız yeterlidir.

`GIZLI_ANAHTAR` için güçlü, rastgele bir değer üretmek isterseniz:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **Uyarı:** Gerçek `.env` dosyası gizli bilgiler içerir ve depoya gönderilmemelidir (`.gitignore` ile korunur). Depoya yalnızca `.env.example` şablonu dahil edilir.

## API Uç Noktaları

### Genel

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| GET | `/` | API'nin çalıştığını doğrulayan karşılama mesajı | Gerekmez |

### Kimlik Doğrulama

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| POST | `/kayit` | Yeni yönetici kaydı oluşturur | Gerekmez |
| POST | `/giris` | Giriş yapar ve JWT token döndürür | Gerekmez |

### Öğrenci

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| GET | `/ogrenciler` | Tüm öğrencileri listeler | Gerekmez |
| GET | `/ogrenciler/{ogrenci_id}` | Tek bir öğrencinin bilgisini getirir | Gerekmez |
| POST | `/ogrenciler` | Yeni öğrenci ekler | Gerekli |
| PUT | `/ogrenciler/guncelle/{ogrenci_id}` | Öğrenci bilgilerini günceller | Gerekli |
| DELETE | `/ogrenci/sil/{ogrenci_id}` | Öğrenci siler | Gerekli |

### Öğretmen

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| GET | `/ogretmenler` | Tüm öğretmenleri listeler | Gerekmez |
| GET | `/ogretmenler/{ogretmen_id}` | Tek bir öğretmenin bilgisini getirir | Gerekmez |
| POST | `/ogretmenler` | Yeni öğretmen ekler | Gerekli |
| PUT | `/ogretmenler/guncelle/{ogretmen_id}` | Öğretmen bilgilerini günceller | Gerekli |
| DELETE | `/ogretmen/sil/{ogretmen_id}` | Öğretmen siler | Gerekli |

### Fakülte

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| POST | `/fakulteler` | Yeni fakülte ekler | Gerekli |
| DELETE | `/fakulte/sil/{fakulte_id}` | Fakülte siler (bağlı öğrenci/öğretmen/bölüm yoksa) | Gerekli |

### Bölüm

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| POST | `/bolumler` | Bir fakülteye bağlı yeni bölüm ekler | Gerekli |
| DELETE | `/bolum/sil/{bolum_id}` | Bölüm siler (bağlı öğrenci/öğretmen yoksa) | Gerekli |

### Raporlar

| Metot | Yol | Açıklama | Kimlik Doğrulama |
|---|---|---|---|
| GET | `/ogrenci-fakulte-bolum-raporu` | Fakülte ve bölüm bazında öğrenci sayıları | Gerekmez |
| GET | `/ogretmen-fakulte_bolum_raporu` | Fakülte ve bölüm bazında öğretmen sayıları | Gerekmez |

## Kimlik Doğrulama Kullanımı

Yazma işlemleri (POST, PUT, DELETE) geçerli bir JWT token gerektirir. Tipik akış:

**1. Yönetici kaydı oluşturun:**

```
POST /kayit
{
  "kullanici_adi": "admin",
  "sifre": "sifre123"
}
```

**2. Giriş yapıp token alın:**

```
POST /giris
{
  "kullanici_adi": "admin",
  "sifre": "sifre123"
}
```

Yanıt olarak bir `access_token` döner.

**3. Korumalı uç noktalara token ile istek atın.** İstek başlığına şunu ekleyin:

```
Authorization: Bearer <access_token>
```

Swagger arayüzünde (`/docs`) sağ üstteki **Authorize** düğmesine token'ı yapıştırmanız, sonraki tüm isteklere otomatik eklenmesini sağlar. Token varsayılan olarak 60 dakika geçerlidir.

## Testleri Çalıştırma

Testler gerçek veritabanına dokunmaz; ayrı bir test veritabanında (`okul_kayit_test_db`) izole çalışır. Önce bu veritabanını oluşturun:

```sql
CREATE DATABASE okul_kayit_test_db;
```

Tüm testleri çalıştırın:

```bash
pytest -v
```

Kod kapsamı (coverage) raporuyla birlikte çalıştırmak için:

```bash
pytest --cov=main --cov=auth --cov=database --cov=models --cov-report=term-missing
```

Test altyapısı `conftest.py` içinde tanımlıdır: her test öncesi test veritabanı sıfırlanır, veritabanı bağlantıları test veritabanına yönlendirilir ve korumalı uç noktalar için geçerli bir token üretilir.

## Veritabanı Yapısı

Uygulama ilk çalıştığında aşağıdaki tablolar otomatik olarak oluşturulur (foreign key bağımlılıkları nedeniyle bu sırayla):

- **fakulteler** — `id` (otomatik artan), `ad` (benzersiz)
- **bolumler** — `id` (otomatik artan), `ad` (benzersiz), `fakulte_id` (→ fakulteler)
- **yoneticiler** — `id` (otomatik artan), `kullanici_adi` (benzersiz), `sifre_hash`
- **ogrenciler** — `id` (elle verilir), `ad`, `soyad`, `telefon_no`, `mail`, `fakulte_id` (→ fakulteler), `bolum_id` (→ bolumler), `guncel_donem`
- **ogretmenler** — `id` (elle verilir), `ad`, `soyad`, `telefon_no`, `mail`, `fakulte_id` (→ fakulteler), `bolum_id` (→ bolumler)

Öğrenci ve öğretmen kimlikleri (`id`) kullanıcı tarafından elle atanır; fakülte ve bölüm kimlikleri veritabanı tarafından otomatik üretilir.