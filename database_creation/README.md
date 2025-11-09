# Databázová vrstva - Analyticity

Tento priečinok obsahuje SQL schémy, inicializačné skripty a Python loadery pre databázovú vrstvu platformy Analyticity.

---

## 📊 Prehľad databáz

Systém používa **dva typy databáz**:

1. **Brno Database** (`traffic_brno`) - Hlavná pracovná databáza
   - Ukladá Waze dáta (jams, alerts) a historické nehody pre Brno
   - Používa TimescaleDB pre časové série
   - Schéma: `init.sql`

2. **Central Database** (`central_db`) - Správcovská databáza (pre budúce použitie)
   - Registry viacerých regionálnych databáz
   - Mapovanie coverage areas
   - Schéma: `init_db_central.sql`

---

## 🗂️ Súbory v tomto priečinku

```
database_creation/
├── README.md                        # Tento súbor
├── init.sql                         # Schéma Brno databázy
├── init_db_central.sql              # Schéma centrálnej databázy
├── load_alerts_from_csv_to_db.py   # Loader pre Waze alerts
├── load_jams_from_csv_to_db.py     # Loader pre Waze jams
├── load_nehody_from_csv_to_db.py   # Loader pre nehody
├── update_coverage_area.py          # Aktualizácia coverage areas
└── data/
    └── db_brno/                     # PostgreSQL dátový priečinok (vytvorený automaticky)
```

---

## 🏗️ Dátový model - Brno Database (`init.sql`)

### 1. Rozšírenia (Extensions)

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;  -- Časové série
CREATE EXTENSION IF NOT EXISTS postgis;       -- Priestorové dáta
```

### 2. Tabuľka `jams` - Dopravné zápchy z Waze

**Účel:** Ukladá informácie o dopravných zápchach v reálnom čase.

**Štruktúra:**

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `id` | BIGINT | ID zápchy z Waze |
| `uuid` | INTEGER | Unikátny identifikátor zápchy |
| `country` | TEXT | Krajina (napr. 'CZ') |
| `city` | TEXT | Mesto (napr. 'Brno') |
| `turn_type` | TEXT | Typ križovatky/odbočky |
| `street` | TEXT | **Názov ulice** |
| `end_node` | TEXT | ID koncového uzla |
| `start_node` | TEXT | ID počiatočného uzla |
| `road_type` | INTEGER | Typ cesty (1-6) |
| `blocking_alert_uuid` | UUID | ID blokujúceho alertu |
| **Agregované metriky (počas update_count aktualizácií):** | | |
| `jam_level_max` | INTEGER | Maximálna úroveň zápchy (0-5) |
| `jam_level_avg` | FLOAT | Priemerná úroveň zápchy |
| `speed_kmh_min` | INTEGER | Minimálna rýchlosť (km/h) |
| `speed_kmh_avg` | FLOAT | Priemerná rýchlosť (km/h) |
| `jam_length_max` | INTEGER | Maximálna dĺžka zápchy (metre) |
| `jam_length_avg` | FLOAT | Priemerná dĺžka zápchy (metre) |
| `speed_max` | FLOAT | Maximálna rýchlosť (mph - pôvodné jednotky) |
| `speed_avg` | FLOAT | Priemerná rýchlosť (mph) |
| `delay_max` | INTEGER | Maximálne zdržanie (sekundy) |
| `delay_avg` | FLOAT | Priemerné zdržanie (sekundy) |
| `update_count` | INTEGER | Počet aktualizácií tejto zápchy |
| **Geometria:** | | |
| `jam_line` | GEOGRAPHY(LINESTRING, 4326) | Geometria zápchy (WGS84) |
| **Časové značky:** | | |
| `published_at` | TIMESTAMPTZ | Čas prvého publikovania |
| `last_updated` | TIMESTAMPTZ | Čas poslednej aktualizácie |
| `active` | BOOLEAN | Je zápcha aktívna? |

**Primárny klúč:** `(uuid, published_at)` - umožňuje sledovať vývoj jednej zápchy v čase

**Hypertable:** Konvertované na TimescaleDB hypertable podľa `published_at` pre efektívne časové dotazy

**Priestorový index:**
```sql
CREATE INDEX idx_jams_jam_line ON jams USING GIST(jam_line);
```

---

### 3. Tabuľka `alerts` - Waze upozornenia

**Účel:** Ukladá používateľské upozornenia z Waze (nehody, nebezpečenstvá, policajné kontroly).

**Štruktúra:**

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `uuid` | UUID | Unikátny identifikátor alertu |
| `country` | TEXT | Krajina |
| `city` | TEXT | Mesto |
| `type` | TEXT | Typ alertu (ACCIDENT, HAZARD, JAM, atď.) |
| `subtype` | TEXT | Podtyp (HAZARD_ON_ROAD, ACCIDENT_MINOR, atď.) |
| `street` | TEXT | Názov ulice |
| `report_rating` | INTEGER | Hodnotenie správy (0-5) |
| `confidence` | INTEGER | Spoľahlivosť (0-10) |
| `reliability` | INTEGER | Dôveryhodnosť zdroja (0-10) |
| `road_type` | INTEGER | Typ cesty |
| `magvar` | INTEGER | Magnetická variácia |
| `report_by_municipality_user` | BOOLEAN | Nahlásené mestom? |
| `report_description` | TEXT | Popis upozornenia |
| **Geometria:** | | |
| `location` | GEOGRAPHY(POINT, 4326) | GPS súradnice (WGS84) |
| **Časové značky:** | | |
| `published_at` | TIMESTAMPTZ | Čas publikovania |
| `last_updated` | TIMESTAMPTZ | Čas poslednej aktualizácie |
| `active` | BOOLEAN | Je alert aktívny? |

**Primárny klúč:** `(uuid, published_at)`

**Hypertable:** Konvertované na TimescaleDB hypertable podľa `published_at`

**Priestorový index:**
```sql
CREATE INDEX idx_alerts_location ON alerts USING GIST(location);
```

---

### 4. Tabuľka `nehody` - Historické dopravné nehody

**Účel:** Ukladá štatistické údaje o dopravných nehodách z Polície ČR.

**Štruktúra:**

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `p1` | BIGINT | Primárny identifikátor nehody |
| `p2a` | DATE | Dátum nehody (**partition key**) |
| `p2b` | INTEGER | Čas nehody (HHMM) |
| `p6` | INTEGER | Druh nehody (zrážka, havária, atď.) |
| `p7` | INTEGER | Druh zrážky |
| `p10` | INTEGER | Charakter nehody |
| `p13a`, `p13b`, `p13c` | INTEGER | Príčiny nehody |
| `p34` | INTEGER | Počet mŕtvych |
| `p35` | INTEGER | Počet ťažko zranených |
| `p36` | TEXT | Okres |
| `p37` | TEXT | Obec |
| `p47` | TEXT | Druh miesta |
| `p48a` | INTEGER | Druh povrchu |
| `p49` | INTEGER | Stav povrchu |
| ... | | (ďalších ~30 stĺpcov s detailami) |
| **Geometria:** | | |
| `x`, `y` | FLOAT | Súradnice v S-JTSK (EPSG:5514) |
| `geom` | GEOMETRY(POINT, 5514) | Geometria v S-JTSK |
| `geog` | GEOGRAPHY(POINT, 4326) | Geometria v WGS84 (pre mapovanie) |

**Primárny klúč:** `p1`

**Hypertable:** Konvertované na TimescaleDB hypertable podľa `p2a` (dátum)

**Priestorové indexy:**
```sql
CREATE INDEX idx_accidents_geom ON nehody USING GIST(geom);
CREATE INDEX idx_accidents_geog ON nehody USING GIST(geog);
```

**Poznámka:** Kódy v stĺpcoch `p*` zodpovedajú číselníkom Polície ČR.

---

### 5. Tabuľka `segments` - Segmenty zápch

**Účel:** Rozdelenie zápch na menšie úseky/segmenty.

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `id` | SERIAL | Primárny klúč |
| `jam_id` | BIGINT | Referencia na jam.id |
| `from_node` | BIGINT | ID počiatočného uzla |
| `to_node` | BIGINT | ID koncového uzla |
| `segment_id` | BIGINT | ID segmentu |
| `is_forward` | BOOLEAN | Smer segmentu |

---

### 6. Tabuľka `sum_statistics` - Agregované štatistiky

**Účel:** Predpočítané hodinové štatistiky (pre rýchle dashboardy).

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `stat_time` | TIMESTAMPTZ | Čas (zaokrúhlený na hodinu) |
| `total_active_jams` | INTEGER | Počet aktívnych zápch |
| `total_active_alerts` | INTEGER | Počet aktívnych alertov |
| `avg_speed_kmh` | FLOAT | Priemerná rýchlosť (km/h) |
| `avg_jam_length` | FLOAT | Priemerná dĺžka zápchy (m) |
| `avg_delay` | FLOAT | Priemerné zdržanie (s) |
| `avg_jam_level` | FLOAT | Priemerná úroveň zápchy |

**Primárny klúč:** `stat_time`

---

## 🌐 Dátový model - Central Database (`init_db_central.sql`)

### Tabuľka `data_sources` - Register databáz

**Účel:** Centrálny register všetkých regionálnych databáz v systéme.

| Stĺpec | Typ | Popis |
|--------|-----|-------|
| `id` | SERIAL | Primárny klúč |
| `name` | TEXT | Unikátny názov DB (napr. 'brno', 'jmk') |
| `db_host` | TEXT | Docker hostname (napr. 'db_brno') |
| `db_port_external` | INTEGER | Externý port (napr. 5433) |
| `db_port_internal` | INTEGER | Interný port (default 5432) |
| `db_name` | TEXT | Názov databázy |
| `db_user` | TEXT | Používateľ |
| `db_password` | TEXT | Heslo |
| `description` | TEXT | Popis |
| `active` | BOOLEAN | Je DB aktívna? |
| `coverage_area` | GEOMETRY(POLYGON, 4326) | Geografická oblasť pokrytia |
| `created_at` | TIMESTAMPTZ | Čas vytvorenia záznamu |
| `updated_at` | TIMESTAMPTZ | Čas aktualizácie |

**Primárny klúč:** `id`

**Unikátny constraint:** `name`

**Príklad coverage_area:**
```sql
-- Brno (približný bounding box)
ST_GeomFromText('POLYGON((16.5 49.1, 16.7 49.1, 16.7 49.3, 16.5 49.3, 16.5 49.1))', 4326)
```

---

## 📥 Načítanie dát (CSV Loadery)

### `load_jams_from_csv_to_db.py`

Načíta historické dáta o zápchach z `../data/brno_jams.csv`.

**Funkcie:**
- `insert_jams_from_csv()` - Kompletné načítanie s agregáciami
- `insert_jams_simplified()` - Zjednodušené načítanie (používa sa v produkcii)
- `calculate_update_count()` - Vypočíta počet aktualizácií na základe `last_updated - published_at`

**CSV stĺpce:**
```
id, uuid, country, city, turn_type, street, end_node, start_node, road_type,
blocking_alert_uuid, jam_level_max, jam_level_avg, speed_kmh_min, speed_kmh_avg,
jam_length_max, jam_length_avg, speed_max, speed_avg, delay_max, delay_avg,
update_count, jam_line (WKT), published_at, last_updated, active
```

**ON CONFLICT:** Ignoruje duplicitné záznamy s rovnakým `(uuid, published_at)`

---

### `load_alerts_from_csv_to_db.py`

Načíta historické upozornenia z `../data/brno_alerts.csv`.

**CSV stĺpce:**
```
uuid, country, city, type, subtype, street, report_rating, confidence,
reliability, road_type, magvar, report_by_municipality_user,
report_description, location (WKT POINT), published_at, last_updated, active
```

---

### `load_nehody_from_csv_to_db.py`

Načíta historické nehody z `../data/brno_nehody.csv`.

**CSV stĺpce:**
```
p1, p36, p37, p2a, p2b, p6, ..., x, y, geom (WKT), geog (WKT)
```

**Poznámka:** Geometrie sú v dvoch CRS:
- `geom` - S-JTSK (EPSG:5514) pre česká dáta
- `geog` - WGS84 (EPSG:4326) pre webové mapy

---

## 🔄 Proces inicializácie databázy

1. **Docker Compose spustí kontajner `brno-db`**
   ```bash
   docker compose up brno-db
   ```

2. **PostgreSQL automaticky spustí `/docker-entrypoint-initdb.d/00_init.sql`**
   - Vytvorí extensions (timescaledb, postgis)
   - Vytvorí schému tabuliek
   - Vytvorí hypertables
   - Vytvorí priestorové indexy

3. **Healthcheck počká, kým je DB pripravená**
   ```bash
   pg_isready -U analyticity_admin -d traffic_brno
   ```

4. **Spustí sa `brno-bootstrap` kontajner** (loader)
   ```bash
   docker compose up brno-bootstrap
   ```

5. **Loader vykoná tri Python skripty postupne:**
   ```bash
   python load_alerts_from_csv_to_db.py
   python load_jams_from_csv_to_db.py
   python load_nehody_from_csv_to_db.py
   ```

6. **Loader kontajner sa vypne** (exit code 0)

---

## 🗑️ Reset databázy

Ak potrebujete úplne vymazať a znova vytvoriť databázu:

```bash
# Zastavte všetky kontajnery
docker compose down

# Vymažte PostgreSQL dáta
rm -rf data/db_brno

# Spustite znova (automaticky sa vytvorí nová DB)
docker compose up --build
```

---

## 🔍 Priame pripojenie k databáze

### Cez psql (z hosťovského počítača)

```bash
psql -h localhost -p 5433 -U analyticity_admin -d traffic_brno
```

### Cez pgAdmin

1. Otvorte http://localhost:8080
2. Prihláste sa (email a heslo z `.env`)
3. Pridajte nový server:
   - **Name:** Brno DB
   - **Host:** `brno-db` (v Docker sieti) alebo `localhost` (z hostu)
   - **Port:** `5432` (v Docker) alebo `5433` (z hostu)
   - **Database:** `traffic_brno`
   - **Username:** `analyticity_admin`
   - **Password:** `admin`

---

## 📊 Príklady SQL dotazov

### Počet aktívnych zápch v posledných 24 hodinách

```sql
SELECT COUNT(*) 
FROM jams 
WHERE published_at > NOW() - INTERVAL '24 hours' 
  AND active = TRUE;
```

### Top 10 ulíc s najviac zápchami

```sql
SELECT street, COUNT(*) as jam_count
FROM jams
WHERE published_at > NOW() - INTERVAL '7 days'
  AND street IS NOT NULL
GROUP BY street
ORDER BY jam_count DESC
LIMIT 10;
```

### Priemerná rýchlosť v Brne za poslednú hodinu

```sql
SELECT AVG(speed_kmh_avg) as avg_speed
FROM jams
WHERE published_at > NOW() - INTERVAL '1 hour'
  AND city = 'Brno';
```

### Nehody v určenom oblasti (bounding box)

```sql
SELECT p1, p2a, p36, p37, ST_AsText(geog)
FROM nehody
WHERE ST_Intersects(
  geog,
  ST_MakeEnvelope(16.5, 49.1, 16.7, 49.3, 4326)
)
LIMIT 100;
```

### Časová distribúcia alertov (po hodinách)

```sql
SELECT 
  date_trunc('hour', published_at) as hour,
  COUNT(*) as alert_count
FROM alerts
WHERE published_at > NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour DESC;
```

---

## 🛠️ Údržba a optimalizácia

### Vacuum a analyze

```sql
VACUUM ANALYZE jams;
VACUUM ANALYZE alerts;
VACUUM ANALYZE nehody;
```

### Aktualizácia štatistík

```sql
ANALYZE jams;
ANALYZE alerts;
ANALYZE nehody;
```

### Kontrola veľkosti tabuliek

```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 📝 Poznámky

- **TimescaleDB hypertables** automaticky particionujú dáta podľa času pre rýchlejšie dotazy
- **PostGIS indexy** (GIST) výrazne zrýchľujú priestorové dotazy
- **WGS84 (EPSG:4326)** sa používa pre webové mapy (Leaflet, OpenLayers)
- **S-JTSK (EPSG:5514)** je oficiálny súradnicový systém ČR (používa sa v nehody.geom)
- Pre production nasadenie **zmeňte default heslá** v `.env`
- Databáza podporuje **časové dotazy** (time_bucket) a **priestorové dotazy** (ST_DWithin, ST_Intersects)

---

## 🔗 Súvisiace dokumenty

- [Hlavné README](../README.md)
- [Accidents API README](../accidents_api/README.md)
- [Analyticity Backend README](../Analyticity-backend/README.md)
- [Frontend README](../frontend/README.md)

