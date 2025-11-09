/*
	author: Veronika Šimková (xsimko14)
	file: accident-detail-modal.tsx
*/

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download } from "lucide-react";
import { FC } from "react";
import { useTranslation } from "react-i18next";

type AccidentDetailModalProps = {
  accident: Accident;
  isOpen: boolean;
  onClose: () => void;
};

export const AccidentDetailModal: FC<AccidentDetailModalProps> = ({
  accident,
  isOpen,
  onClose,
}) => {
  const { t } = useTranslation();

  const handleExportJson = () => {
    const jsonData = JSON.stringify(accident, null, 2);
    const blob = new Blob([jsonData], { type: "application/json" });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `accident-${accident.attributes.id_nehody}.json`;
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
        <DialogHeader className="flex flex-row items-center justify-between">
          <DialogTitle className="text-xl">
            {t("accident.detail_title")}
          </DialogTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleExportJson}
            title={t("accident.export_json")}
          >
            <Download className="size-4" />
          </Button>
        </DialogHeader>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/3">Property</TableHead>
              <TableHead>Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium">1. Longitude</TableCell>
              <TableCell>{accident.geometry.x}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="font-medium">2. Latitude</TableCell>
              <TableCell>{accident.geometry.y}</TableCell>
            </TableRow>
            {Object.entries(accident.attributes).map(([key, value], i) => (
              <TableRow key={key}>
                <TableCell className="font-medium">
                  {i + 3}. {key.split("_").join(" ")}
                </TableCell>
                <TableCell>
                  {value === null || value === undefined ? "-" : value}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DialogContent>
    </Dialog>
  );
};
