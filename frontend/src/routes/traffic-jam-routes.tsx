/*
	author: Veronika Šimková (xsimko14)
	file: traffic-jam-routes.tsx
*/

import Navbar from "@/components/traffic-jam-components/navbar";
import Dashboard from "@/pages/traffic-jam-pages/Dashboard";
import FullMap from "@/pages/traffic-jam-pages/FullMap";
import "@/styles/traffic-jams/App.css";
import "@/styles/traffic-jams/layout-styles.scss";
import "@/styles/traffic-jams/responsivity.scss";

import {
  dataContext,
  filterContext,
  routeContext,
  streetContext,
} from "@/utils/traffic-jam-utils/contexts";
import { useDataContext } from "@/utils/traffic-jam-utils/useDataContext";
import { useFilter } from "@/utils/traffic-jam-utils/useFilter";
import { useRouteContext } from "@/utils/traffic-jam-utils/useRouteContext";
import { useStreetContext } from "@/utils/traffic-jam-utils/useStreetContext";
import { Layout } from "antd";
import { Content } from "antd/es/layout/layout";
import { Route, Routes } from "react-router";

export const TrafficJamRoutes = () => {
  const filter = useFilter();
  const street = useStreetContext();
  const data = useDataContext();
  const route = useRouteContext();

  return (
    <Layout>
      <filterContext.Provider value={filter}>
        <streetContext.Provider value={street}>
          <dataContext.Provider value={data}>
            <routeContext.Provider value={route}>
              <Navbar />
              <Layout>
                <Content className="content">
                  <Routes>
                    <Route index element={<FullMap />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                  </Routes>
                </Content>
              </Layout>
            </routeContext.Provider>
          </dataContext.Provider>
        </streetContext.Provider>
      </filterContext.Provider>
    </Layout>
  );
};
