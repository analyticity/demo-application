/*
	author: Veronika Šimková (xsimko14)
	file: accident-routes.tsx
*/

import { DateRangeSlider } from "@/components/accident-components/data-range-slider";
import { SiteHeader } from "@/components/accident-components/site-header";
import "@/index.css";
import { ChartPage } from "@/pages/accident-pages/charts-page";
import { HomePage } from "@/pages/accident-pages/home-page";
import { motion } from "framer-motion";
import "leaflet/dist/leaflet.css";
import { Route, Routes } from "react-router";

export const AccidentRoutes = () => {
  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background to-background/95">
      <SiteHeader />
      <Routes>
        <Route path="" Component={HomePage} />
        <Route path="charts" Component={ChartPage} />
      </Routes>
      <motion.div
        initial={{ width: "100px", opacity: 0 }}
        animate={{
          width: "75%",
          opacity: 1,
        }}
        transition={{
          duration: 0.6,
          ease: [0.23, 1, 0.32, 1],
          width: { delay: 0.2 },
        }}
        className="rounded-full border bg-background/80 px-8 backdrop-blur-sm h-12 fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center"
      >
        <DateRangeSlider />
      </motion.div>
    </div>
  );
};
