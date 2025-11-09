/*
	author: Veronika Šimková (xsimko14)
	file: layer-store.ts
*/

import { create } from "zustand";

type LayerFilters = {
  police: boolean;
  waze: boolean;
  heatmap: boolean;
};

interface LayerState {
  activeFilters: LayerFilters;
  toggleFilter: (type: keyof LayerFilters) => void;
}

export const useLayerStore = create<LayerState>((set) => ({
  activeFilters: {
    police: true,
    waze: false,
    heatmap: false,
  },
  toggleFilter: (type) =>
    set((state) => ({
      activeFilters: {
        ...state.activeFilters,
        [type]: !state.activeFilters[type],
      },
    })),
}));
