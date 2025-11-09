/*
	author: Veronika Šimková (xsimko14)
	file: accident-marker.tsx
*/

import { cn } from "@/lib/utils";
import { AlertTriangle, Car, Navigation, PersonStanding } from "lucide-react";
import { FC } from "react";

type AccidentMarkerProps = {
  accident: Accident;
  selected: boolean;
};

type WazeReportMarkerProps = {
  accident: WazeReport;
  selected: boolean;
};

export const AccidentMarker: FC<AccidentMarkerProps> = ({
  accident,
  selected,
}) => {
  const accidentTypes = {
    pedestrian: {
      icon: PersonStanding,
      color: "bg-blue-500 text-white border-blue-700",
    },
    fatal: {
      icon: AlertTriangle,
      color: "bg-red-600 text-white border-red-800",
    },
    minor: {
      icon: Car,
      color: "bg-gray-500 text-white border-gray-700",
    },
  };

  const accidentType = accident.attributes.charakter
    ? accident.attributes.charakter === "pouze_hmotna_skoda"
      ? accidentTypes.minor
      : accidentTypes.fatal
    : accidentTypes.pedestrian;

  return (
    <div
      className={cn(
        "flex items-center group border justify-center size-6 rounded-full shadow-md transition-all duration-150",
        selected ? "scale-150" : "",
        accidentType.color,
      )}
    >
      <accidentType.icon className="size-3" />
    </div>
  );
};

export const WazeReportMarker: FC<WazeReportMarkerProps> = ({ selected }) => {
  return (
    <div
      className={cn(
        "flex items-center group border justify-center size-6 rounded-full shadow-md transition-all duration-150 bg-[#05c8f7]",
        selected ? "scale-150" : "",
      )}
    >
      <Navigation className="size-3" />
    </div>
  );
};
