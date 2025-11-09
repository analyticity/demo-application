/*
	author: Veronika Šimková (xsimko14)
	file: waze-hover-store.ts
*/

import { create } from "zustand";

interface HoverState {
  hoveredWazeId: string | null;
  setHoveredWazeId: (id: string | null) => void;
}

export const useWazeHoverStore = create<HoverState>((set) => ({
  hoveredWazeId: null,
  setHoveredWazeId: (id) => set({ hoveredWazeId: id }),
}));
