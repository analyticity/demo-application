/*
	author: Veronika Šimková (xsimko14)
	file: heat-map.tsx
*/

import L, { HeatLatLngTuple } from "leaflet";
import "leaflet.heat";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { useMap } from "react-leaflet";

interface HeatmapLayerProps {
  points: HeatLatLngTuple[];
}

export const HeatmapLayer = ({ points }: HeatmapLayerProps) => {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    // Create and add the heat layer
    const heatLayer = L.heatLayer(points, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: { 0.4: "blue", 0.65: "lime", 1: "red" },
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, points]);

  return null;
};
