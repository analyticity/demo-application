/*
	author: Veronika Šimková (xsimko14)
	file: utils.ts
*/

import { format } from "date-fns";

export function isAccident(report: Accident | WazeReport): report is Accident {
  return (report as Accident).geometry !== undefined;
}

export function isWazeReport(
  report: Accident | WazeReport,
): report is WazeReport {
  return (report as WazeReport).is_primary !== undefined;
}

export const formatDate = (
  date?: string,
  dateFormat: string = "dd MMMM yyyy (EEEE)",
) => {
  if (!date) {
    return "Unknown";
  }
  const date_object = new Date(date);

  return format(date_object, dateFormat);
};

export const formatAttributeValue = (value: string | undefined | null) => {
  if (!value) return "Unknown";

  const joinedValue = value.split("_").join(" ");

  return joinedValue.slice(0, 1).toLocaleUpperCase() + joinedValue.slice(1);
};

export const getSeverityTypeColor = (value: string) => {
  if (value === "pouze_hmotna_skoda") {
    return "bg-amber-500";
  }
  return "bg-red-500";
};

export const formatTimeDelta = (minutesDiff: number): string => {
  if (minutesDiff < 60) {
    return `${minutesDiff.toFixed(1)} min`;
  } else {
    const hours = Math.floor(minutesDiff / 60);
    const minutes = Math.round(minutesDiff % 60);
    return minutes > 0 ? `${hours} h ${minutes} min` : `${hours} h`;
  }
};

export const formatLargeNumber = (num: number | string) => {
  if (num === null || num === undefined) return "0";

  const numValue =
    typeof num === "string" ? parseFloat(num.replace(/[^\d.-]/g, "")) : num;

  if (isNaN(numValue)) return "0";

  if (numValue >= 1000000000000) {
    return (numValue / 1000000000000).toFixed(1).replace(/\.0$/, "") + "T";
  }
  if (numValue >= 1000000000) {
    return (numValue / 1000000000).toFixed(1).replace(/\.0$/, "") + "B";
  }
  if (numValue >= 1000000) {
    return (numValue / 1000000).toFixed(1).replace(/\.0$/, "") + "M";
  }
  if (numValue >= 1000) {
    return (numValue / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  }

  return numValue.toLocaleString();
};
