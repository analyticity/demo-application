/*
	author: Veronika Šimková (xsimko14)
	file: home-page.tsx
*/

import { LayerFilter } from "@/components/accident-components/filters/layer-filter";
import { AccidentDetailCard } from "@/components/accident-components/map/accident-detail-card";
import {
  AccidentMarker,
  WazeReportMarker,
} from "@/components/accident-components/map/accident-marker";
import { HeatmapLayer } from "@/components/accident-components/map/heat-map";
import { usePoliceReports } from "@/hooks/use-police-reports";
import { useWazeReports } from "@/hooks/use-waze-reports";
import { useLayerStore } from "@/stores/layer-store";
import { useWazeStore } from "@/stores/waze-cache-store";
import { useWazeHoverStore } from "@/stores/waze-hover-store";
import { isAccident, isWazeReport } from "@/utils/utils";
import { divIcon, HeatLatLngTuple } from "leaflet";
import "leaflet.heat";
import "leaflet/dist/leaflet.css";
import { useMemo, useState } from "react";
import { renderToString } from "react-dom/server";
import { MapContainer, Marker, TileLayer } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";

export const HomePage = () => {
  const { activeFilters } = useLayerStore();
  const { hoveredWazeId } = useWazeHoverStore();
  const wazeStore = useWazeStore();

  const [selectedAccident, setSelectedAccident] = useState<
    Accident | WazeReport | null
  >(null);

  const { data: policeRaw } = usePoliceReports();
  const { data: wazeRaw }   = useWazeReports();


  // const { data: policeData } = usePoliceReports();
  // const { data: wazeData } = useWazeReports();
  
  // vždy pole (aj na prvý render)
const policeData = Array.isArray(policeRaw)
  ? policeRaw
  : Array.isArray((policeRaw as any)?.features)
  ? (policeRaw as any).features
  : [];

const wazeData = Array.isArray(wazeRaw)
  ? wazeRaw
  : Array.isArray((wazeRaw as any)?.features)
  ? (wazeRaw as any).features
  : [];
  
  const clusterOptions = {
    chunkedLoading: true,
    spiderfyOnMaxZoom: true,
    disableClusteringAtZoom: 17,
  };

  const heatmapPoints = useMemo(() => {
    const points: HeatLatLngTuple[] = [];

    // Add police data points if that filter is active and data is available
    if (activeFilters.police && policeData) {
      policeData.forEach((accident) => {
        points.push([accident.geometry.y, accident.geometry.x, 2]);
      });
    }

    if (activeFilters.waze && wazeData) {
      wazeData.forEach((accident) => {
        points.push([accident.y, accident.x, 1]); // lat, lng, intensity
      });
    }

    return points;
  }, [policeData, wazeData, activeFilters.police, activeFilters.waze]);

  // Find related waze reports for selected police accident
  const relatedWazeReports = useMemo(() => {
    if (!selectedAccident || !wazeData || isWazeReport(selectedAccident)) {
      return [];
    }

    return wazeData.filter((report) =>
      selectedAccident.attributes.matched_waze?.includes(report.uuid),
    );
  }, [selectedAccident, wazeData]);

  const customIcon = (accident: Accident) => {
    return divIcon({
      className: "custom-marker",
      html: renderToString(
        <AccidentMarker
          accident={accident}
          selected={
            selectedAccident && isAccident(selectedAccident)
              ? accident.attributes.id_nehody ===
                selectedAccident.attributes.id_nehody
              : false
          }
        />,
      ),
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  };

  const customWazeIcon = (accident: WazeReport) => {
    return divIcon({
      className: "custom-marker",
      html: renderToString(
        <WazeReportMarker
          accident={accident}
          selected={
            selectedAccident === accident || accident.uuid === hoveredWazeId
          }
        />,
      ),
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  };

  return (
    <main className="relative mx-auto h-[calc(100dvh-48px)]">
      <MapContainer
        center={[49.19469087608702, 16.61131840963104]}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {activeFilters.heatmap && <HeatmapLayer points={heatmapPoints} />}

        {hoveredWazeId &&
          (() => {
            const accident = wazeStore.getReportById(hoveredWazeId);
            if (accident) {
              return (
                <Marker
                  position={[accident.y, accident.x]}
                  key={`waze-${hoveredWazeId}`}
                  icon={customWazeIcon(accident)}
                  eventHandlers={{
                    click: () => {
                      setSelectedAccident(accident);
                    },
                  }}
                />
              );
            }
            return null;
          })()}

        <MarkerClusterGroup {...clusterOptions}>
          {!activeFilters.heatmap &&
            activeFilters.police &&
            policeData &&
            policeData.map((accident, i) => (
              <Marker
                position={[accident.geometry.y, accident.geometry.x]}
                key={`accident-${i}`}
                icon={customIcon(accident)}
                eventHandlers={{
                  click: () => {
                    setSelectedAccident(accident);
                  },
                }}
              />
            ))}
          {!activeFilters.heatmap &&
            activeFilters.waze &&
            wazeData &&
            wazeData
              .filter((event) => event.is_primary)
              .map((accident, i) => (
                <Marker
                  position={[accident.y, accident.x]}
                  key={`waze-${i}`}
                  icon={customWazeIcon(accident)}
                  eventHandlers={{
                    click: () => {
                      setSelectedAccident(accident);
                    },
                  }}
                />
              ))}
        </MarkerClusterGroup>

        {!activeFilters.heatmap &&
          relatedWazeReports.length > 0 &&
          relatedWazeReports.map((accident, i) => (
            <Marker
              position={[accident.y, accident.x]}
              key={`related-waze-${i}`}
              icon={customWazeIcon(accident)}
              eventHandlers={{
                click: () => {
                  setSelectedAccident(accident);
                },
              }}
            />
          ))}
      </MapContainer>

      {selectedAccident && (
        <AccidentDetailCard
          selectedAccident={selectedAccident}
          setSelectedAccident={setSelectedAccident}
        />
      )}

      <LayerFilter />
    </main>
  );
};
