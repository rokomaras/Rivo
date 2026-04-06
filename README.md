# Rivo

Monorepo projekt:
- `api/` — FastAPI backend
- `web/` — Vue SPA frontend

## Lokalno pokretanje baze (PostgreSQL)
```bash
cp .env.example .env
docker compose up -d db
docker compose ps
```

## Pokretanje API servera

```bash
cd api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Auth endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Registracija novog korisnika |
| POST | `/auth/login` | Prijava – vraća JWT `access_token` + HttpOnly `refresh_token` kolačić |
| POST | `/auth/refresh` | Osvježi access token koristeći `refresh_token` kolačić (rotacija) |
| POST | `/auth/logout` | Odjava – briše `refresh_token` kolačić |
| GET  | `/auth/me` | Vraća trenutnog korisnika (zahtijeva Bearer token) |

### Access token

Koristite `Authorization: Bearer <access_token>` zaglavlje za zaštićene rute.

## Products / Categories endpoints

| Method | Path | Prava |
|--------|------|-------|
| GET | `/products/` | svi |
| GET | `/products/{id}` | svi |
| POST | `/products/` | samo admin |
| PUT | `/products/{id}` | samo admin |
| DELETE | `/products/{id}` | samo admin |
| GET | `/categories/` | svi |
| GET | `/categories/{id}` | svi |
| POST | `/categories/` | samo admin |
| PUT | `/categories/{id}` | samo admin |
| DELETE | `/categories/{id}` | samo admin |

## Orders endpoints

| Method | Path | Prava | Opis |
|--------|------|-------|------|
| POST | `/orders/` | customer, admin | Kreiraj draft narudžbu |
| GET  | `/orders/` | customer (vlastite), admin (sve) | Popis narudžbi (pagination: `limit`, `offset`; filter: `status`) |
| GET  | `/orders/{id}` | vlasnik, admin | Dohvati narudžbu |
| POST | `/orders/{id}/items` | vlasnik, admin | Dodaj stavku (draft) |
| PATCH | `/orders/{id}/items/{item_id}` | vlasnik, admin | Ažuriraj količinu (draft) |
| DELETE | `/orders/{id}/items/{item_id}` | vlasnik, admin | Ukloni stavku (draft) – 204 |
| POST | `/orders/{id}/checkout` | vlasnik, admin | Zaključi narudžbu (draft → submitted) |

> **Napomena:** Nakon checkoutа, izmjene stavki vraćaju 400 (`order_locked`). Duplikat istog proizvoda u narudžbi vraća 409 (`duplicate_item`).

## Postavljanje admin korisnika

Nakon pokretanja baze i migracija, promoviraj korisnika u admina:

```sql
UPDATE users SET is_admin = true, role = 'admin' WHERE email = 'rokomaras@icloud.com';
```

## Pokretanje testova

```bash
cd api
DATABASE_URL="sqlite://" python -m pytest tests/ -v
```

## Varijable okoline (.env)

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/rivo
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_SECRET=your-refresh-secret-here
JWT_REFRESH_EXPIRE_DAYS=7
JWT_ISSUER=rivo-api
ENV=dev
```

