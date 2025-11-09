/*
	author: Veronika Šimková (xsimko14)
	file: accidents-by-month-chart.tsx
*/

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/use-debounce";
import { cn } from "@/lib/utils";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { format } from "date-fns";
import { FC } from "react";

type AccidentDistributionChartProps = {
  description?: string;
  className?: string;
};

type MonthDistributionData = Record<string, Record<string, number>>;

const chartConfig = {
  2025: {
    label: "2025",
  },
  2024: {
    label: "2024",
    color: "hsl(45 91% 60%)", // Amber/orange color
  },
  2023: {
    label: "2023",
  },
  2022: {
    label: "2022",
  },
};

export const AccidentByMonthChart: FC<AccidentDistributionChartProps> = ({
  description,
  className,
}) => {
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const getMonthName = (monthCode: string): string => {
    const date = new Date(2025, Number(monthCode) - 1, 1);

    return format(date, "MMMM");
  };

  const { data, isLoading } = useQuery({
    queryKey: ["charts-by-month", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<MonthDistributionData>(
        `charts/accidents-by-month`,
        {
          params: configStore.asQueryParams(),
        },
      );

      const transformedData = Object.entries(data).map(([key, value]) => {
        const entry: any = {
          name: getMonthName(key),
        };

        Object.entries(value).forEach(([year, count]) => {
          entry[year] = count;
        });

        return entry;
      });
      return transformedData;
    },
  });

  if (!data || isLoading) {
    return (
      <Card
        className={cn("max-h-[370px] py-4 overflow-hidden w-full", className)}
      >
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
  }

  return (
    <Card className={cn("w-full max-h-[370px] overflow-hidden", className)}>
      <CardHeader className="flex flex-row items-center gap-2 pb-2">
        <CardTitle>{description}</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={chartConfig}
          className="h-[300px] pt-4 w-[114%] md:w-full max-md:-ml-8"
        >
          <BarChart data={data}>
            <ChartLegend content={<ChartLegendContent />} />
            <CartesianGrid vertical={false} className="stroke-border" />
            <XAxis
              dataKey="name"
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 12 }}
              tickMargin={8}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 12 }}
              tickMargin={8}
            />
            {["2022", "2023", "2024", "2025"].map((year, i) => (
              <Bar
                dataKey={year}
                key={`${year}-${i}`}
                fill={`hsl(var(--chart-${i + 1}))`}
                stackId={`a`}
              />
            ))}

            <ChartTooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;

                return (
                  <div className="rounded-lg border bg-background p-2 shadow-sm">
                    <div className="flex flex-col items-center gap-y-2">
                      <span className="font-medium text-start w-full border-b pb-0.5">
                        {payload[0].payload.name}
                      </span>
                      <div className="w-full flex flex-col gap-y-1">
                        {payload.map((payloadData, i) => (
                          <div
                            className="grid grid-cols-2 gap-2"
                            key={`tooltip-${i}`}
                          >
                            <div className="flex items-center gap-2">
                              <div
                                className={`h-2 w-2 rounded`}
                                style={{
                                  background: payloadData.fill,
                                }}
                              />
                              <p>{payloadData.dataKey}</p>
                            </div>
                            <div className="text-right font-medium">
                              <p>{payloadData.value}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              }}
              cursor={{ fill: "var(--color-accidents)", opacity: 0.1 }}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
