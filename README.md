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
|--------|------|------|
| POST | `/auth/register` | Registracija novog korisnika |
| POST | `/auth/login` | Prijava – vraća JWT `access_token` |
| GET | `/auth/me` | Vraća trenutnog korisnika (zahtijeva Bearer token) |

## Postavljanje admin korisnika

Nakon pokretanja baze i migracija, promoviraj korisnika u admina:

```sql
UPDATE users SET is_admin = true WHERE email = 'rokomaras@icloud.com';
```

## Varijable okoline (.env)

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/rivo
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```
