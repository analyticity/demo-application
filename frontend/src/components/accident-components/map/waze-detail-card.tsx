/*
	author: Veronika Šimková (xsimko14)
	file: waze-detail-card.tsx
*/

import { CopyButton } from "@/components/accident-components/copy-button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useWazeStore } from "@/stores/waze-cache-store";
import { useWazeHoverStore } from "@/stores/waze-hover-store";
import { formatDate, formatTimeDelta } from "@/utils/utils";
import { differenceInMinutes, formatDistanceToNow } from "date-fns";
import {
  Calendar,
  Clock,
  MapPin,
  ThumbsUp,
  TrafficCone,
  X,
} from "lucide-react";
import { FC, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

type wazeDetailCardProps = {
  selectedAccident: WazeReport;
  setSelectedAccident: (accident: Accident | null) => void;
};

export const WazeDetailCard: FC<wazeDetailCardProps> = ({
  selectedAccident,
  setSelectedAccident,
}) => {
  const [showMatched, setShowMatched] = useState(false);
  const { t } = useTranslation();
  const { setHoveredWazeId } = useWazeHoverStore();
  const wazeStore = useWazeStore();

  const matchedOccurences = selectedAccident.related_reports.length;

  useEffect(() => {
    setShowMatched(false);
  }, [selectedAccident]);

  const relatedReports = selectedAccident.related_reports
    .filter((uuid) => uuid !== selectedAccident.uuid) // Exclude the selected accident itself
    .map((uuid) => wazeStore.getReportById(uuid))
    .filter(Boolean);

  return (
    <Card className="absolute left-4 top-1/2 -translate-y-1/2 w-[380px] bg-background/90 rounded-2xl">
      <CardHeader className="pb-0">
        <CardTitle className="flex justify-between items-center">
          <div className="bg-blue-200 px-3 rounded-full text-xs py-1 text-blue-600">
            <div>{selectedAccident.uuid}</div>
          </div>

          <button onClick={() => setSelectedAccident(null)}>
            <X className="size-4" />
          </button>
        </CardTitle>
        <CardDescription className="pt-2 flex flex-col items-center gap-y-3">
          <div className="w-full flex flex-col space-y-1">
            <h3 className="text-primary text-2xl font-bold">
              Waze Event Detail
            </h3>
            <div className="flex gap-x-2 items-center">
              {selectedAccident.published_at && (
                <span>
                  {formatDistanceToNow(selectedAccident.published_at)} ago
                </span>
              )}
              <div className="size-1 rounded-full bg-muted-foreground"></div>
              <button
                onClick={() => setShowMatched((prev) => !prev)}
                disabled={matchedOccurences < 2}
                className="disable:hover:none hover:underline"
              >
                Nahlašeno {matchedOccurences} krát
              </button>
            </div>
          </div>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Separator className={showMatched ? "mt-5" : "my-5"} />
        {showMatched ? (
          <div className="min-h-[320px]">
            {relatedReports
              .filter((report) => report !== undefined)
              .map((report) => (
                <TooltipProvider>
                  <div
                    key={report.uuid}
                    className="w-full rounded-md p-2 flex justify-between items-center border-b hover:bg-gray-100"
                    onMouseEnter={() => {
                      setHoveredWazeId(report.uuid);
                    }}
                    onMouseLeave={() => setHoveredWazeId(null)}
                  >
                    <div>
                      <div className="flex items-center gap-x-2 text-muted-foreground">
                        <div className="flex items-center gap-x-1">
                          <Calendar className="size-4" />
                          <span className="text-sm text-primary">
                            {formatDate(report.published_at)}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-x-2">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="mt-2 text-sm">
                              <span className="text-muted-foreground text-xs">
                                Distance:{" "}
                              </span>
                              {report.distance_to_primary.toFixed(1)} m
                            </p>
                          </TooltipTrigger>
                          <TooltipContent className="max-w-[250px]">
                            <span className="font-semibold">Distance</span>
                            <p>
                              Physical distance between the estimated Waze
                              location and reported alert locations.
                            </p>
                          </TooltipContent>
                        </Tooltip>

                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="mt-2 text-sm">
                              <span className="text-muted-foreground text-xs">
                                Time delta:{" "}
                              </span>
                              {formatTimeDelta(
                                differenceInMinutes(
                                  report.published_at,
                                  selectedAccident.published_at,
                                ),
                              )}
                            </p>
                          </TooltipTrigger>
                          <TooltipContent className="max-w-[250px]">
                            <span className="font-semibold">
                              Time Difference
                            </span>
                            <p>
                              Time elapsed between Waze report and estimated
                              time of accident.
                            </p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                    </div>
                  </div>
                </TooltipProvider>
              ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-4">
              <div className="flex items-start space-x-3">
                <div className="bg-blue-100 p-2 rounded-full">
                  <MapPin size={18} className="text-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-medium">{t("waze.location")}</h3>
                  <div className="flex items-center gap-x-3">
                    <div>
                      <p className="text-sm text-muted-foreground break-all">
                        {selectedAccident.y}
                      </p>
                      <p className="text-sm text-muted-foreground break-all">
                        {selectedAccident.x}
                      </p>
                    </div>
                    <CopyButton
                      className="[&>*]:size-3 text-muted-foreground p-2 rounded-md hover:bg-gray-100"
                      textToCopy={`${selectedAccident.y}, ${selectedAccident.x}`}
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-indigo-100 p-2 rounded-full">
                  <Calendar size={18} className="text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium">{t("waze.date")}</h3>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(selectedAccident.published_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="bg-purple-100 p-2 rounded-full">
                  <Clock size={18} className="text-purple-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium">{t("waze.time")}</h3>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(selectedAccident.published_at, "HH:mm")}
                  </p>
                </div>
              </div>
            </div>
            <Separator className="my-5" />
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className={cn("p-2 rounded-full bg-orange-100")}>
                  <TrafficCone size={18} className="text-orange-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium">{t("waze.road_type")}</h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedAccident.roadTypeName}
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className={cn("p-2 rounded-full bg-green-100")}>
                  <ThumbsUp size={18} className="text-green-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium">
                    {t("waze.reliability")}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedAccident.reliability}/10
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
