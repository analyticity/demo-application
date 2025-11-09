/*
	author: Veronika Šimková (xsimko14)
	file: data-range-slider.tsx
*/

import { Slider } from "@/components/ui/slider";
import { useConfigStore } from "@/stores/config-store";
import { differenceInDays, format, startOfDay, subYears } from "date-fns";

export const DateRangeSlider = () => {
  const configStore = useConfigStore();

  const today = startOfDay(new Date());

  return (
    <div className="w-full flex gap-x-4 items-center">
      <p className="text-sm">
        {format(configStore.getTimeline().startDate, "dd.MM.yyyy")}
      </p>
      <Slider
        value={configStore.timeline}
        max={differenceInDays(today, subYears(today, configStore.yearRange))}
        step={1}
        onValueChange={(newVal) => configStore.setTimeline(newVal)}
      />
      <p className="text-sm">
        {format(configStore.getTimeline().endDate, "dd.MM.yyyy")}
      </p>
    </div>
  );
};
