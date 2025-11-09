/*
	author: Veronika Šimková (xsimko14)
	file: filter-items.tsx
*/

import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useFilterSchema } from "@/hooks/use-filter-schema";
import { cn } from "@/lib/utils";
import { Filter, Operator, useConfigStore } from "@/stores/config-store";
import { Check, ChevronsUpDown, X } from "lucide-react";
import { FC, useState } from "react";

const baseOperators = [
  {
    value: "eq",
    label: "==",
  },
  {
    value: "neq",
    label: "!=",
  },
];

const numericOperators = [
  {
    value: "lt",
    label: "<",
  },
  {
    value: "gt",
    label: ">",
  },
];

export const FilterItem: FC<Filter> = (filterObject) => {
  const configStore = useConfigStore();

  const operators =
    filterObject.attribute_type === "options"
      ? baseOperators
      : baseOperators.concat(numericOperators);

  const { data } = useFilterSchema();
  const [open, setOpen] = useState(false);

  const setValue = (value: string) => {
    if (!data) return;
    const schemaObject = Object.entries(data).find(([key]) => key === value);
    if (!schemaObject) return;

    if (schemaObject[1].type === "options") {
      configStore.updateFilter(filterObject.id, {
        attribute: value,
        options: schemaObject[1].values,
        attribute_type: "options",
        operator: "eq",
      });
    } else {
      configStore.updateFilter(filterObject.id, {
        attribute: value,
        options: [],
        attribute_type: "number",
        value: schemaObject[1].min_val,
      });
    }
  };

  return (
    <div className="w-full py-4 px-2 border border-gray-200 rounded-md flex items-center gap-x-2 flex-wrap gap-y-4">
      <div className="flex items-center gap-x-1 w-full">
        <Button
          className="shrink-0"
          variant={"ghost"}
          size={"icon"}
          onClick={() => configStore.removeFilter(filterObject.id)}
        >
          <X />
        </Button>
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger
            asChild
            role="combobox"
            aria-expanded={open}
            className="w-full capitalize justify-between"
          >
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-full capitalize justify-between"
            >
              <span>
                {filterObject.attribute && data
                  ? Object.entries(data)
                      .find(([name]) => name === filterObject.attribute)?.[0]
                      .split("_")
                      .join(" ")
                  : "Select attribute"}
              </span>

              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[250px] p-0">
            <Command>
              <CommandInput placeholder="Search attribute" />
              <CommandList>
                <CommandEmpty>No attribute found.</CommandEmpty>
                <CommandGroup>
                  {data &&
                    Object.entries(data)
                      .sort((a, b) => a[1].type.localeCompare(b[1].type))
                      .map(([name, _fields]) => (
                        <CommandItem
                          key={name}
                          value={name}
                          className="capitalize"
                          keywords={[name.split("_").join(" "), name]}
                          onSelect={(currentValue) => {
                            setValue(
                              currentValue === filterObject.attribute
                                ? ""
                                : currentValue,
                            );
                            setOpen(false);
                          }}
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              filterObject.attribute === name
                                ? "opacity-100"
                                : "opacity-0",
                            )}
                          />
                          {name.split("_").join(" ")}
                        </CommandItem>
                      ))}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>

      <div className="w-full grid grid-cols-3 gap-x-3">
        {/* operator select */}
        <Select
          value={filterObject.operator}
          onValueChange={(value: Operator) =>
            configStore.updateFilter(filterObject.id, { operator: value })
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select operator" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Operator</SelectLabel>
              {operators.map((operator, i) => (
                <SelectItem key={`attribute-${i}`} value={operator.value}>
                  {operator.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        {/* value select */}
        {filterObject.attribute_type === "options" ? (
          <Select
            value={String(filterObject.value)}
            onValueChange={(value) => {
              configStore.updateFilter(filterObject.id, {
                value: String(value),
              });
            }}
          >
            <SelectTrigger className="w-full col-span-2">
              <SelectValue placeholder="Select value" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Attributes</SelectLabel>
                {filterObject.options.map((attribute, i) => (
                  <SelectItem
                    key={`attribute-${i}`}
                    value={String(attribute)}
                    className="capitalize"
                  >
                    {String(attribute).split("_").join(" ")}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        ) : (
          <Input
            className="col-span-2 w-full"
            type="number"
            value={filterObject.value}
            onChange={(e) => {
              configStore.updateFilter(filterObject.id, {
                value: Number(e.target.value),
              });
            }}
          />
        )}
      </div>
    </div>
  );
};
