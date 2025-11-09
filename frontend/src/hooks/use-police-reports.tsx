/*
	author: Veronika Šimková (xsimko14)
	file: use-police-reports.tsx
*/

import { useDebounce } from "@/hooks/use-debounce";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { useQuery } from "@tanstack/react-query";

export const usePoliceReports = () => {
  const configStore = useConfigStore();

  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  return useQuery({
    queryKey: ["accidents", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<Accident[]>("/accidents", {
        params: { ...configStore.asQueryParams(), limit: 1000 },
      });
      return data;
    },
    refetchOnMount: false,
  });
};
