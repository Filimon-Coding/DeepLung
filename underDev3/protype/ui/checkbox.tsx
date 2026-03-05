import React from "react";

type Props = {
  id?: string;
  checked?: boolean;
  onCheckedChange?: (v: boolean) => void;
};

export function Checkbox({ id, checked = false, onCheckedChange }: Props) {
  return (
    <input
      id={id}
      type="checkbox"
      checked={checked}
      onChange={(e) => onCheckedChange?.(e.target.checked)}
      className="w-4 h-4"
    />
  );
}