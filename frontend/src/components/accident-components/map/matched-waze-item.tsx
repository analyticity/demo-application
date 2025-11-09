/*
	author: Veronika Šimková (xsimko14)
	file: matched-waze-item.tsx
*/

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useWazeHoverStore } from "@/stores/waze-hover-store";
import { formatDate, formatTimeDelta } from "@/utils/utils";
import { Calendar, InfoIcon } from "lucide-react";
import { FC } from "react";

type matchedWazeItemProps = {
  wazeReport: MatchedWazeReport;
};

export const MatchedWazeItem: FC<matchedWazeItemProps> = ({ wazeReport }) => {
  const { setHoveredWazeId } = useWazeHoverStore();

  return (
    <TooltipProvider>
      <div
        className="w-full rounded-md p-2 flex justify-between items-center border-b hover:bg-gray-100"
        onMouseEnter={() => setHoveredWazeId(wazeReport.uuid)}
        onMouseLeave={() => setHoveredWazeId(null)}
      >
        <div>
          <div className="flex items-center gap-x-2 text-muted-foreground">
            <div className="flex items-center gap-x-1">
              <Calendar className="size-4" />
              <span className="text-sm text-primary">
                {formatDate(wazeReport.published_at, "dd.MM.yy, HH:mm")}
              </span>
            </div>
            <div className="size-1 rounded-full bg-muted-foreground"></div>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex text-sm gap-x-1 items-center">
                  <InfoIcon className="size-4" />
                  <p className="text-primary">
                    {(wazeReport.match_score * 100).toFixed(2)}
                  </p>
                </div>
              </TooltipTrigger>
              <TooltipContent className="max-w-[250px]">
                <span className="font-semibold">Match Score</span>
                <p>Weighted score combining distance and time proximity.</p>
              </TooltipContent>
            </Tooltip>
          </div>
          <div className="flex items-center gap-x-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <p className="mt-2 text-sm">
                  <span className="text-muted-foreground text-xs">
                    Distance:{" "}
                  </span>
                  {wazeReport.match_distance.toFixed(1)} m
                </p>
              </TooltipTrigger>
              <TooltipContent className="max-w-[250px]">
                <span className="font-semibold">Distance</span>
                <p>
                  Physical distance between Waze and police report locations.
                </p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <p className="mt-2 text-sm">
                  <span className="text-muted-foreground text-xs">
                    Time delta:{" "}
                  </span>
                  {formatTimeDelta(wazeReport.match_time_diff)}
                </p>
              </TooltipTrigger>
              <TooltipContent className="max-w-[250px]">
                <span className="font-semibold">Time Difference</span>
                <p>Time elapsed between Waze report and police record.</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
};
