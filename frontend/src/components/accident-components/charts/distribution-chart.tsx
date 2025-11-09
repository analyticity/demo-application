/*
	author: Veronika Šimková (xsimko14)
	file: distribution-chart.tsx
*/

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip } from "@/components/ui/chart";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/use-debounce";
import { cn } from "@/lib/utils";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { Expand } from "lucide-react";
import { useState } from "react";

const ChartSkeleton = ({
  description,
}: {
  description: string | undefined;
}) => (
  <Card className="h-[370px] py-4 w-full">
    <CardHeader className="flex flex-row items-center gap-2 pb-2">
      <CardTitle>{description}</CardTitle>
    </CardHeader>
    <CardContent className="flex flex-col items-center justify-center pt-4">
      <Skeleton className="w-full h-full min-h-[180px]" />
      <div className="w-full grid grid-cols-2 pt-4 gap-x-4">
        <Skeleton className="w-full h-10" />
        <Skeleton className="w-full h-10" />
      </div>
    </CardContent>
  </Card>
);

const DistributionChart = ({
  data,
  className,
}: {
  data: { name: string; value: number }[];
  className?: string;
}) => {
  const chartConfig = {
    accidents: {
      label: "Accidents",
      color: "hsl(217 91% 60%)", // Bright blue color
    },
  };
  return (
    <ChartContainer
      config={chartConfig}
      className={cn(
        "h-[300px] pt-4 w-[110%] md:w-full max-md:-ml-4",
        className,
      )}
    >
      <BarChart data={data}>
        <CartesianGrid vertical={false} className="stroke-border" />
        <XAxis
          dataKey="name"
          tickLine={false}
          axisLine={false}
          tick={{ fontSize: 12 }}
          tickMargin={8}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tick={{ fontSize: 12 }}
          tickMargin={8}
        />
        <Bar
          dataKey="value"
          fill="var(--color-accidents)"
          radius={[4, 4, 0, 0]}
          maxBarSize={50}
        />
        <ChartTooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;

            return (
              <div className="rounded-lg border bg-background p-2 shadow-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded bg-blue-500" />
                    <span className="font-medium">
                      {payload[0].payload.name}
                    </span>
                  </div>
                  <div className="text-right font-medium">
                    {payload[0].value}
                  </div>
                </div>
              </div>
            );
          }}
          cursor={{ fill: "var(--color-accidents)", opacity: 0.1 }}
        />
      </BarChart>
    </ChartContainer>
  );
};

export function AccidentDistributionChart({
  attribute,
  description,
  className,
}: DistributionChartProps) {
  const [open, setOpen] = useState(false);
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data, isLoading, isError } = useQuery({
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
          name: key.split("_").join(" "),
          value: value,
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 8);
      return transformedData;
    },
  });

  if (!data || isLoading) {
    return <ChartSkeleton description={description} />;
  }

  if (isError) {
    return null;
  }

  return (
    <>
      <Card className={cn("w-full max-h-[370px] overflow-hidden", className)}>
        <CardHeader className="flex flex-row items-center gap-2 pb-2 justify-between">
          <CardTitle>{description}</CardTitle>
          <button onClick={() => setOpen(true)} className="max-sm:hidden">
            <Expand className="size-4  text-gray-500" />
          </button>
        </CardHeader>
        <CardContent className="overflow-hidden">
          <DistributionChart data={data.slice(0, 6)} />
        </CardContent>
      </Card>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:min-w-[90vw]">
          <DialogHeader>
            <DialogTitle>{description}</DialogTitle>
          </DialogHeader>
          <DistributionChart data={data} className="h-[400px]" />
        </DialogContent>
      </Dialog>
    </>
  );
}
