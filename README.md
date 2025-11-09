# Analyticity - Traffic Analysis Platform - Demo Version

**Analyticity** je platforma na analýzu dopravných dát z Waze (zápchy, upozornenia) a nehôd. Systém sa skladá z:
- **TimescaleDB databázy** s PostGIS podporou pre časové a priestorové dáta
- **Dvoch backend API** (accidents_api, analyticity-backend)
- **React frontend aplikácie** s mapovou vizualizáciou
- **pgAdmin** pre správu databázy

Celý stack sa spúšťa jedným príkazom cez **Docker Compose**.
---

## 🚀 Rýchly štart

## ⚠️ Pred prvým spustením
- Unzipnite `data.zip` (mal by vzniknúť priečinok `data/` s CSV súbormi)

### 1. Príprava prostredia

```bash
# Skopírujte a upravte konfiguračný súbor
cp .env.example .env

# Editujte .env podľa potreby (hesla, prístupy, atď.)
nano .env
```

### 2. Spustenie aplikácie

```bash
# Spustenie celého stacku
docker compose up --build
```

**Prvé spustenie trvá ~3-5 minút** (sťahovanie images, build, inicializácia databázy, nahratie dát).

### 3. Prístup k aplikácii

Po úspešnom spustení:

| Služba | URL | Prihlásenie |
|--------|-----|-------------|
| **Frontend** | http://localhost:5173 | - |
| **Accidents API (Swagger)** | http://localhost:8000/docs | - |
| **Analyticity Backend (Swagger)** | http://localhost:8010/docs | - |
| **pgAdmin** | http://localhost:8080 | Email a heslo z `.env` |

---

## ⚠️ Riešenie problémov

### Databáza sa nespustí / chyby pri inicializácii

Ak `brno-db` padá na chybe alebo sa nejak pokazila databáza:

```bash
# Zastavte všetky kontajnery
docker compose down

# Vymažte dáta databázy
rm -rf database_creation/data/db_brno

# Spustite znova
docker compose up --build
```

### Port je už obsadený

Ak máte chybu typu `port is already allocated`:

```bash
# Zmeňte porty v docker-compose.yaml, napr.:
# brno-db: "5433:5432" → "5434:5432"
# frontend: "5173:5173" → "5175:5173"
# atď.
```

### Frontend nedokáže načítať dáta

Skontrolujte, či sú v `.env` správne nastavené API URL:
```bash
VITE_API_URL=http://localhost:8000
VITE_BACKEND_API_URL=http://localhost:8010
```

---

## 🔑 Konfigurácia (.env)

Všetky premenné prostredia sú v súbore `.env`. Tu je kompletný popis:

### Externé dátové zdroje

```bash
# URL pre sťahovanie dát z Waze Partner Hub (používané loaderom)
DATA_JMK="https://www.waze.com/row-partnerhub-api/partners/.../waze-feeds/..."
DATA_ORP_MOST="https://www.waze.com/row-partnerhub-api/partners/.../waze-feeds/..."
```

### Centrálna databáza (pre budúce použitie)

```bash
# Konfigurácia centrálnej DB pre správu viacerých regiónov
POSTGRES_DB_CENTRAL=central_db
POSTGRES_USER_CENTRAL=db
POSTGRES_PASSWORD_CENTRAL=admin
```

### Brno databáza (hlavná pracovná DB)

```bash
# Názov databázy, používateľ a heslo
POSTGRES_DB_BRNO=traffic_brno
POSTGRES_USER_BRNO=analyticity_admin
POSTGRES_PASSWORD_BRNO=admin
```

### pgAdmin (webové UI pre správu databázy)

```bash
# ⚠️ POVINNÉ - bez týchto hodnôt sa pgAdmin nespustí
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
```

### Interné Docker premenné

```bash
# Hostname a port databázy VNÚTRI Docker siete
# (používajú sa v loader skriptoch a backend službách)
DB_HOST=brno-db
DB_PORT=5432
```

### Externé prístupy (pre lokálne Python skripty)

```bash
# Hostname a port pre pripojenie Z HOSTITEĽSKÉHO POČÍTAČA
# (napr. keď spúšťate Python skripty lokálne, mimo Docker)
POSTGRES_HOST_BRNO=localhost
POSTGRES_PORT_BRNO=5433
```

### Frontend API endpoints

```bash
# URL backend API pre frontend (vkladá sa do build-u frontendu)
VITE_API_URL=http://localhost:8000
VITE_BACKEND_API_URL=http://localhost:8010
```

---

## 📁 Štruktúra projektu

```
demo-app/
├── README.md                          # Tento súbor
├── .env.example                       # Šablóna konfigurácie
├── docker-compose.yaml                # Orchestrácia služieb
│
├── database_creation/                 # Databázové skripty a dáta
│   ├── README.md                      # Detailný popis databázy
│   ├── init.sql                       # Schéma Brno DB
│   ├── init_db_central.sql            # Schéma centrálnej DB
│   ├── load_*.py                      # Skripty na nahratie CSV dát
│   └── data/db_brno/                  # PostgreSQL dáta (generované)
│
├── data/                              # CSV súbory s historickými dátami
│   ├── brno_alerts.csv
│   ├── brno_jams.csv
│   └── brno_nehody.csv
│
├── accidents_api/                     # Backend API #1 (FastAPI)
│   ├── README.md                      # Detailný popis accidents_api
│   ├── bp_api/                        # Zdrojový kód
│   └── pyproject.toml                 # Poetry dependencies
│
├── Analyticity-backend/               # Backend API #2 (FastAPI)
│   ├── README.md                      # Detailný popis analyticity-backend
│   ├── AnalyticityBackend/            # Zdrojový kód
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                          # React + TypeScript frontend
│   ├── README.md                      # Detailný popis frontendu
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── ops/                               # Operačné skripty
│   └── loader_entrypoint.sh           # Entrypoint pre CSV loader
│
└── Dockerfile.*                       # Dockerfiles pre jednotlivé služby
```

---

## 📚 Detailná dokumentácia

Pre podrobné informácie o jednotlivých častiach systému:

- **[Databáza](database_creation/README.md)** - popis dátového modelu, tabuliek a indexov
- **[Accidents API](accidents_api/README.md)** - endpointy, modely, routing
- **[Analyticity Backend](Analyticity-backend/README.md)** - endpointy, helpers, SQL queries
- **[Frontend](frontend/README.md)** - komponenty, routing, state management

---

## 🐳 Prehľad služieb

| Služba | Kontajner | Port | Popis |
|--------|-----------|------|-------|
| **brno-db** | brno_db | 5433→5432 | TimescaleDB s PostGIS |
| **brno-bootstrap** | brno_bootstrap | - | Jednorazový loader CSV dát |
| **pgadmin** | pgadmin_demo | 8080→80 | Webové UI pre DB |
| **accidents_api** | accidents_api | 8000 | FastAPI pre nehody |
| **analyticity-backend** | analyticity_backend | 8010 | FastAPI pre Waze dáta |
| **frontend** | bp_frontend_dev | 5173, 5174 | React + Vite dev server |

---

## 🛠️ Príkazy pre prácu s Docker Compose

```bash
# Spustenie všetkých služieb
docker compose up

# Spustenie s rebuild (po zmenách v kóde)
docker compose up --build

# Spustenie na pozadí
docker compose up -d

# Zastavenie služieb
docker compose down

# Zastavenie + vymazanie volumes (DB dáta)
docker compose down -v

# Zobrazenie logov
docker compose logs -f

# Zobrazenie logov konkrétnej služby
docker compose logs -f brno-db
docker compose logs -f analyticity-backend

# Re-spustenie len loadera (ak chcete znova načítať CSV)
docker compose run --rm brno-bootstrap

# Reštart konkrétnej služby
docker compose restart frontend
```

---

## 🧹 Úplné vyčistenie

Ak chcete úplne odstrániť všetky kontajnery, siete, volumes a obrazy:

```bash
docker compose down -v --rmi all
rm -rf database_creation/data/db_brno
```

---

## 📝 Poznámky

- **Prvé spustenie** databázy automaticky vytvorí schému a nahrá CSV dáta
- **Frontend** beží v dev móde s hot-reload
- **Backend API** majú automaticky generovanú Swagger dokumentáciu
- **pgAdmin** si pamätá pripojenia (persistované v Docker volume)
- Pre **production** nasadenie zmeňte heslá a použite production buildy

---

## 🆘 Časté problémy

| Problém | Riešenie |
|---------|----------|
| `PGADMIN_DEFAULT_EMAIL is not set` | Doplňte `PGADMIN_EMAIL` a `PGADMIN_PASSWORD` v `.env` |
| `port 5433 already allocated` | Zmeňte port v `docker-compose.yaml` alebo ukončite aplikáciu, ktorá ho používa |
| `No module named 'connection_to_db'` | Skontrolujte, či je v `docker-compose.yaml` volume pre `connection_to_db.py` |
| DB sa nespustí po páde | Vymažte `database_creation/data/db_brno` a spustite znova |
| Frontend hlási CORS chyby | Skontrolujte `VITE_API_URL` v `.env` a CORS nastavenia v backend API |

---


