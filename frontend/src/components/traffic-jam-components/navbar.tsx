/*
	author: Ing. Magdaléna Ondrušková
	file: navbar.tsx
*/

import "@/index.css";
import {
  FILTER_DEFAULT_VALUE,
  filterContext,
} from "@/utils/traffic-jam-utils/contexts";
import { MenuOutlined } from "@ant-design/icons";
import { Dropdown, MenuProps } from "antd";
import { useContext } from "react";
import { useTranslation } from "react-i18next";
import { Link, NavLink, useSearchParams } from "react-router";
import LanguageSwitcher from "./language-switcher";

function Navbar() {
  const { t, i18n } = useTranslation();

  const [searchParams] = useSearchParams();

  const { filter, setNewFilter } = useContext(filterContext);

  var searchParamsQuery = "";
  if (
    JSON.stringify(filter) !==
      JSON.stringify(FILTER_DEFAULT_VALUE.filterDefaultValue) &&
    filter !== null
  ) {
    searchParamsQuery = `?${searchParams.toString()}`;
  }

  const items: MenuProps["items"] = [
    {
      label: (
        <NavLink
          to={`/traffic-jams/${searchParamsQuery}`}
          className={"navLink"}
          end
        >
          {t("Live Map")}
        </NavLink>
      ),
      key: "0",
    },
    {
      label: (
        <NavLink
          to={`/traffic-jams${searchParamsQuery}`}
          className={"navLink"}
          end
        >
          {t("Dashboard")}
        </NavLink>
      ),
      key: "1",
    },
    {
      type: "divider",
    },
  ];

  return (
    <header className=" flex h-12 w-full items-center justify-between bg-white px-6 py-3 shadow-sm">
      <div className="flex-1 flex font-semibold gap-x-6 pl-5 tracking-wide">
        <Link
          to={"/accidents"}
          className={
            location.pathname.startsWith("/accidents")
              ? "text-[#da2128] hover:text-[#da2128] block"
              : "text-black hover:text-black"
          }
        >
          Accidents
        </Link>
        <Link
          to={"/traffic-jams"}
          className={
            location.pathname.startsWith("/traffic-jams")
              ? "text-[#da2128] hover:text-[#da2128] block"
              : "text-black hover:text-black"
          }
        >
          Traffic jams
        </Link>
      </div>
      <p className="title">{t("app.title")}</p>
      <nav className="flex-1 flex items-center justify-end">
        <NavLink
          to={`/traffic-jams${searchParamsQuery}`}
          className={"navLink"}
          end
        >
          {t("Live Map")}
        </NavLink>
        <NavLink
          to={`/traffic-jams/dashboard${searchParamsQuery}`}
          className={"navLink"}
          end
        >
          {t("Dashboard")}
        </NavLink>
        <LanguageSwitcher i18n={i18n} t={t}></LanguageSwitcher>
        <Dropdown
          menu={{ items, selectable: true, defaultSelectedKeys: ["0"] }}
          trigger={["click"]}
          className="mobile-menu"
          overlayClassName="mobile-menu-overlay"
        >
          <a onClick={(e) => e.preventDefault()}>
            <MenuOutlined />
          </a>
        </Dropdown>
      </nav>
    </header>
  );
}

export default Navbar;
