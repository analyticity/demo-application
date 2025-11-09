// i18n.js - Configuration file
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import csTranslation from "@/locales/cs.json";
import enTranslation from "@/locales/en.json";
import skTranslation from "@/locales/sk.json";

const resources = {
  en: {
    translation: enTranslation,
  },
  cs: {
    translation: csTranslation,
  },
  sk: {
    translation: skTranslation,
  },
};

// Configure i18n
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  });

export default i18n;
