import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "solid" | "outline";
};

export function Button({ variant = "solid", className = "", ...props }: Props) {
  const base =
    "inline-flex items-center justify-center rounded font-bold tracking-widest transition-opacity disabled:opacity-50 disabled:cursor-not-allowed";
  const solid = "bg-[#1f3b63] text-white hover:opacity-90";
  const outline = "border border-[#1f3b63] text-[#1f3b63] bg-white hover:opacity-80";

  const style = variant === "outline" ? outline : solid;

  return <button className={`${base} ${style} ${className}`} {...props} />;
}