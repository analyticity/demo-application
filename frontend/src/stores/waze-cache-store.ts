/*
	author: Veronika Šimková (xsimko14)
	file: waze-cache-store.ts
*/

import { create } from "zustand";

interface WazeStoreState {
  reportsById: Record<string, WazeReport>;
  reportIds: string[];
  setReports: (reports: WazeReport[]) => void;
  getReportById: (id: string) => WazeReport | undefined;
  clearReports: () => void;
}

export const useWazeStore = create<WazeStoreState>((set, get) => ({
  reportsById: {},
  reportIds: [],
  setReports: (reports) => {
    const reportsById: Record<string, WazeReport> = {};
    const reportIds: string[] = [];

    reports.forEach((report) => {
      reportsById[report.uuid] = report;
      reportIds.push(report.uuid);
    });

    set({ reportsById, reportIds });
  },
  getReportById: (id) => {
    return get().reportsById[id];
  },
  clearReports: () => {
    set({ reportsById: {}, reportIds: [] });
  },
}));
