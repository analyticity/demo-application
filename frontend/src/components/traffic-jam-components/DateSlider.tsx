
import { colorRed } from '@/utils/traffic-jam-utils/constants';
import { filterContext } from '@/utils/traffic-jam-utils/contexts';
import { Slider, SliderSingleProps } from 'antd';
import dayjs from 'dayjs';
import React, { useContext, useEffect, useRef, useState } from 'react';
// import { colorRed } from '../utils/traffic-jam-utils/constants';
// import { filterContext } from '../utils/traffic-jam-utils/contexts';

type RangeValues = { startValue: number; endValue: number };

const JAN_START = dayjs('2025-01-01');
const JAN_END = dayjs('2025-01-31');
const MAX_INDEX = JAN_END.diff(JAN_START, 'day'); // 30

const defaultValues = {
  defaultStartDate: JAN_START,
  defaultEndDate: JAN_END,
  defaultStartValue: 0,
  defaultEndValue: MAX_INDEX, // celý mesiac
};

const DateSlider = () => {
  const { filter, setNewFilter } = useContext(filterContext);

  // 1) defaultne vybraný celý mesiac (0..30)
  const [value, setValue] = useState<RangeValues>({
    startValue: defaultValues.defaultStartValue,
    endValue: defaultValues.defaultEndValue,
  });

  const initialized = useRef(false);

  const marks: SliderSingleProps['marks'] = {
    0: { style: { color: colorRed }, label: <strong>{JAN_START.format('DD.MM.YYYY')}</strong> },
    [MAX_INDEX]: { style: { color: colorRed }, label: <strong>{JAN_END.format('DD.MM.YYYY')}</strong> },
  };

  const handleChange = (val: number[]) =>
    setValue({ startValue: val[0], endValue: val[1] });

  // 2) Pri prvom mount-e (alebo ak filter ešte nemá dátumy) nastav celý mesiac
  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;

      // ak už filter má dátumy, premietni ich do slidera
      if (filter?.fromDate && filter?.toDate) {
        const from = dayjs(filter.fromDate);
        const to = dayjs(filter.toDate);
        const startIdx = Math.max(0, Math.min(MAX_INDEX, from.diff(JAN_START, 'day')));
        const endIdx = Math.max(startIdx, Math.min(MAX_INDEX, to.diff(JAN_START, 'day')));
        setValue({ startValue: startIdx, endValue: endIdx });
      } else {
        // inak default: celý január
        setNewFilter(prev => ({
          ...prev,
          fromDate: JAN_START.format('YYYY-MM-DD'),
          toDate: JAN_END.format('YYYY-MM-DD'),
        }));
        setValue({ startValue: 0, endValue: MAX_INDEX });
      }
      return;
    }

    // ak sa filter mení neskôr (napr. zvonku), zosúľaď slider
    if (filter?.fromDate && filter?.toDate) {
      const from = dayjs(filter.fromDate);
      const to = dayjs(filter.toDate);
      const startIdx = Math.max(0, Math.min(MAX_INDEX, from.diff(JAN_START, 'day')));
      const endIdx = Math.max(startIdx, Math.min(MAX_INDEX, to.diff(JAN_START, 'day')));
      setValue({ startValue: startIdx, endValue: endIdx });
    }
  }, [filter, setNewFilter]);

  return (
    <div style={{ width: '95%', margin: 'auto' }}>
      <Slider
        range={{ draggableTrack: false }}
        marks={marks}
        min={defaultValues.defaultStartValue} // 0
        max={defaultValues.defaultEndValue}   // 30
        step={1}
        value={[value.startValue, value.endValue]}
        onChange={handleChange}
        className="date-slider"
        tooltip={{
          formatter: (v?: number) =>
            v !== undefined ? JAN_START.add(v, 'day').format('DD.MM.YYYY') : '',
        }}
        onChangeComplete={(val: number[]) => {
          const [startIdx, endIdx] = val;
          const from = JAN_START.add(startIdx, 'day');
          const to = JAN_START.add(endIdx, 'day');

          // “clamp” pre istotu v rámci januára
          const clampedFrom = from.isBefore(JAN_START) ? JAN_START : from;
          const clampedTo = to.isAfter(JAN_END) ? JAN_END : to;

          setNewFilter(prev => ({
            ...prev,
            fromDate: clampedFrom.format('YYYY-MM-DD'),
            toDate: clampedTo.format('YYYY-MM-DD'),
          }));
        }}
      />
    </div>
  );
};

export default DateSlider;