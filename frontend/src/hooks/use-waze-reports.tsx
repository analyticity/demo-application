/*
	author: Veronika Šimková (xsimko14)
	file: use-waze-reports.tsx
*/

import { useDebounce } from "@/hooks/use-debounce";
import { useConfigStore } from "@/stores/config-store";
import { useWazeStore } from "@/stores/waze-cache-store";
import { apiClient } from "@/utils/api";
import { useQuery } from "@tanstack/react-query";

export const useWazeReports = () => {
  const configStore = useConfigStore();
  const wazeStore = useWazeStore();

  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  return useQuery({
    queryKey: ["waze", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<WazeReport[]>("/waze", {
        params: configStore.asQueryParams(),
      });
      wazeStore.setReports(data);
      return data;
    },
    refetchOnMount: false,
  });
};
