# Analyticity Backend - API Documentation

**Analyticity Backend** je FastAPI server, ktorý poskytuje pokročilé endpointy pre analýzu dopravných dát z Waze (zápchy, upozornenia) s priamym pripojením na TimescaleDB databázu. Backend je optimalizovaný pre časovo-priestorové dotazy a poskytuje agregované štatistiky.

---

## 🎯 Účel

Analyticity Backend poskytuje:
- **Časovo-priestorové analýzy** zápch a upozornení
- **Agregované štatistiky** (hodinové, denné, týždenné)
- **Filtrovanie** podľa ulíc, časového rozsahu, trás (routes)
- **Mapové vizualizácie** s farebnými úsekmi ulíc
- **Top N štatistiky** (najproblematickejšie ulice)
- **Health checks** pre monitorovanie databázy

---

## 🚀 Spustenie

### Cez Docker Compose (odporúčané)

```bash
# Z root priečinku demo-app
docker compose up analyticity-backend
```

API bude dostupné na: **http://localhost:8010**

Swagger dokumentácia: **http://localhost:8010/docs**

### Lokálne (pre vývoj)

```bash
cd Analyticity-backend

# Vytvorenie virtuálneho prostredia
python -m venv venv
source venv/bin/activate  # Linux/Mac
# alebo
venv\Scripts\activate  # Windows

# Inštalácia závislostí
pip install -r requirements.txt

# Nastavenie environment variables
export DB_BRNO_HOST=localhost
export DB_BRNO_PORT=5433
export DB_BRNO_USER=analyticity_admin
export DB_BRNO_PASSWORD=admin
export DB_BRNO_NAME=traffic_brno

# Spustenie servera
uvicorn AnalyticityBackend.main:app --reload --host 0.0.0.0 --port 8010
```

---

## 📁 Štruktúra projektu

```
Analyticity-backend/
├── requirements.txt              # Python dependencies
├── Dockerfile
├── README.md                     # Tento súbor
└── AnalyticityBackend/           # Zdrojový kód
    ├── main.py                   # FastAPI aplikácia
    ├── db_config.py              # Databázové pripojenia
    ├── logging_config.py         # Konfigurácia logovania
    ├── constants/
    │   ├── queries.py            # SQL dotazy (QUERY_*)
    │   └── universal_constants.py # Konštanty
    ├── datasets/                 # GeoJSON súbory
    │   ├── nehody.geojson
    │   ├── processed_alerts.json
    │   └── streets_exploded.geojson
    ├── helpers/                  # Business logika
    │   ├── homepage_helpers.py   # Štatistiky pre homepage
    │   ├── jams_helpers.py       # Priestorové počítanie zápch
    │   ├── logging_helpers.py    # Logovanie utilities
    │   └── universal_helpers.py  # Spoločné funkcie
    ├── middleware/
    │   └── request_logging.py    # Middleware pre logy
    ├── models/                   # Pydantic modely
    │   ├── request_models.py     # Request schemas
    │   └── response_models.py    # Response schemas
    ├── routers/                  # API endpointy
    │   ├── alerts_endpoints.py   # Waze alerts
    │   ├── dashboard_endpoints.py # Dashboard stats
    │   ├── health_endpoints.py   # Health checks
    │   ├── homepage_endpoints.py # Homepage stats
    │   ├── jams_endpoints.py     # Jams + vizualizácie
    │   └── plot_endpoints.py     # Grafy
    └── utils/                    # Utility funkcie (budúce použitie)
```

---

## 🔌 API Endpointy

### 📍 **Base URL:** `http://localhost:8010`

---

## 🏥 Health & Status

### `GET /health/db`

Kontrola stavu databázového pripojenia.

**Response:**
```json
{
  "brno": {
    "status": "ok",
    "latency_ms": 15,
    "tables": {
      "jams": {
        "first_record": "2024-01-01T00:00:00Z",
        "last_record": "2024-12-31T23:59:00Z"
      },
      "alerts": { ... },
      "accidents": { ... }
    }
  }
}
```

**Status codes:**
- `200` - DB funguje
- `503` - DB nedostupná

---

## 📊 Homepage Statistics

### `POST /{name}/homepage/sum_statistics`

Vráti agregované štatistiky pre homepage (časová os s počtami jams/alerts).

**Path parameter:**
- `name` (str) - Názov DB (napr. `brno`)

**Request body:**
```json
{
  "from_date": "2024-06-01",
  "to_date": "2024-06-30",
  "streets": ["Hlinky", "Kotlářská"],  // optional
  "route": [[49.2, 16.6], [49.21, 16.61]]  // optional
}
```

**Response:**
```json
{
  "jams": [12, 15, 18, 20, 22],
  "alerts": [5, 8, 6, 9, 7],
  "pubMillis": [1717200000000, 1717203600000, ...],
  "speedKMH": [35.5, 32.1, 28.9, ...],
  "delay": [0.5, 1.2, 2.3, ...],
  "level": [1.2, 1.5, 2.1, ...],
  "length": [0.15, 0.23, 0.31, ...]
}
```

**Popis polí:**
- `jams` - Počet zápch v každej hodine
- `alerts` - Počet upozornení v každej hodine
- `pubMillis` - Unix timestamps (ms) pre os X (zaokrúhlené na hodiny)
- `speedKMH` - Priemerná rýchlosť (km/h)
- `delay` - Priemerné zdržanie (minúty)
- `level` - Priemerná úroveň zápchy (0-5)
- `length` - Priemerná dĺžka zápchy (km)

---

### `POST /{name}/homepage/hourly_stats`

Hodinové štatistiky v novom formáte (zjednodušený response).

**Response:**
```json
{
  "hours": ["2024-06-01T00:00:00Z", "2024-06-01T01:00:00Z", ...],
  "jams": [12, 15, 18],
  "alerts": [5, 8, 6],
  "avg_speed": [35.5, 32.1, 28.9],
  "avg_delay": [0.5, 1.2, 2.3]
}
```

---

### `POST /{name}/homepage/total_statistics`

Celkové štatistiky za zvolené obdobie (jedno sumarizované číslo).

**Response:**
```json
{
  "data_jams": 450,
  "data_alerts": 180,
  "speedKMH": 32.5,
  "delay": 1.8,
  "level": 2.1,
  "length": 0.25
}
```

---

## 🗺️ Jams Visualization

### `POST /{name}/all_delays/`

**Hlavný endpoint pre vizualizáciu zápch na mape.** Vráti úseky ulíc s farbou podľa počtu zápch.

**Request body:**
```json
{
  "from_date": "2024-06-01",
  "to_date": "2024-06-30",
  "streets": ["Hlinky", "Kotlářská"]  // optional filter
}
```

**Response:**
```json
[
  {
    "street_name": "Hlinky",
    "path": [[49.2015, 16.6081], [49.2025, 16.6091]],
    "color": "red"
  },
  {
    "street_name": "Kotlářská",
    "path": [[49.1951, 16.6081], [49.1961, 16.6091]],
    "color": "orange"
  }
]
```

**Farebné schéma:**
- 🟢 **green** - Menej ako 7 zápch
- 🟠 **orange** - 7 až 21 zápch
- 🔴 **red** - Viac ako 21 zápch

**Poznámka:** Farba sa určuje podľa **názvu ulice** - jams sa priradujú len úsekom s rovnakým názvom.

---

## 📈 Dashboard Statistics

### `POST /{name}/dashboard/plot_streets`

Top N ulíc s najviac jams/alerts.

**Request body:**
```json
{
  "from_date": "2024-06-01",
  "to_date": "2024-06-30",
  "streets": [],  // optional filter
  "limit": 10
}
```

**Response:**
```json
{
  "streets_jams": ["Hlinky", "Kotlářská", "Purkyňova"],
  "values_jams": [45, 38, 32],
  "streets_alerts": ["Hlinky", "Žerotínovo nám.", "Hlavní nádraží"],
  "values_alerts": [28, 24, 19]
}
```

---

### `POST /{name}/dashboard/alerts_types`

Distribúcia alertov podľa typu a subtypu.

**Response:**
```json
[
  {
    "type": "ACCIDENT",
    "subtype": "ACCIDENT_MINOR",
    "count": 45
  },
  {
    "type": "HAZARD",
    "subtype": "HAZARD_ON_ROAD",
    "count": 32
  }
]
```

---

## 🚨 Alerts Endpoints

### `POST /{name}/alerts/`

Zoznam Waze alerts s filtrami.

**Request body:**
```json
{
  "from_date": "2024-06-01",
  "to_date": "2024-06-30",
  "streets": ["Hlinky"],  // optional
  "route": [[49.2, 16.6], [49.21, 16.61]]  // optional
}
```

**Response:**
```json
[
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "street": "Hlinky",
    "type": "ACCIDENT",
    "subtype": "ACCIDENT_MINOR",
    "pubMillis": 1717200000000,
    "longitude": 16.6081,
    "latitude": 49.2015
  }
]
```

---

## 🔧 Konfigurácia

### Environment Variables

Backend očakáva tieto premenné (nastavené v Docker Compose):

```bash
DB_BRNO_HOST=brno-db          # Hostname databázy
DB_BRNO_PORT=5432             # Port (internal)
DB_BRNO_USER=analyticity_admin
DB_BRNO_PASSWORD=admin
DB_BRNO_NAME=traffic_brno
```

### Databázové pripojenia (`db_config.py`)

```python
DATABASES = {
    "brno": {
        "host": os.getenv("DB_BRNO_HOST", "localhost"),
        "port": int(os.getenv("DB_BRNO_PORT", 5433)),
        "user": os.getenv("DB_BRNO_USER", "analyticity_admin"),
        "password": os.getenv("DB_BRNO_PASSWORD", "admin"),
        "database": os.getenv("DB_BRNO_NAME", "traffic_brno"),
    }
}

def get_db_connection(db_name: str) -> psycopg2.extensions.connection:
    config = DATABASES.get(db_name)
    return psycopg2.connect(**config)
```

---

## 📜 SQL Queries (`constants/queries.py`)

Backend používa predpripravené SQL dotazy optimalizované pre TimescaleDB.

### Príklad: `QUERY_SUM_STATISTICS`

```sql
WITH hours AS (
    SELECT generate_series(
        date_trunc('hour', %s::timestamptz),
        date_trunc('hour', %s::timestamptz) - interval '1 hour',
        interval '1 hour'
    ) AS utc_time
),
jams_agg AS (
    SELECT
        date_trunc('hour', published_at AT TIME ZONE 'UTC') AS utc_time,
        COUNT(*) AS data_jams,
        AVG(speed_kmh_avg)::FLOAT AS speedKMH,
        AVG(delay_avg)::FLOAT AS delay,
        AVG(jam_level_avg)::FLOAT AS level,
        AVG(jam_length_avg)::FLOAT AS length
    FROM jams
    WHERE published_at >= %s AND published_at < %s
    GROUP BY utc_time
),
alerts_agg AS (
    SELECT
        date_trunc('hour', published_at AT TIME ZONE 'UTC') AS utc_time,
        COUNT(*) AS data_alerts
    FROM alerts
    WHERE published_at >= %s AND published_at < %s
    GROUP BY utc_time
)
SELECT
    j.data_jams,
    j.speedKMH,
    j.delay,
    j.level,
    j.length,
    h.utc_time,
    COALESCE(a.data_alerts, 0) AS data_alerts
FROM hours h
LEFT JOIN jams_agg j USING (utc_time)
LEFT JOIN alerts_agg a USING (utc_time)
ORDER BY h.utc_time;
```

**Kľúčové vlastnosti:**
- ✅ Generuje kompletný časový axis (aj hodiny bez dát)
- ✅ Používa `AVG(speed_kmh_avg)` (opravené názvy stĺpcov)
- ✅ LEFT JOIN zabezpečí, že sa vrátia aj hodiny bez jams

---

## 🧮 Helpers - Business Logika

### `homepage_helpers.py`

**Funkcie:**

#### `transform_sum_statistics_to_legacy_format()`

Transformuje databázové výsledky na formát očakávaný frontnendom.

```python
def transform_sum_statistics_to_legacy_format(
    rows: Iterable[dict],
    from_date: datetime,
    to_date: datetime,
) -> Tuple[List[int], List[int], List[int], List[float], ...]
```

**Logika:**
- Vytvorí hodinový axis pre celý rozsah `[from_date, to_date)`
- Vynechá budúce hodiny (ak `to_date` je v budúcnosti)
- Pre hodiny **bez zápch** vráti default hodnoty:
  - `speedKMH = 35.0` (default rýchlosť)
  - `delay = 0.0`
  - `level = 0.0`
  - `length = 0.0`

#### `fetch_sum_statistics()`

Vykoná SQL dotaz a vráti surové výsledky.

```python
def fetch_sum_statistics(cursor, from_date, to_date):
    cursor.execute(QUERY_SUM_STATISTICS, (from_date, to_date, ...))
    return cursor.fetchall()
```

---

### `jams_helpers.py`

**Funkcie:**

#### `_count_with_strtree_tolerant()`

Priestorové počítanie zápch pre každý úsek ulice pomocou **STRtree** (priestorový index).

```python
def _count_with_strtree_tolerant(
    street_gdf: gpd.GeoDataFrame,
    jams_gdf: gpd.GeoDataFrame,
    logger=None,
    tol_m: float = 15
) -> gpd.GeoDataFrame
```

**Algoritmus:**
1. Konvertuje geometrie do metrického CRS (EPSG:3857)
2. Vytvorí STRtree index pre rýchle vyhľadávanie
3. Pre každý úsek ulice:
   - Vytvorí buffer ±15 metrov
   - Nájde kandidátov pomocou STRtree
   - **Skontroluje zhodu názvov ulíc** (case-insensitive)
   - Spočíta len tie jams, ktoré:
     - Priestorovo sa pretínajú s bufferom
     - Majú rovnaký názov ulice

**Výstup:** GeoDataFrame s pridaným stĺpcom `count`

#### `_assign_color()`

Priradí farbu podľa počtu zápch.

```python
def _assign_color(count: int, num_days: int = 7) -> str:
    if count < 1 * num_days:
        return "green"
    if count <= 3 * num_days:
        return "orange"
    return "red"
```

#### `_serialize_street_paths()`

Konvertuje GeoDataFrame na JSON response pre frontend.

```python
def _serialize_street_paths(df_streets: gpd.GeoDataFrame) -> list:
    return [
        {
            "street_name": row["nazev"],
            "path": [[lat, lon] for lon, lat in coords],  # swap to [lat, lon]
            "color": row["color"]
        }
        for _, row in df_streets.iterrows()
    ]
```

---

## 🌐 CORS Konfigurácia

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Pre production pridajte produkčnú doménu do `allow_origins`.

---

## 📝 Logovanie (`logging_config.py`)

Backend používa **štruktúrované JSON logovanie**.

**Konfigurácia:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

**Príklad logu:**
```
2024-06-15T10:30:45 | app.jams | INFO | [jams] DB query executed in 125 ms; rows=1234
2024-06-15T10:30:46 | app.jams | INFO | [jams] Counting: 567 streets, 1234 jams, tolerance=15m
2024-06-15T10:30:47 | app.jams | INFO | [jams] Counting done: 89 total matches, 42/567 streets with jams
```

**Request logging middleware:**
- Každý request dostane unikátny `request_id`
- Loguje sa path, method, duration, status code

---

## 🧪 Testovanie

### Swagger UI

Otvorte http://localhost:8010/docs

### cURL príklady

```bash
# Health check
curl http://localhost:8010/health/db

# Homepage stats
curl -X POST http://localhost:8010/brno/homepage/sum_statistics \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-06-01",
    "to_date": "2024-06-30"
  }'

# All delays (map visualization)
curl -X POST http://localhost:8010/brno/all_delays/ \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-06-01",
    "to_date": "2024-06-30",
    "streets": ["Hlinky", "Kotlářská"]
  }'
```

### Python príklad

```python
import requests

# Získaj štatistiky
response = requests.post(
    "http://localhost:8010/brno/homepage/total_statistics",
    json={
        "from_date": "2024-06-01",
        "to_date": "2024-06-30"
    }
)

stats = response.json()
print(f"Celkom zápch: {stats['data_jams']}")
print(f"Priemerná rýchlosť: {stats['speedKMH']} km/h")
```

---

## 🐳 Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Inštalácia systémových závislostí pre PostGIS/GEOS
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopírovanie requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírovanie kódu
COPY AnalyticityBackend ./AnalyticityBackend

EXPOSE 8010

CMD ["uvicorn", "AnalyticityBackend.main:app", "--host", "0.0.0.0", "--port", "8010"]
```

---

## 🔍 Debugging & Troubleshooting

### Problém: Všetky ulice sú zelené (žiadne zápchy)

**Možné príčiny:**
1. Názvy ulíc v jams DB sa nezhodujú s názvami v GeoJSON
2. Priestorový buffer je príliš malý (default 15m)
3. Zápchy sú mimo časového rozsahu

**Riešenie:**
Skontrolujte logy:
```
[jams] Sample jam streets from DB: ['Hlinky', 'Kotlářská', ...]
[jams] Sample street names: ['hlinky', 'kotlářská', ...]
[jams] Sample matched pairs: [('Hlinky', 'Hlinky'), ...]
[jams] Counting done: 89 total matches, 42/567 streets with jams
```

### Problém: Pomalé dotazy

**Riešenie:**
1. Skontrolujte priestorové indexy:
```sql
SELECT indexname FROM pg_indexes WHERE tablename = 'jams';
```

2. Spustite VACUUM ANALYZE:
```sql
VACUUM ANALYZE jams;
VACUUM ANALYZE alerts;
```

3. Zúžte časový rozsah dotazu

---

## 📊 Performance

### Optimalizácie

1. **TimescaleDB chunks** - Dáta automaticky particionované po týždňoch
2. **GIST indexy** - Priestorové dotazy sú rýchle
3. **STRtree** - In-memory priestorový index (GeoPandas)
4. **Prepared statements** - SQL dotazy sú reusable

### Benchmarky (orientačné)

| Endpoint | Dáta | Čas |
|----------|------|-----|
| `sum_statistics` | 30 dní | ~150ms |
| `all_delays` | 30 dní, 500 ulíc | ~2s |
| `total_statistics` | 30 dní | ~50ms |
| `alerts_types` | 30 dní | ~80ms |

---

## 🔗 Súvisiace dokumenty

- [Hlavné README](../README.md)
- [Database README](../database_creation/README.md)
- [Accidents API README](../accidents_api/README.md)
- [Frontend README](../frontend/README.md)

---

## 📦 Dependencies (requirements.txt)

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
psycopg2-binary==2.9.9
geopandas==0.14.1
shapely==2.0.2
pandas==2.1.4
numpy==1.26.2
pyproj==3.6.1
python-multipart==0.0.6
```

---