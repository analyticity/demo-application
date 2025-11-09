/*
	author: Veronika Šimková (xsimko14)
	file: language-switcher.tsx
*/

// components/LanguageSwitcher.tsx
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Globe } from "lucide-react";
import { useTranslation } from "react-i18next";

const LanguageSwitcher = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (language: string) => {
    i18n.changeLanguage(language);
  };

  // Mapping of language codes to their full names
  const languages = {
    en: t("language.english"),
    sk: t("language.slovak"),
    cs: t("language.czech"),
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <Globe size={16} />
          <span>{languages[i18n.language] || languages.en}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>{t("language.select")}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup
          value={i18n.language}
          onValueChange={changeLanguage}
        >
          <DropdownMenuRadioItem value="en">
            {t("language.english")}
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="sk">
            {t("language.slovak")}
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="cs">
            {t("language.czech")}
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LanguageSwitcher;
