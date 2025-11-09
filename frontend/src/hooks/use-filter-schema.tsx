/*
	author: Veronika Šimková (xsimko14)
	file: use-filter-schema.tsx
*/

import { apiClient } from "@/utils/api";
import { useQuery } from "@tanstack/react-query";

type NumericFilterSchema = {
  type: "number";
  min_val: number;
  max_val: number;
};

type OptionsFilterSchema = {
  type: "options";
  values: string[];
};

type FilterSchemaItem = NumericFilterSchema | OptionsFilterSchema;

export type FilterSchema = Record<string, FilterSchemaItem>;

export const useFilterSchema = () => {
  return useQuery({
    queryKey: ["filter-schema"],
    queryFn: async () => {
      const { data } = await apiClient.get<FilterSchema>(
        "/charts/filter-schema",
      );
      return data;
    },
  });
};
