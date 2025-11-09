# Frontend - Analyticity React Application

**Frontend** je React + TypeScript aplikácia s mapovou vizualizáciou dopravných dát. Využíva Vite pre rýchly development, Leaflet pre mapy a TanStack Query pre state management.

---

## 🎯 Účel

Frontend poskytuje:
- **Interaktívnu mapu** s vizualizáciou nehôd, zápch a upozornení
- **Dashboard** s agregovanými štatistikami a grafmi
- **Filtrovanie** podľa času, ulíc, typu incidentov
- **Viacjazyčnosť** (slovenčina, čeština, angličtina)
- **Responzívny dizajn** pre desktop aj mobile

---

## 🚀 Spustenie

### Cez Docker Compose (odporúčané)

```bash
# Z root priečinku demo-app
docker compose up frontend
```

Aplikácia bude dostupná na: **http://localhost:5173**

HMR (Hot Module Replacement): **http://localhost:5174**

### Lokálne (pre vývoj)

```bash
cd frontend

# Inštalácia závislostí
npm install

# Spustenie dev servera
npm run dev

# Build pre production
npm run build

# Preview production buildu
npm run preview
```

---

## 📁 Štruktúra projektu

```
frontend/
├── package.json                # Dependencies a scripts
├── tsconfig.json               # TypeScript konfigurácia
├── vite.config.ts              # Vite konfigurácia
├── tailwind.config.js          # Tailwind CSS
├── index.html                  # HTML entry point
├── public/                     # Statické assets
│   ├── czech-republic.png      # Vlajky pre jazyky
│   ├── slovakia.png
│   └── united-kingdom.png
└── src/                        # Zdrojový kód
    ├── main.tsx                # React entry point
    ├── App.tsx                 # Root komponenta
    ├── index.css               # Globálne štýly
    ├── vite-env.d.ts           # Vite type definitions
    │
    ├── assets/                 # Obrázky, ikony
    │   ├── Brno.png
    │   ├── DataBrno.png
    │   ├── fit.png
    │   └── info.svg
    │
    ├── components/             # React komponenty
    │   ├── accident-components/    # Komponenty pre nehody
    │   ├── chart-components/       # Grafy (ApexCharts, Recharts)
    │   ├── filter-components/      # Filtre (dátumy, ulice)
    │   ├── homepage-components/    # Homepage widgety
    │   ├── map-components/         # Leaflet mapy
    │   ├── navigation-components/  # Navigácia, menu
    │   └── ui/                     # Reusable UI (shadcn/ui)
    │
    ├── hooks/                  # Custom React hooks
    │   ├── useAccidents.ts
    │   ├── useJams.ts
    │   ├── useStats.ts
    │   └── useLanguage.ts
    │
    ├── lib/                    # Utility funkcie
    │   └── utils.ts            # cn() helper, atď.
    │
    ├── locales/                # i18n preklady
    │   ├── cs.json             # Čeština
    │   ├── sk.json             # Slovenčina
    │   └── en.json             # Angličtina
    │
    ├── pages/                  # Stránky (routes)
    │   ├── HomePage.tsx
    │   ├── AccidentsPage.tsx
    │   ├── JamsPage.tsx
    │   ├── DashboardPage.tsx
    │   └── AboutPage.tsx
    │
    ├── routes/                 # React Router konfigurácia
    │   └── router.tsx
    │
    ├── stores/                 # Zustand stores (state management)
    │   ├── useFilterStore.ts
    │   ├── useMapStore.ts
    │   └── useUIStore.ts
    │
    ├── styles/                 # SCSS moduly
    │   └── *.module.scss
    │
    ├── types/                  # TypeScript typy
    │   ├── accidents.ts
    │   ├── jams.ts
    │   ├── alerts.ts
    │   └── api.ts
    │
    └── utils/                  # Helper funkcie
        ├── dateUtils.ts
        ├── geoUtils.ts
        └── apiClient.ts
```

---

## 🗺️ Hlavné stránky

### 1. **Home Page** (`/`)

- **Mapa Brna** s heat mapou nehôd
- **Časová os** s počtami jams/alerts
- **Metriky** (priemerná rýchlosť, delay, úroveň zápch)
- **Filter** podľa dátumu

### 2. **Accidents Page** (`/accidents`)

- **Interaktívna mapa** s markermi nehôd
- **Detail nehody** po kliknutí (sidebar)
- **Filtre:**
  - Časový rozsah
  - Typ nehody
  - Závažnosť (mŕtvi, ťažko zranení)
  - Bounding box (kreslenie na mape)

### 3. **Jams Page** (`/jams`)

- **Mapa s úsekmi ulíc** (farebné podľa hustoty zápch)
- **Filter podľa ulíc** (dropdown s autocomplete)
- **Legenda** (zelená/oranžová/červená)

### 4. **Dashboard** (`/dashboard`)

- **Grafy:**
  - Top 10 ulíc s najviac zápchami
  - Distribúcia alertov podľa typu
  - Časový vývoj (line chart)
- **Štatistiky v kartách**

### 5. **About** (`/about`)

- Informácie o projekte
- Zdroje dát
- Kontakt

---

## 🎨 UI Komponenty

Frontend používa **shadcn/ui** komponenty (built on Radix UI):

### Nainštalované komponenty:

- `Button` - Tlačidlá s variantmi
- `Card` - Karty pre widgety
- `Dialog` - Modály
- `Dropdown Menu` - Menu s akciami
- `Select` - Selecty s vyhľadávaním
- `Slider` - Posúvač pre rozsahy
- `Tooltip` - Tooltips
- `Separator` - Deliace čiary
- `ScrollArea` - Skrolovateľné oblasti

### Príklad použitia:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold">{value}</p>
      </CardContent>
    </Card>
  )
}
```

---

## 🗺️ Mapové komponenty (Leaflet)

### `MapContainer` - Základná mapa

```tsx
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

<MapContainer center={[49.1951, 16.6081]} zoom={13}>
  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
  <Marker position={[49.1951, 16.6081]}>
    <Popup>Brno - Hlavní nádraží</Popup>
  </Marker>
</MapContainer>
```

### `HeatmapLayer` - Heat mapa nehôd

```tsx
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

function HeatmapLayer({ points }: { points: [number, number, number][] }) {
  const map = useMap()
  
  useEffect(() => {
    const heatLayer = L.heatLayer(points, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
    }).addTo(map)
    
    return () => {
      map.removeLayer(heatLayer)
    }
  }, [map, points])
  
  return null
}
```

### `PolylineLayer` - Ulice s farbami

```tsx
import { Polyline } from 'react-leaflet'

{streets.map((street) => (
  <Polyline
    key={street.street_name}
    positions={street.path}  // [[lat, lon], ...]
    pathOptions={{
      color: street.color,   // 'green', 'orange', 'red'
      weight: 5,
      opacity: 0.7
    }}
  />
))}
```

---

## 📊 Grafy (ApexCharts)

### Line Chart - Časový vývoj

```tsx
import Chart from 'react-apexcharts'

const options = {
  chart: { type: 'line' },
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar'],
  },
}

const series = [
  { name: 'Jams', data: [30, 40, 35] },
  { name: 'Alerts', data: [20, 25, 22] },
]

<Chart options={options} series={series} type="line" height={350} />
```

### Bar Chart - Top ulice

```tsx
const options = {
  chart: { type: 'bar', horizontal: true },
  xaxis: {
    categories: ['Hlinky', 'Kotlářská', 'Purkyňova'],
  },
}

const series = [
  { name: 'Jams', data: [45, 38, 32] }
]

<Chart options={options} series={series} type="bar" height={300} />
```

---

## 🌐 Viacjazyčnosť (i18next)

### Konfigurácia (`src/main.tsx`)

```tsx
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import cs from './locales/cs.json'
import sk from './locales/sk.json'
import en from './locales/en.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      cs: { translation: cs },
      sk: { translation: sk },
      en: { translation: en },
    },
    fallbackLng: 'sk',
    interpolation: {
      escapeValue: false,
    },
  })
```

### Použitie v komponentoch

```tsx
import { useTranslation } from 'react-i18next'

function Header() {
  const { t, i18n } = useTranslation()
  
  return (
    <div>
      <h1>{t('header.title')}</h1>
      <button onClick={() => i18n.changeLanguage('cs')}>
        Čeština
      </button>
    </div>
  )
}
```

### Príklad prekladu (`locales/sk.json`)

```json
{
  "header": {
    "title": "Analyticity - Analýza dopravy",
    "home": "Domov",
    "accidents": "Nehody",
    "jams": "Zápchy"
  },
  "filters": {
    "date_range": "Časový rozsah",
    "streets": "Ulice",
    "apply": "Použiť"
  }
}
```

---

## 🔄 State Management

### Zustand Stores

#### `useFilterStore.ts`

```tsx
import { create } from 'zustand'

interface FilterState {
  fromDate: string
  toDate: string
  streets: string[]
  setFromDate: (date: string) => void
  setToDate: (date: string) => void
  setStreets: (streets: string[]) => void
}

export const useFilterStore = create<FilterState>((set) => ({
  fromDate: '2024-01-01',
  toDate: '2024-12-31',
  streets: [],
  setFromDate: (date) => set({ fromDate: date }),
  setToDate: (date) => set({ toDate: date }),
  setStreets: (streets) => set({ streets }),
}))
```

#### Použitie:

```tsx
function FilterPanel() {
  const { fromDate, toDate, setFromDate, setToDate } = useFilterStore()
  
  return (
    <div>
      <input 
        type="date" 
        value={fromDate} 
        onChange={(e) => setFromDate(e.target.value)} 
      />
      <input 
        type="date" 
        value={toDate} 
        onChange={(e) => setToDate(e.target.value)} 
      />
    </div>
  )
}
```

---

## 🔌 API Integration (TanStack Query)

### Custom hook s React Query

```tsx
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8010'

export function useJamsStats(fromDate: string, toDate: string) {
  return useQuery({
    queryKey: ['jams-stats', fromDate, toDate],
    queryFn: async () => {
      const response = await axios.post(
        `${API_URL}/brno/homepage/sum_statistics`,
        { from_date: fromDate, to_date: toDate }
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minút
  })
}
```

### Použitie v komponente:

```tsx
function StatsWidget() {
  const { fromDate, toDate } = useFilterStore()
  const { data, isLoading, error } = useJamsStats(fromDate, toDate)
  
  if (isLoading) return <div>Načítavam...</div>
  if (error) return <div>Chyba: {error.message}</div>
  
  return (
    <div>
      <p>Celkom zápch: {data.data_jams}</p>
      <p>Priemerná rýchlosť: {data.speedKMH} km/h</p>
    </div>
  )
}
```

---

## 🎨 Styling

### Tailwind CSS

Frontend používa **Tailwind CSS** pre styling.

**Príklad:**
```tsx
<div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-800">Štatistiky</h2>
  <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Načítať
  </button>
</div>
```

### SCSS Modules (optional)

```scss
// styles/MapPage.module.scss
.mapContainer {
  width: 100%;
  height: calc(100vh - 64px);
  
  .controls {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1000;
  }
}
```

```tsx
import styles from './MapPage.module.scss'

<div className={styles.mapContainer}>
  <div className={styles.controls}>...</div>
</div>
```

---

## 🔧 Environment Variables

### `.env` súbor

```bash
# Backend API URLs
VITE_API_URL=http://localhost:8000
VITE_BACKEND_API_URL=http://localhost:8010

# Mapbox token (optional)
VITE_MAPBOX_TOKEN=pk.eyJ1...
```

### Použitie v kóde:

```tsx
const API_URL = import.meta.env.VITE_API_URL
const BACKEND_URL = import.meta.env.VITE_BACKEND_API_URL
```

---

## 🧪 Testovanie

### Unit testy (Vitest - budúce)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```tsx
// __tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)
  expect(screen.getByText('Click me')).toBeInTheDocument()
})
```

---

## 🐳 Docker

### Dockerfile (`Dockerfile.frontend.dev`)

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Kopírovanie package.json
COPY frontend/package*.json ./

# Inštalácia dependencies
RUN npm install

# Exponovanie portov
EXPOSE 5173 5174

# Spustenie dev servera
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Volume mounting:** Kód sa mountuje ako volume pre hot-reload.

---

## 🚀 Build & Deployment

### Development build

```bash
npm run dev
```

### Production build

```bash
npm run build

# Output: dist/
```

### Preview production buildu

```bash
npm run preview
```

### Deploy (príklad - Nginx)

```nginx
server {
  listen 80;
  server_name analyticity.example.com;
  
  root /var/www/analyticity/dist;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:8010;
  }
}
```

---

## 📦 Hlavné dependencies

| Balík | Verzia | Účel |
|-------|--------|------|
| `react` | ^18.3.1 | UI framework |
| `react-router` | ^7.2.0 | Routing |
| `vite` | ^6.0.5 | Build tool |
| `typescript` | ~5.6.2 | Type safety |
| `tailwindcss` | ^3.4.1 | CSS framework |
| `@tanstack/react-query` | ^5.61.3 | Data fetching |
| `axios` | ^1.7.7 | HTTP client |
| `leaflet` | ^1.9.4 | Mapy |
| `react-leaflet` | ^4.2.1 | React wrapper pre Leaflet |
| `apexcharts` | ^4.7.0 | Grafy |
| `i18next` | ^25.0.1 | Internacionalizácia |
| `zustand` | (viď package.json) | State management |
| `framer-motion` | ^12.4.7 | Animácie |

---

## 🎯 Best Practices

### 1. **Komponenty**
- Rozdeliť na malé, reusable komponenty
- Použiť TypeScript pre type safety
- Prop validácia cez TypeScript interfaces

### 2. **State Management**
- Lokálny state: `useState`, `useReducer`
- Globálny state: Zustand stores
- Server state: TanStack Query

### 3. **API Calls**
- Vždy cez TanStack Query (caching, invalidation)
- Error handling
- Loading states

### 4. **Performance**
- `React.memo()` pre expensive komponenty
- `useMemo()`, `useCallback()` kde má zmysel
- Code splitting (`React.lazy()`)
- Image optimization

### 5. **Accessibility**
- Používať sémantické HTML elementy
- ARIA labels kde treba
- Keyboard navigation

---

## 🔍 Debugging

### React DevTools

Nainštalujte **React Developer Tools** (browser extension).

### Vite DevTools

- Hot Module Replacement (HMR) automaticky
- Source maps pre debugging

### Network Tab

Sledujte API requesty v Developer Tools → Network.

---

## 🔗 Súvisiace dokumenty

- [Hlavné README](../README.md)
- [Database README](../database_creation/README.md)
- [Accidents API README](../accidents_api/README.md)
- [Analyticity Backend README](../Analyticity-backend/README.md)

---


## 📄 Licencia

MIT License - projekt vytvorený pre bakalársku prácu.

