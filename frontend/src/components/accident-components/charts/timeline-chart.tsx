/*
	author: Veronika Šimková (xsimko14)
	file: timeline-chart.tsx
*/

import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
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
import { format } from "date-fns";
import { Expand } from "lucide-react";
import { useState } from "react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";

type TimelineChartProps = {
  description: string;
  className?: string;
};

const ChartSkeleton = ({
  description,
}: {
  description: string | undefined;
}) => (
  <Card className="max-h-[370px] py-4 w-full col-span-2">
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

const TimelineChartComponent = ({
  data,
  className,
}: {
  data: { date: string; incidents: number }[];
  className?: string;
}) => {
  const chartConfig = {
    incidents: {
      label: "Accidents",
      color: "hsl(217 91% 60%)", // Bright blue color
    },
    waze_reports: {
      label: "Waze reports",
      color: "hsl(212 95% 68%)",
    },
  };
  return (
    <ChartContainer
      config={chartConfig}
      className={cn("h-[300px] pt-4 w-full", className)}
    >
      <AreaChart
        accessibilityLayer
        data={data}
        margin={{
          left: 12,
          right: 12,
        }}
      >
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="date"
          tickLine={false}
          axisLine={false}
          tickMargin={6}
          minTickGap={40}
        />
        <ChartTooltip
          cursor={true}
          content={
            <ChartTooltipContent indicator="dot" className="min-w-[140px]" />
          }
        />
        <Area
          dataKey="incidents"
          type="linear"
          fill="var(--color-incidents)"
          fillOpacity={0.4}
          stroke="var(--color-incidents)"
        />
        <Area
          dataKey="waze_reports"
          type="linear"
          fill="var(--color-waze_reports)"
          fillOpacity={0.4}
          stroke="var(--color-waze_reports)"
        />
        <ChartLegend content={<ChartLegendContent />} />
      </AreaChart>
    </ChartContainer>
  );
};

export function TimelineChart({ description, className }: TimelineChartProps) {
  const [open, setOpen] = useState(false);
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data, isLoading, isError } = useQuery({
    queryKey: ["charts", "timeline", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<
        { date: string; incidents: number; waze_reports: number }[]
      >(`charts/timeline-chart`, {
        params: configStore.asQueryParams(),
      });

      return data.map((item) => {
        return { ...item, date: format(new Date(item.date), "dd.MM.yyyy") };
      });
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
          <button onClick={() => setOpen(true)}>
            <Expand className="size-4  text-gray-500" />
          </button>
        </CardHeader>
        <CardContent className="w-full">
          <TimelineChartComponent data={data} />
        </CardContent>
      </Card>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="md:min-w-[90vw]">
          <DialogHeader>
            <DialogTitle>{description}</DialogTitle>
          </DialogHeader>
          <TimelineChartComponent data={data} className="h-[400px]" />
        </DialogContent>
      </Dialog>
    </>
  );
}
