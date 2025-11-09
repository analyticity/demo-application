/*
	author: Veronika Šimková (xsimko14)
	file: distribution-pie-chart.tsx
*/

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/use-debounce";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { useQuery } from "@tanstack/react-query";
import { PieChartComponent } from "./pie-chart";

export function AccidentDistributionPieChart({
  description,
  attribute,
}: DistributionChartProps) {
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data } = useQuery({
    queryKey: ["charts", attribute, debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<Record<string, number>>(
        `charts/accidents-by-attribute`,
        {
          params: { ...configStore.asQueryParams(), attribute: attribute },
        },
      );
      const transformedData = Object.entries(data)
        .map(([key, value]) => ({
          name: key,
          value: value,
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 6);
      return transformedData;
    },
  });

  if (!data) {
    return (
      <Card className="flex flex-col">
        <CardHeader className="flex-row items-start space-y-0 pb-0">
          <div className="grid gap-1">
            <CardTitle>{description}</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex flex-1 justify-center py-4">
          <Skeleton className="w-full h-full" />
        </CardContent>
      </Card>
    );
  }

  return <PieChartComponent data={data} description={description} />;
}
