/*
	author: Veronika Šimková (xsimko14)
	file: period-summary.tsx
*/

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/use-debounce";
import { useConfigStore } from "@/stores/config-store";
import { apiClient } from "@/utils/api";
import { formatLargeNumber } from "@/utils/utils";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { useTranslation } from "react-i18next";

type PeriodSummaryData = {
  accident_count: number;
  fatalities_count: number;
  seriously_injured: number;
  total_damage_cost: number;
};

export const PeriodSummary = () => {
  const configStore = useConfigStore();
  const { t } = useTranslation();

  const debouncedFilter = useDebounce(
    JSON.stringify(configStore.asQueryParams()),
    500,
  );

  const { data, isLoading, isError } = useQuery({
    queryKey: ["charts", "summary", debouncedFilter],
    queryFn: async () => {
      const { data } = await apiClient.get<PeriodSummaryData>(
        `charts/period-summary`,
        {
          params: configStore.asQueryParams(),
        },
      );
      return data;
    },
  });

  const formattedRange = `${format(configStore.getTimeline().startDate, "dd.MM.yyyy")} - ${format(
    configStore.getTimeline().endDate,
    "dd.MM.yyyy",
  )}`;

  const Description = () => (
    <CardDescription>
      {t("summary.description")}{" "}
      <span className="font-medium">({formattedRange}).</span>
    </CardDescription>
  );

  if (!data || isLoading || isError) {
    return (
      <Card className="md:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle>{t("summary.title")}</CardTitle>
          <Description />
        </CardHeader>
        <CardContent className="pt-2">
          <div className="h-[0.4px] w-full bg-gray-200"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-4 h-[84px]">
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
    <Card className="md:col-span-2">
      <CardHeader className="pb-2">
        <CardTitle>{t("summary.title")}</CardTitle>
        <Description />
      </CardHeader>
      <CardContent className="pt-2">
        <div className="h-[0.4px] w-full bg-gray-200"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-4">
          <div className="space-y-2">
            <p className="text-gray-500">{t("summary.total_accidents")}</p>
            <p className="text-3xl font-bold">{data.accident_count}</p>
          </div>
          <div className="space-y-2">
            <p className="text-gray-500">{t("summary.fatalities")}</p>
            <p className="text-3xl font-bold">{data.fatalities_count}</p>
          </div>
          <div className="space-y-2">
            <p className="text-gray-500">{t("summary.serious_injuries")}</p>
            <p className="text-3xl font-bold">{data.seriously_injured}</p>
          </div>
          <div className="space-y-2">
            <p className="text-gray-500">{t("summary.total_damage")}</p>
            <p className="text-3xl font-bold">
              {formatLargeNumber(data.total_damage_cost)}{" "}
              <span className="text-sm text-gray-600">CZK</span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
