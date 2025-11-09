/*
	author: Ing. Magdaléna Ondrušková
	file: StatsTileComplet.tsx
*/

import { get_data_delay_alerts } from "@/utils/traffic-jam-utils/backendApiRequests";
import {
  dataContext,
  filterContext,
  routeContext,
  streetContext,
} from "@/utils/traffic-jam-utils/contexts";
import * as Icons from "@/utils/traffic-jam-utils/icons";
import { getXMinDate } from "@/utils/traffic-jam-utils/util";
import { Spin } from "antd";
import { useContext, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import StatsTile from "./StatsTile";

type Props = {
  isDashboard?: boolean;
};

const StatsTilesComplet = ({ isDashboard }: Props) => {
  const { t } = useTranslation();
  const { filter } = useContext(filterContext);

  const [dataLoading, setDataLoading] = useState<boolean>(false);

  const {
    jamsData,
    alertData,
    levelData,
    speedData,
    lengthData,
    timeData,
    dateTimeFrom,
    dateTimeTo,
    setLengthData,
    setLevelData,
    setSpeedData,
    setTimeData,
    setDateTimeFrom,
    setDateTimeTo,
    setPreviousDate,
    setJamsData,
    setAlertData,
    setXAxisData,
  } = useContext(dataContext);

  const { route } = useContext(routeContext);
  const { streetsInRoute } = useContext(streetContext);

  useEffect(() => {
    if (!filter) {
      return;
    }

    setDataLoading(true);
    const get_data = async () => {
      const response = await get_data_delay_alerts(
        filter,
        route,
        streetsInRoute,
      );

      if (!response) return;

      setJamsData(response.jams);
      setAlertData(response.alerts);
      setXAxisData(response.xaxis);
      setSpeedData(response.speedKMH);
      setTimeData(response.time);
      setLevelData(response.level);
      setLengthData(response.length);
      setDataLoading(false);
    };

    setDateTimeFrom(`${filter.fromDate}`);
    setDateTimeTo(`${filter.toDate}`);
    setPreviousDate(getXMinDate(filter?.toDate));

    get_data();
  }, [filter]);

  return (
    <div className={isDashboard ? "dashboard-top-row-stats" : ""}>
      <Spin tip={t("loading.data")} size="large" spinning={dataLoading}>
        <StatsTile
          icon={<Icons.WarningIcon />}
          tileTitle={new Intl.NumberFormat("cs-CZ").format(
            alertData?.reduce((sum, attribute) => sum + attribute, 0),
          )}
          tileType={t("tile.ActiveAlerts")}
        ></StatsTile>
        <StatsTile
          icon={<Icons.CarIcon />}
          tileTitle={new Intl.NumberFormat("cs-CZ").format(
            jamsData?.reduce((sum, attribute) => sum + attribute, 0),
          )}
          tileType={t("tile.TrafficJams")}
        ></StatsTile>
        <StatsTile
          icon={<Icons.SpeedIcon />}
          tileTitle={new Intl.NumberFormat("pt-PT", {
            style: "unit",
            unit: "kilometer-per-hour",
          }).format(
            Number(
              (
                speedData?.reduce((sum, attribute) => sum + attribute, 0) /
                jamsData?.length
              ).toFixed(2),
            ),
          )}
          tileType={t("tile.AverageSpeed")}
        ></StatsTile>
        <StatsTile
          icon={<Icons.CarIcon />}
          tileTitle={new Intl.NumberFormat("cs-CZ", {
            style: "unit",
            unit: "kilometer",
          }).format(lengthData?.reduce((sum, attribute) => sum + attribute, 0))}
          tileType={t("tile.JamsLength")}
        ></StatsTile>

        <StatsTile
          icon={<Icons.JamDelayIcon />}
          tileTitle={new Intl.NumberFormat("cs-CZ", {
            style: "unit",
            unit: "hour",
          }).format(
            timeData?.reduce((sum, attribute) => sum + attribute, 0) / 60,
          )}
          tileType={t("tile.JamsDelay")}
        ></StatsTile>

        <StatsTile
          icon={<Icons.JamLevelIcon />}
          tileTitle={(
            levelData?.reduce((sum, attribute) => sum + attribute, 0) /
            jamsData?.length
          ).toFixed(2)}
          tileType={t("tile.AverageJamLevel")}
        ></StatsTile>
      </Spin>
    </div>
  );
};

export default StatsTilesComplet;
