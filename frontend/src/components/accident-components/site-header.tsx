/*
	author: Veronika Šimková (xsimko14)
	file: site-header.tsx
*/

import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { PanelRightOpen } from "lucide-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router";
import LanguageSwitcher from "../traffic-jam-components/language-switcher";
import { FilterBuilder } from "./filter-builder";

export function SiteHeader() {
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const [sheetOpen, setSheetOpen] = useState(false);

  const NAV_LINKS = [
    { path: "/accidents", label: t("map") },
    { path: "/accidents/charts", label: "Dashboard" },
  ];

  useEffect(() => {
    setSheetOpen(false);
  }, [location.pathname]);

  return (
    <nav className="sticky top-0 z-50 flex h-12 items-center justify-between px-6 py-3 shadow-sm backdrop-blur-sm bg-white/50">
      <div className="w-full h-full hidden md:flex">
        <div className="flex-1 font-semibold text-sm space-x-4">
          <Link
            to={"/accidents"}
            className={
              location.pathname.startsWith("/accidents") ? "text-[#da2128]" : ""
            }
          >
            {t("accidents")}
          </Link>
          <Link
            to={"/traffic-jams"}
            className={
              location.pathname.startsWith("/traffic-jams")
                ? "text-[#da2128]"
                : ""
            }
          >
            {t("traffic_jams")}
          </Link>
        </div>

        <h1 className="hidden md:block text-xl font-bold text-[#da2128] uppercase">
          {t("nav.title")}
        </h1>

        <div className="flex items-center gap-x-4 font-semibold text-sm flex-1 justify-end">
          <div className="flex space-x-4">
            {NAV_LINKS.map(({ path, label }) => (
              <Link
                key={path}
                to={path}
                className={location.pathname === path ? "text-[#da2128]" : ""}
              >
                {label}
              </Link>
            ))}
          </div>

          <FilterBuilder />
          <LanguageSwitcher i18n={i18n} t={t}></LanguageSwitcher>
        </div>
      </div>
      <div className="flex md:hidden w-full justify-between">
        <h1 className="text-md font-bold text-[#da2128] uppercase">
          {t("nav.title")}
        </h1>
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <SheetTrigger asChild>
            <button>
              <PanelRightOpen className="size-5" />
            </button>
          </SheetTrigger>
          <SheetContent className="flex flex-col py-8 text-black">
            <div className="flex flex-col gap-y-4 mb-6">
              <Link
                to={"/accidents"}
                className={`text-lg font-medium ${
                  location.pathname.startsWith("/accidents")
                    ? "text-[#da2128] font-semibold"
                    : "text-black"
                }`}
              >
                {t("accidents")}
              </Link>
              <Link
                to={"/traffic-jams"}
                className={`text-lg font-medium ${
                  location.pathname.startsWith("/traffic-jams")
                    ? "text-[#da2128] font-semibold"
                    : "text-black"
                }`}
              >
                {t("traffic_jams")}
              </Link>
            </div>
            <div className="h-px bg-gray-200 w-full my-2"></div>
            <div className="flex flex-col mt-6 gap-y-4">
              {NAV_LINKS.map(({ path, label }) => (
                <Link
                  key={path}
                  to={path}
                  className={`text-lg font-medium ${
                    location.pathname === path
                      ? "text-[#da2128] font-semibold"
                      : "text-black"
                  }`}
                >
                  {label}
                </Link>
              ))}
            </div>
            <LanguageSwitcher i18n={i18n} t={t}></LanguageSwitcher>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  );
}
