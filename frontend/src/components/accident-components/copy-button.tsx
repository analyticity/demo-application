/*
	author: Veronika Šimková (xsimko14)
	file: copy-button.tsx
*/

import { cn } from "@/lib/utils";
import { Check, Copy } from "lucide-react";
import { FC, useState } from "react";

type CopyButtonProps = {
  className?: string;
  textToCopy: string;
};

export const CopyButton: FC<CopyButtonProps> = ({ textToCopy, className }) => {
  const [isSuccess, setIsSuccess] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(textToCopy);
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };
  return (
    <button className={cn(className)} onClick={handleCopy}>
      {isSuccess ? <Check /> : <Copy />}
    </button>
  );
};
