/*
	author: Veronika Šimková (xsimko14)
	file: pie-chart.tsx
*/

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartStyle,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import React, { FC } from "react";
import { useTranslation } from "react-i18next";
import { Label, Pie, PieChart } from "recharts";

type PieChartComponentProps = {
  description?: string;
  data: { name: string; value: number }[];
  colorPrefix?: string;
};

export const PieChartComponent: FC<PieChartComponentProps> = ({
  data,
  description,
  colorPrefix = "chart",
}) => {
  const chartConfig = React.useMemo(() => {
    const config: ChartConfig = {};

    data.forEach((item, index) => {
      const formattedName = item.name.split("_").join(" ");
      config[item.name] = {
        label: formattedName.charAt(0).toUpperCase() + formattedName.slice(1),
        color: `hsl(var(--chart-${index + 1}))`,
      };
    });

    // Add a generic value label
    config["value"] = {
      label: "Value",
    };

    return config;
  }, [data, colorPrefix]);

  const enhancedData = React.useMemo(
    () =>
      data.map((item, _index) => ({
        ...item,
        fill: `var(--color-${item.name})`,
      })),
    [data],
  );

  const id = "pie-interactive";

  const { t } = useTranslation();

  return (
    <Card data-chart={id} className="flex flex-col">
      <ChartStyle id={id} config={chartConfig} />
      <CardHeader className="flex-row items-start space-y-0 pb-0">
        <div className="grid gap-1">
          <CardTitle>{description}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 justify-center pb-0">
        <ChartContainer
          id={id}
          config={chartConfig}
          className="mx-auto aspect-square w-full max-w-[300px]"
        >
          <PieChart margin={{ bottom: 20 }}>
            <ChartLegend content={<ChartLegendContent />} />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent hideLabel className="min-w-[150px]" />
              }
            />
            {data.length > 0 && (
              <Pie
                data={enhancedData}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                strokeWidth={5}
              >
                <Label
                  content={({ viewBox }) => {
                    if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                      return (
                        <text
                          x={viewBox.cx}
                          y={viewBox.cy}
                          textAnchor="middle"
                          dominantBaseline="middle"
                        >
                          <tspan
                            x={viewBox.cx}
                            y={viewBox.cy}
                            className="fill-foreground text-3xl font-bold"
                          >
                            {data.reduce((acc, item) => item.value + acc, 0)}
                          </tspan>
                          <tspan
                            x={viewBox.cx}
                            y={(viewBox.cy || 0) + 24}
                            className="fill-muted-foreground"
                          >
                            {t("records.label", {
                              count: data.reduce(
                                (acc, item) => item.value + acc,
                                0,
                              ),
                            })}
                          </tspan>
                        </text>
                      );
                    }
                  }}
                />
              </Pie>
            )}
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
