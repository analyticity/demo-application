/*
	author: Veronika Šimková (xsimko14)
	file: heat-table-chart.tsx
*/

import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDebounce } from "@/hooks/use-debounce";
import { cn } from "@/lib/utils";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { FC, useMemo } from "react";

type AccidentDistributionChartProps = {
  description?: string;
  className?: string;
};

type dataType = Record<string, Record<string, number>>;

export const HeatTableChart: FC<AccidentDistributionChartProps> = ({
  description,
  className,
}) => {
  const configStore = useConfigStore();
  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data, isLoading } = useQuery({
    queryKey: ["charts-heat-table", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<dataType>(`charts/heatmap-table`, {
        params: configStore.asQueryParams(),
      });

      return data;
    },
  });

  const transformedData = useMemo(() => {
    if (!data) return null;

    const transformed: Record<string, Record<string, number>> = {
      "0": {},
      "1": {},
      "2": {},
      "3": {},
      "4": {},
      "5": {},
      "6": {},
    };

    // Loop through original data (hour -> day) and swap
    Object.entries(data).forEach(([hour, dayValues]) => {
      Object.entries(dayValues).forEach(([day, value]) => {
        if (!transformed[day]) {
          transformed[day] = {};
        }
        transformed[day][hour] = value;
      });
    });

    return transformed;
  }, [data]);

  // Calculate maximum values for color scaling
  const { maxDayValue, maxTotalValue, columnSums, grandTotal } = useMemo(() => {
    if (!transformedData)
      return {
        maxDayValue: 0,
        maxTotalValue: 0,
        columnSums: {},
        grandTotal: 0,
      };

    let maxDay = 0;
    let maxTotal = 0;
    let columnSums: Record<string, number> = {};
    let grandTotal = 0;

    // First, create columnSums keys for all possible hours
    if (data) {
      Object.keys(data).forEach((hour) => {
        columnSums[hour] = 0;
      });
    }

    Object.values(transformedData).forEach((hourData) => {
      // Calculate day totals and find max
      const dayTotal = Object.entries(hourData).reduce((sum, [hour, val]) => {
        // Add to column sums
        columnSums[hour] = (columnSums[hour] || 0) + val;
        grandTotal += val;
        return sum + val;
      }, 0);

      if (dayTotal > maxTotal) maxTotal = dayTotal;

      // Find max for individual day values
      Object.values(hourData).forEach((value) => {
        if (value > maxDay) maxDay = value;
      });
    });

    return {
      maxDayValue: maxDay,
      maxTotalValue: maxTotal,
      columnSums,
      grandTotal,
    };
  }, [transformedData, data]);

  // Color functions for heatmap
  const getDayCellColor = (value: number) => {
    if (!maxDayValue) return "bg-gray-50";
    const ratio = value / maxDayValue;

    if (ratio < 0.25) return "bg-yellow-100";
    if (ratio < 0.5) return "bg-yellow-200";
    if (ratio < 0.75) return "bg-orange-200";
    return "bg-orange-300";
  };

  const getTotalCellColor = (value: number) => {
    if (!maxTotalValue) return "bg-gray-50";
    const ratio = value / maxTotalValue;

    if (ratio < 0.25) return "bg-blue-100";
    if (ratio < 0.5) return "bg-blue-200";
    if (ratio < 0.75) return "bg-blue-300";
    return "bg-blue-400";
  };

  // Get text color for better readability
  const getTextColor = (bgColor: string) => {
    if (bgColor === "bg-orange-300" || bgColor === "bg-blue-400") {
      return "text-gray-800";
    }
    return "text-gray-900";
  };

  // Map day numbers to day names
  const getDayName = (day: string): string => {
    switch (day) {
      case "0":
        return "Pondelok";
      case "1":
        return "Utorok";
      case "2":
        return "Streda";
      case "3":
        return "Štvrtok";
      case "4":
        return "Piatok";
      case "5":
        return "Sobota";
      case "6":
        return "Nedeľa";
      default:
        return day;
    }
  };

  if (!data || isLoading) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <CardTitle>{description}</CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="grid grid-cols-4 w-full mt-3 gap-x-6 h-[400px]">
            <Skeleton className="w-full h-full" />
            <Skeleton className="w-full h-full" />
            <Skeleton className="w-full h-full" />
            <Skeleton className="w-full h-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("w-full max-w-full overflow-x-scroll", className)}>
      <CardHeader className="flex flex-row items-center gap-2 pb-2">
        <CardTitle>{description}</CardTitle>
      </CardHeader>
      <CardContent className="pt-2 overflow-x-auto">
        {transformedData && (
          <Table>
            <TableHeader>
              <TableRow className="bg-blue-600 hover:none">
                <TableHead className="w-[120px] !text-white">
                  Deň/Hodina
                </TableHead>
                {data &&
                  Object.keys(data)
                    .sort((a, b) => Number(a) - Number(b))
                    .map((hour) => (
                      <TableHead
                        key={`hour-${hour}`}
                        className="text-white px-0 font-normal text-center"
                      >
                        {Number(hour)}
                      </TableHead>
                    ))}
                <TableHead className="text-white font-semibold text-center">
                  Celkovo
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {/* Sort days to ensure they appear in correct order */}
              {Object.entries(transformedData)
                .sort(([dayA], [dayB]) => Number(dayA) - Number(dayB))
                .map(([day, hourData], i) => {
                  // Calculate total for this row (day)
                  const rowTotal = Object.values(hourData).reduce(
                    (acc, val) => acc + val,
                    0,
                  );

                  // Get color for total cell
                  const totalCellColor = getTotalCellColor(rowTotal);
                  const totalTextColor = getTextColor(totalCellColor);

                  return (
                    <TableRow key={`row-${i}`}>
                      <TableCell className="font-semibold bg-blue-500 text-white">
                        {getDayName(day)}
                      </TableCell>
                      {/* Create cells for each hour in order */}
                      {data &&
                        Object.keys(data)
                          .sort((a, b) => Number(a) - Number(b))
                          .map((hour) => {
                            const value = hourData[hour] || 0;
                            const cellColor = getDayCellColor(value);
                            const textColor = getTextColor(cellColor);
                            return (
                              <TableCell
                                key={`day-${day}-hour-${hour}`}
                                className={cn(
                                  cellColor,
                                  textColor,
                                  "text-center",
                                )}
                              >
                                {value}
                              </TableCell>
                            );
                          })}
                      <TableCell
                        className={cn(
                          totalCellColor,
                          totalTextColor,
                          "text-center font-medium",
                        )}
                      >
                        {rowTotal}
                      </TableCell>
                    </TableRow>
                  );
                })}
              <TableRow className="border-t-2 border-gray-400">
                <TableCell className="font-semibold bg-blue-500 text-white">
                  Celkovo
                </TableCell>
                {columnSums &&
                  Object.keys(columnSums)
                    .sort((a, b) => Number(a) - Number(b))
                    .map((hour) => {
                      const sum = columnSums[hour] || 0;
                      const cellColor = getTotalCellColor(sum);

                      return (
                        <TableCell
                          key={`column-sum-${hour}`}
                          className={cn(
                            "bg-blue-500 text-white text-center font-medium",
                          )}
                        >
                          {sum}
                        </TableCell>
                      );
                    })}
                <TableCell
                  className={cn("text-center font-bold bg-blue-600 text-white")}
                >
                  {grandTotal}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};
