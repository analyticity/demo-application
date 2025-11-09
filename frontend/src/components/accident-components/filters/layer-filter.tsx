/*
	author: Veronika Šimková (xsimko14)
	file: layer-filter.tsx
*/

import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLayerStore } from "@/stores/layer-store";
import { ListFilter } from "lucide-react";

export const LayerFilter = () => {
  const { activeFilters, toggleFilter } = useLayerStore();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="absolute top-8 right-10 bg-secondary/80 backdrop-blur-sm p-2 rounded-md">
        <ListFilter className="size-5" />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuLabel>View Options</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuCheckboxItem
          checked={activeFilters.heatmap}
          onCheckedChange={() => toggleFilter("heatmap")}
        >
          Heatmap View
        </DropdownMenuCheckboxItem>

        <DropdownMenuSeparator />
        <DropdownMenuLabel>Event Types</DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuCheckboxItem
          checked={activeFilters.police}
          onCheckedChange={() => toggleFilter("police")}
        >
          Police events
        </DropdownMenuCheckboxItem>
        <DropdownMenuCheckboxItem
          checked={activeFilters.waze}
          onCheckedChange={() => toggleFilter("waze")}
        >
          Waze reports
        </DropdownMenuCheckboxItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
