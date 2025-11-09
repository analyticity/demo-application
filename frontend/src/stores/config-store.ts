/*
	author: Veronika Šimková (xsimko14)
	file: config-store.ts
*/

import { addDays, differenceInDays, startOfDay, subYears } from "date-fns";
import { nanoid } from "nanoid";
import { create } from "zustand";
import { persist } from "zustand/middleware";

type Timeline = {
  startDate: Date;
  endDate: Date;
};

type AttributeType = "options" | "number";
export type Operator = "eq" | "neq" | "in" | "not_in" | "lt" | "gt";

export type Filter = {
  id: string;
  attribute: string;
  attribute_type: AttributeType;
  operator: Operator;
  value: string | number;
  options: Array<string | number>;
};

interface ConfigState {
  yearRange: number;
  timeline: number[];
  filters: Filter[];
  setTimeline: (x: number[]) => void;
  getTimeline: () => Timeline;
  createFilter: () => Record<string, string>;
  addFilter: (filter: Filter) => void;
  createDefaultFilter: () => Filter;
  addDefaultFilter: () => string; // Returns the ID of the created filter
  removeFilter: (id: string) => void;
  updateFilter: (id: string, updatedFilter: Partial<Filter>) => void;
  clearFilters: () => void;
  asRequestBody: () => {
    filters: {
      attribute: string;
      operator: Operator;
      value: string | number;
      id: string;
    }[];
  };
  asQueryParams: () => Record<string, string>;
}

// Base dates for the timeline calculation.
const yearRange = 3;
const today = startOfDay(new Date());
const baseStartDate = startOfDay(subYears(today, yearRange));
const totalDays = differenceInDays(today, baseStartDate);

export const useConfigStore = create<ConfigState>()(
  persist(
    (set, get) => ({
      yearRange: yearRange,
      timeline: [0, totalDays],
      filters: [],
      setTimeline: (val: number[]) => set(() => ({ timeline: val })),
      getTimeline: () => {
        const [startOffset, endOffset] = get().timeline;
        return {
          startDate: addDays(baseStartDate, startOffset),
          endDate: addDays(baseStartDate, endOffset),
        };
      },
      createFilter: () => {
        const [startOffset, endOffset] = get().timeline;
        return {
          startDate: addDays(baseStartDate, startOffset).toISOString(),
          endDate: addDays(baseStartDate, endOffset).toISOString(),
        };
      },
      createDefaultFilter: () => {
        return {
          id: nanoid(),
          attribute: "",
          attribute_type: "options",
          operator: "eq",
          value: "",
          options: [],
        };
      },
      addDefaultFilter: () => {
        const newFilter = get().createDefaultFilter();
        get().addFilter(newFilter);
        return newFilter.id;
      },
      addFilter: (filter: Filter) => {
        set((state) => ({
          filters: [...state.filters, filter],
        }));
      },
      removeFilter: (id: string) => {
        set((state) => ({
          filters: state.filters.filter((filter) => filter.id !== id),
        }));
      },
      updateFilter: (id: string, updatedFilter: Partial<Filter>) => {
        set((state) => ({
          filters: state.filters.map((filter) =>
            filter.id === id ? { ...filter, ...updatedFilter } : filter,
          ),
        }));
      },
      clearFilters: () => {
        set({ filters: [] });
      },
      asRequestBody: () => {
        return {
          filters: get()
            .filters.filter((filter) => filter.value && filter.attribute)
            .map((filter) => {
              return {
                attribute: filter.attribute,
                operator: filter.operator,
                value: filter.value,
                id: filter.id,
              };
            }),
        };
      },
      asQueryParams: (): Record<string, string> => {
        const filters = get().asRequestBody();
        const params: Record<string, string> = {};

        const [startOffset, endOffset] = get().timeline;

        filters.filters.forEach(({ attribute, operator, value, id }) => {
          params[`${attribute}:${operator}:${id}`] = String(value);
        });

        return {
          ...params,
          startDate: addDays(baseStartDate, startOffset).toISOString(),
          endDate: addDays(baseStartDate, endOffset).toISOString(),
        };
      },
    }),
    {
      name: "config-storage", // Name for the localStorage item
      partialize: (state) => ({
        // Only persist these fields
        timeline: state.timeline,
        filters: state.filters,
      }),
    },
  ),
);
