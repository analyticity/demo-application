/*
	author: Veronika Šimková (xsimko14)
	file: charts-page.tsx
*/

import { AccidentByMonthChart } from "@/components/accident-components/charts/accidents-by-month-chart";
import { CasualtiesTimelineChart } from "@/components/accident-components/charts/casulties-timeline-chart";
import { AccidentDistributionChart } from "@/components/accident-components/charts/distribution-chart";
import { AccidentDistributionPieChart } from "@/components/accident-components/charts/distribution-pie-chart";
import { HeatTableChart } from "@/components/accident-components/charts/heat-table-chart";
import { PeriodSummary } from "@/components/accident-components/charts/period-summary";
import { TimelineChart } from "@/components/accident-components/charts/timeline-chart";
import { WazeEventsDistributionPieChart } from "@/components/accident-components/charts/waze-events-distribution-chart";
import { WazeRoadTypesDistributionPieChart } from "@/components/accident-components/charts/waze-road-types-chart";
import { useTranslation } from "react-i18next";

export const ChartPage = () => {
  const { t } = useTranslation();

  return (
    <div className="pt-10 min-h-screen container mx-auto grid md:grid-cols-2 gap-6 px-6 md:px-0 mb-20 overflow-x-hidden">
      <PeriodSummary />
      <TimelineChart
        description={t("chart.daily_count")}
        className="md:col-span-2"
      />
      <CasualtiesTimelineChart
        description={t("chart.casualties_timeline")}
        className="md:col-span-2"
      />
      <AccidentDistributionPieChart
        attribute="alkohol"
        description={t("chart.alcohol")}
      />
      <AccidentDistributionChart
        attribute="hlavni_pricina"
        description={t("chart.main_cause")}
        className="max-w-full"
      />
      <AccidentDistributionChart
        attribute="smerove_pomery"
        description={t("chart.direction_conditions")}
      />
      <AccidentDistributionPieChart
        attribute="drogy"
        description={t("chart.drugs")}
      />
      <AccidentDistributionPieChart
        attribute="druh_komun"
        description={t("chart.road_type")}
      />
      <AccidentByMonthChart description={t("chart.monthly_count")} />
      <HeatTableChart
        description={t("chart.day_hour_count")}
        className="md:col-span-2"
      />
      <WazeEventsDistributionPieChart />
      <WazeRoadTypesDistributionPieChart />
    </div>
  );
};
