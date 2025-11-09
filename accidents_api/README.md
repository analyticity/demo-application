# Accidents API - Backend Documentation

**Accidents API** je FastAPI backend, ktorý spravuje a poskytuje dáta o dopravných nehodách a Waze upozorneniach. API je určené pre vizualizáciu a analýzu dopravných incidentov v Brne.

---

## 🎯 Účel

Accidents API poskytuje:
- **RESTful endpointy** pre dopravné nehody (z databázy Polície ČR)
- **Waze reports** (alerts a jams) načítané z JSON súborov
- **Matchované dáta** - prepojenie nehôd s Waze upozorneniami v priestore a čase
- **Štatistické endpointy** pre grafy a vizualizácie

---

## 🚀 Spustenie

### Cez Docker Compose (odporúčané)

```bash
# Z root priečinku demo-app
docker compose up accidents_api
```

API bude dostupné na: **http://localhost:8000**

Swagger dokumentácia: **http://localhost:8000/docs**

### Lokálne (pre vývoj)

```bash
cd accidents_api

# Inštalácia závislostí cez Poetry
poetry install

# Aktivácia virtuálneho prostredia
poetry shell

# Spustenie servera
uvicorn bp_api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 Štruktúra projektu

```
accidents_api/
├── pyproject.toml              # Poetry dependencies
├── poetry.lock
├── README.md                   # Tento súbor
└── bp_api/                     # Zdrojový kód
    ├── main.py                 # FastAPI aplikácia + CORS
    ├── data_loader.py          # Načítanie dát pri štarte
    ├── models/                 # Pydantic modely
    │   ├── accidents_model.py  # Modely pre nehody
    │   ├── waze_model.py       # Modely pre Waze
    │   ├── data_map.py         # Číselníky a mapovania
    │   └── models.py           # Spoločné modely
    ├── routers/                # API endpointy
    │   ├── accidents.py        # Endpointy pre nehody
    │   ├── waze.py             # Endpointy pre Waze
    │   └── charts.py           # Štatistické endpointy
    └── utils/                  # Pomocné funkcie
        ├── api_client.py       # HTTP klient
        ├── filter.py           # Filtrovacie funkcie
        ├── logger.py           # Logovanie
        └── timestamp.py        # Práca s časom
```

---

## 🔌 API Endpointy

### 📍 **Base URL:** `http://localhost:8000`

### 🚗 Nehody (Accidents)

#### `GET /api/v1/accidents/`

Vráti zoznam všetkých nehôd.

**Query parametre:**
- `limit` (int, optional) - Maximálny počet záznamov
- `offset` (int, optional) - Offset pre stránkovanie

**Response:**
```json
[
  {
    "p1": 12345,
    "p2a": "2024-01-15",
    "p2b": 1430,
    "p36": "Brno-město",
    "p37": "Brno",
    "p6": 1,
    "p10": 3,
    "p34": 0,
    "p35": 1,
    "x": -597234.5,
    "y": -1163789.2,
    "geog": "POINT(16.6081 49.1951)"
  }
]
```

#### `GET /api/v1/accidents/{p1}`

Vráti detail konkrétnej nehody podľa ID.

**Path parameter:**
- `p1` (int) - ID nehody

**Response:**
```json
{
  "p1": 12345,
  "p2a": "2024-01-15",
  "p2b": 1430,
  "p36": "Brno-město",
  "p37": "Brno",
  "druh_nehody": "Srážka s jedoucím nekolejovým vozidlem",
  "pocet_mrtvych": 0,
  "pocet_tazko_zranenych": 1,
  "coordinates": {
    "lat": 49.1951,
    "lon": 16.6081
  }
}
```

#### `POST /api/v1/accidents/filter`

Filtrované nehody podľa kritérií.

**Request body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "druh_nehody": [1, 2],
  "bbox": {
    "min_lon": 16.5,
    "min_lat": 49.1,
    "max_lon": 16.7,
    "max_lat": 49.3
  }
}
```

**Response:** Pole nehôd zodpovedajúcich filtrom

---

### 📡 Waze Reports

#### `GET /api/v1/waze/alerts`

Vráti zoznam Waze alertov (upozornení).

**Query parametre:**
- `type` (str, optional) - Typ alertu (ACCIDENT, HAZARD, JAM, atď.)
- `limit` (int, optional)

**Response:**
```json
[
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "type": "ACCIDENT",
    "subtype": "ACCIDENT_MINOR",
    "street": "Hlinky",
    "pubMillis": 1705320000000,
    "location": {
      "lat": 49.1951,
      "lon": 16.6081
    }
  }
]
```

#### `GET /api/v1/waze/jams`

Vráti zoznam Waze zápch.

**Response:**
```json
[
  {
    "uuid": 12345,
    "street": "Hlinky",
    "level": 3,
    "delay": 120,
    "length": 450,
    "speed": 25.5,
    "pubMillis": 1705320000000
  }
]
```

---

### 📊 Štatistiky a grafy (Charts)

#### `GET /api/v1/charts/accidents-by-time`

Distribúcia nehôd v čase (po hodinách/dňoch/mesiacoch).

**Query parametre:**
- `granularity` (str) - `hour`, `day`, `week`, `month`
- `from_date` (str) - YYYY-MM-DD
- `to_date` (str) - YYYY-MM-DD

**Response:**
```json
{
  "labels": ["2024-01", "2024-02", "2024-03"],
  "values": [45, 38, 52]
}
```

#### `GET /api/v1/charts/accidents-by-type`

Distribúcia nehôd podľa typu.

**Response:**
```json
{
  "Srážka s jedoucím nekolejovým vozidlem": 120,
  "Srážka s chodcem": 45,
  "Srážka s pevnou překážkou": 32
}
```

#### `GET /api/v1/charts/severity-distribution`

Distribúcia nehôd podľa závažnosti (ťažko zranení, mŕtvi).

**Response:**
```json
{
  "bez_zranenia": 450,
  "lahke_zranenia": 280,
  "tazke_zranenia": 65,
  "mrtvi": 8
}
```

---

## 📦 Modely (Pydantic schemas)

### `AccidentModel` (accidents_model.py)

Reprezentuje dopravnú nehodu.

```python
class AccidentModel(BaseModel):
    p1: int                    # ID nehody
    p2a: date                  # Dátum
    p2b: int                   # Čas (HHMM)
    p36: str                   # Okres
    p37: str                   # Obec
    p6: int                    # Druh nehody
    p7: Optional[int]          # Druh zrážky
    p10: int                   # Charakter nehody
    p34: int                   # Počet mŕtvych
    p35: int                   # Počet ťažko zranených
    x: float                   # Súradnica X (S-JTSK)
    y: float                   # Súradnica Y (S-JTSK)
    geog: str                  # WKT POINT (WGS84)
```

### `WazeAlertModel` (waze_model.py)

Reprezentuje Waze upozornenie.

```python
class WazeAlertModel(BaseModel):
    uuid: UUID
    type: str                  # ACCIDENT, HAZARD, JAM, ...
    subtype: Optional[str]     # ACCIDENT_MINOR, HAZARD_ON_ROAD, ...
    street: Optional[str]
    pubMillis: int             # Unix timestamp (ms)
    location: LocationModel    # { lat, lon }
    reportRating: Optional[int]
    confidence: Optional[int]
```

### `WazeJamModel` (waze_model.py)

Reprezentuje Waze zápchu.

```python
class WazeJamModel(BaseModel):
    uuid: int
    street: Optional[str]
    level: int                 # 0-5
    delay: int                 # Sekundy
    length: int                # Metre
    speed: float               # km/h
    speedKMH: float            # km/h (alias)
    pubMillis: int
    line: List[LocationModel]  # Polyline súradníc
```

---

## 🔄 Data Loader (`data_loader.py`)

Pri štarte aplikácie sa automaticky načítajú dáta z JSON súborov:

### Metódy:

- **`load_waze()`** - Načíta Waze alerts a jams z `datasets/processed_alerts.json`
- **`load_accidents_file()`** - Načíta nehody z `datasets/nehody.geojson`
- **`create_matched_tables()`** - Vytvorí matchované tabuľky (priestorovo-časové prepojenie)

### Dátové štruktúry v pamäti:

```python
data_loader.waze_alerts: List[WazeAlertModel]
data_loader.waze_jams: List[WazeJamModel]
data_loader.accidents: List[AccidentModel]
data_loader.matched_alerts: Dict[int, List[WazeAlertModel]]
```

---

## 🧪 Testovanie API

### Cez Swagger UI

Otvorte http://localhost:8000/docs a vyskúšajte endpointy interaktívne.

### Cez curl

```bash
# Všetky nehody
curl http://localhost:8000/api/v1/accidents/

# Detail nehody
curl http://localhost:8000/api/v1/accidents/12345

# Waze alerts
curl http://localhost:8000/api/v1/waze/alerts

# Štatistiky
curl http://localhost:8000/api/v1/charts/accidents-by-type
```

### Cez Python requests

```python
import requests

# Filtrované nehody
response = requests.post(
    "http://localhost:8000/api/v1/accidents/filter",
    json={
        "from_date": "2024-01-01",
        "to_date": "2024-12-31"
    }
)

accidents = response.json()
print(f"Počet nehôd: {len(accidents)}")
```

---

## 🔧 Konfigurácia

### CORS Origins

V `main.py` sú definované povolené origins pre frontend:

```python
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Vite HMR
]
```

Pre production pridajte produkčnú doménu.

### Dátové súbory

API očakáva tieto súbory v `bp_api/datasets/`:

```
datasets/
├── nehody.geojson           # Dopravné nehody (GeoJSON)
└── processed_alerts.json    # Waze alerts + jams
```

---

## 📊 Číselníky (data_map.py)

API používa číselníky Polície ČR pre interpretáciu kódov:

```python
DRUH_NEHODY = {
    1: "Srážka s jedoucím nekolejovým vozidlem",
    2: "Srážka s vozidlem zaparkovaným, odstaveným",
    3: "Srážka s pevnou překážkou",
    4: "Srážka s chodcem",
    # ...
}

CHARAKTER_NEHODY = {
    1: "Čelní",
    2: "Boční",
    3: "Zezadu",
    # ...
}
```

---

## 🐳 Docker

### Dockerfile (`Dockerfile.api`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Inštalácia Poetry
RUN pip install poetry

# Kopírovanie dependencies
COPY accidents_api/pyproject.toml accidents_api/poetry.lock ./

# Inštalácia bez dev dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction

# Kopírovanie kódu
COPY accidents_api/bp_api ./bp_api

# Exponovanie portu
EXPOSE 8000

# Spustenie servera
CMD ["uvicorn", "bp_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔍 Logovanie

API používa štandardný Python `logging` modul.

**Konfigurácia v `utils/logger.py`:**

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Použitie:**

```python
from bp_api.utils.logger import logger

logger.info("Processing request...")
logger.error(f"Failed to load data: {error}")
```

---

## 🛠️ Utility funkcie

### `filter.py`

Pomocné funkcie pre filtrovanie dát:

- `filter_by_date_range(accidents, from_date, to_date)`
- `filter_by_bbox(accidents, min_lon, min_lat, max_lon, max_lat)`
- `filter_by_type(accidents, accident_types)`

### `timestamp.py`

Konverzia časov:

- `millis_to_datetime(millis)` - Unix ms → datetime
- `datetime_to_millis(dt)` - datetime → Unix ms

---

## 📝 Príklady použitia

### Získanie nehôd v určenom období

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/accidents/filter",
    json={
        "from_date": "2024-06-01",
        "to_date": "2024-06-30"
    }
)

june_accidents = response.json()
```

### Waze alerts v blízkosti nehody

```python
import requests

# Získaj nehodu
accident = requests.get("http://localhost:8000/api/v1/accidents/12345").json()

# Získaj alerts v čase nehody ±30 minút
alerts = requests.get(
    "http://localhost:8000/api/v1/waze/alerts",
    params={
        "from_time": accident["p2a"] + " " + str(accident["p2b"]),
        "radius_m": 500
    }
).json()
```

---

## 🧩 Integrácia s Frontend

Frontend používa tento API cez `VITE_API_URL` environment premennú:

```typescript
// frontend/src/config.ts
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Fetch accidents
const response = await fetch(`${API_URL}/api/v1/accidents/`);
const accidents = await response.json();
```

---

## 🚧 Known Issues & Limitations

1. **In-memory dáta** - Všetky dáta sa načítavajú do pamäte pri štarte. Pre veľké datasety použite databázové pripojenie.
2. **Žiadna autentifikácia** - API je otvorené. Pre production pridajte OAuth2 / JWT.
3. **Statické dáta** - Dáta sa načítavajú len pri štarte. Pre real-time use-case implementujte periodické načítavanie.

---

## 🔗 Súvisiace dokumenty

- [Hlavné README](../README.md)
- [Database README](../database_creation/README.md)
- [Analyticity Backend README](../Analyticity-backend/README.md)
- [Frontend README](../frontend/README.md)

---

## 📄 Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = "^0.27.0"
pydantic = "^2.5.0"
geopandas = "^0.14.0"
shapely = "^2.0.0"
pandas = "^2.1.0"
```

---