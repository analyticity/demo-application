/*
	author: Veronika Šimková (xsimko14)
	file: filter-builder.tsx
*/

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useConfigStore } from "@/stores/config-store";
import { FilterIcon } from "lucide-react";
import { FC } from "react";
import { useTranslation } from "react-i18next";
import { FilterItem } from "./filters/filter-items";

export const FilterBuilder: FC = () => {
  const configStore = useConfigStore();
  const { t } = useTranslation();

  return (
    <Sheet modal={true}>
      <SheetTrigger>
        <FilterIcon className="size-4" />
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>{t("filter.title")}</SheetTitle>
          <SheetDescription>{t("filter.description")}</SheetDescription>
        </SheetHeader>
        <div className="mt-4 space-y-6">
          {configStore.filters.map((filter) => {
            return <FilterItem {...filter} key={filter.id} />;
          })}
        </div>
        <Button onClick={() => configStore.addDefaultFilter()} className="mt-8">
          {t("filter.new")}
          <FilterIcon />
        </Button>
      </SheetContent>
    </Sheet>
  );
};
