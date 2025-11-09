/*
	author: Veronika Šimková (xsimko14)
	file: casulties-timeline-chart.tsx
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
import { CartesianGrid, Line, LineChart, XAxis } from "recharts";

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
      <div className="w-full grid grid-cols-3 pt-4 gap-x-4">
        <Skeleton className="w-full h-10" />
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
  data: {
    date: string;
    fatalities: number;
    severe_injuries: number;
    minor_injuries: number;
  }[];
  className?: string;
}) => {
  const chartConfig = {
    fatalities: {
      label: "Fatalities",
      color: "hsl(0 91% 60%)", // Red color
    },
    severe_injuries: {
      label: "Severe Injuries",
      color: "hsl(45 91% 60%)", // Amber/orange color
    },
    minor_injuries: {
      label: "Minor Injuries",
      color: "hsl(217 91% 60%)", // Blue color
    },
  };
  return (
    <ChartContainer
      config={chartConfig}
      className={cn("h-[300px] pt-4 w-full", className)}
    >
      <LineChart
        accessibilityLayer
        data={data}
        margin={{
          left: 12,
          right: 12,
          top: 20,
          bottom: 0,
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
        <Line
          dataKey="fatalities"
          type="monotone"
          stroke="var(--color-fatalities)"
          dot={false}
        />
        <Line
          dataKey="severe_injuries"
          type="monotone"
          stroke="var(--color-severe_injuries)"
          dot={false}
        />
        <Line
          dataKey="minor_injuries"
          type="monotone"
          stroke="var(--color-minor_injuries)"
          dot={false}
        />
        <ChartLegend content={<ChartLegendContent />} />
      </LineChart>
    </ChartContainer>
  );
};

export function CasualtiesTimelineChart({
  description,
  className,
}: TimelineChartProps) {
  const [open, setOpen] = useState(false);
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data, isLoading, isError } = useQuery({
    queryKey: ["charts", "timeline-severity", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<
        {
          date: string;
          fatalities: number;
          severe_injuries: number;
          minor_injuries: number;
        }[]
      >(`charts/timeline-severity-chart`, {
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
            <Expand className="size-4 text-gray-500" />
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
