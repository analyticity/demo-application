/*
	author: Veronika Šimková (xsimko14)
	file: accident-detail-card.tsx
*/

import { CopyButton } from "@/components/accident-components/copy-button";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import { useWazeReports } from "@/hooks/use-waze-reports";
import { cn } from "@/lib/utils";
import {
  formatAttributeValue,
  formatDate,
  getSeverityTypeColor,
  isWazeReport,
} from "@/utils/utils";
import { formatDistanceToNow } from "date-fns";
import {
  AlertOctagon,
  AlertTriangle,
  Calendar,
  Car,
  Clock,
  GlassWater,
  MapPin,
  MoreVerticalIcon,
  X,
} from "lucide-react";
import { FC, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { AccidentDetailModal } from "./accident-detail-modal";
import { MatchedWazeItem } from "./matched-waze-item";
import { WazeDetailCard } from "./waze-detail-card";

type AccidentCardProps = {
  selectedAccident: Accident | WazeReport;
  setSelectedAccident: (accident: Accident | null) => void;
};

export const AccidentDetailCard: FC<AccidentCardProps> = ({
  selectedAccident,
  setSelectedAccident,
}) => {
  const [showMatchedWaze, setShowMatchedWaze] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const { data: WazeReports } = useWazeReports();

  const { t } = useTranslation();

  useEffect(() => {
    const hidePanel = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelectedAccident(null);
    };

    window.addEventListener("keydown", hidePanel);

    return () => {
      window.removeEventListener("keydown", hidePanel);
    };
  }, []);

  useEffect(() => {
    setShowMatchedWaze(false);
  }, [selectedAccident]);

  if (isWazeReport(selectedAccident)) {
    return (
      <WazeDetailCard
        selectedAccident={selectedAccident}
        setSelectedAccident={setSelectedAccident}
      />
    );
  }

  const handleExportJson = () => {
    const jsonData = JSON.stringify(selectedAccident, null, 2);
    const blob = new Blob([jsonData], { type: "application/json" });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `accident-${selectedAccident.attributes.id_nehody}.json`;
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <Card className="absolute left-4 top-1/2 -translate-y-1/2 w-[380px] bg-background/90 rounded-2xl">
        <CardHeader className="pb-0">
          <CardTitle className="flex justify-between items-center">
            <div className="bg-blue-200 px-3 rounded-full text-xs py-1 text-blue-600">
              #{selectedAccident.attributes.id_nehody}
            </div>
            <button onClick={() => setSelectedAccident(null)}>
              <X className="size-4" />
            </button>
          </CardTitle>
          <CardDescription className="pt-2 flex flex-col items-center gap-y-3">
            <div className="w-full flex flex-col space-y-1">
              <div className="flex items-center w-full justify-between">
                <h3 className="text-primary text-2xl font-bold">
                  {t("accident.detail_title")}
                </h3>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button size={"icon"} variant={"ghost"}>
                      <MoreVerticalIcon />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-40">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => setShowDetailModal(true)}>
                      <span>Show details</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleExportJson}>
                      <span>Export as JSON</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <div className="flex gap-x-2 items-center">
                {selectedAccident.attributes.datum && (
                  <span>
                    {formatDistanceToNow(selectedAccident.attributes.datum)} ago
                  </span>
                )}
                <div className="size-1 rounded-full bg-muted-foreground"></div>
                <button
                  disabled={
                    selectedAccident.attributes.waze_matches_count === 0
                  }
                  className={cn(
                    selectedAccident.attributes.waze_matches_count > 0 &&
                      "hover:underline",
                  )}
                  onClick={() => setShowMatchedWaze((prev) => !prev)}
                >
                  {showMatchedWaze ? (
                    <span>{t("accident.show_detail")}</span>
                  ) : (
                    <span>
                      {selectedAccident.attributes.waze_matches_count}{" "}
                      {t("accident.matched_waze", {
                        count: selectedAccident.attributes.waze_matches_count,
                      })}
                    </span>
                  )}
                </button>
              </div>
            </div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Separator className="mt-3" />
          <div className="overflow-y-auto h-[53dvh] 2xl:h-[46dvh] mt-3">
            {showMatchedWaze ? (
              <>
                <div className="flex flex-col gap-y-2">
                  {WazeReports &&
                    (WazeReports as MatchedWazeReport[])
                      .filter((wazeReport) =>
                        selectedAccident.attributes.matched_waze.includes(
                          wazeReport.uuid,
                        ),
                      )
                      .sort((a, b) => b.match_score - a.match_score)
                      .map((wazeReport) => (
                        <MatchedWazeItem
                          wazeReport={wazeReport}
                          key={wazeReport.uuid}
                        />
                      ))}
                </div>
              </>
            ) : (
              <>
                <div className="grid grid-cols-1 gap-4">
                  <div className="flex items-start space-x-3">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <MapPin size={18} className="text-primary" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.location")}
                      </h3>
                      <div className="flex items-center gap-x-3">
                        <div>
                          <p className="text-sm text-muted-foreground break-all">
                            {selectedAccident.geometry.y}
                          </p>
                          <p className="text-sm text-muted-foreground break-all">
                            {selectedAccident.geometry.x}
                          </p>
                        </div>
                        <CopyButton
                          className="[&>*]:size-3 text-muted-foreground p-2 rounded-md hover:bg-gray-100"
                          textToCopy={`${selectedAccident.geometry.y}, ${selectedAccident.geometry.x}`}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="bg-indigo-100 p-2 rounded-full">
                      <Calendar size={18} className="text-indigo-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.date")}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(selectedAccident.attributes.datum)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="bg-purple-100 p-2 rounded-full">
                      <Clock size={18} className="text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.time")}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {selectedAccident.attributes.cas ?? "Unknown"}
                      </p>
                    </div>
                  </div>
                </div>
                <Separator className="my-5" />
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div
                      className={cn(
                        "p-2 rounded-full",
                        getSeverityTypeColor(
                          selectedAccident.attributes.charakter ?? "",
                        ),
                      )}
                    >
                      <AlertTriangle size={18} className="text-white" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.severity")}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatAttributeValue(
                          selectedAccident.attributes.charakter,
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="bg-teal-100 p-2 rounded-full">
                      <Car size={18} className="text-teal-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.vehicle_type")}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatAttributeValue(
                          selectedAccident.attributes.druh_vozidla,
                        )}
                      </p>
                    </div>
                  </div>

                  {selectedAccident.attributes.hlavni_pricina && (
                    <div className="flex items-start space-x-3">
                      <div className="bg-red-100 p-2 rounded-full">
                        <AlertOctagon size={18} className="text-red-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-medium">
                          {t("accident.main_cause")}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {formatAttributeValue(
                            selectedAccident.attributes.hlavni_pricina,
                          )}
                        </p>
                      </div>
                    </div>
                  )}
                  <div className="flex items-start space-x-3">
                    <div className="bg-orange-100 p-2 rounded-full">
                      <GlassWater size={18} className="text-orange-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium">
                        {t("accident.alcohol_involved")}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatAttributeValue(
                          selectedAccident.attributes.alkohol,
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
      {showDetailModal && (
        <AccidentDetailModal
          accident={selectedAccident}
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
        />
      )}
    </>
  );
};
