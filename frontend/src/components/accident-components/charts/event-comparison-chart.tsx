/*
	author: Veronika Šimková (xsimko14)
	file: event-comparison-chart.tsx
*/

import { apiClient } from "@/utils/api";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const EventComparisonChart = () => {
  const { data } = useQuery({
    queryKey: ["charts", "event-comparison"],
    queryFn: async () => {
      const { data } = await apiClient.get<
        Record<
          string,
          {
            police_count: number;
            waze_count: number;
          }
        >
      >("charts/events-by-day");
      const transformed_data = Object.entries(data).map(([key, value]) => {
        return {
          day: key,
          police_count: value.police_count,
          waze_count: value.waze_count,
        };
      });
      return transformed_data;
    },
  });

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="day" tick={{ fontSize: 12 }} />
          <YAxis
            label={{
              value: "Number of Reports",
              angle: -90,
              position: "insideLeft",
              style: { textAnchor: "middle", fontSize: 16 },
            }}
          />
          <Tooltip />
          <Legend />
          <Bar dataKey="police_count" fill="#8884d8" name="Police Reports" />
          <Bar dataKey="waze_count" fill="#82ca9d" name="Waze Reports" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
