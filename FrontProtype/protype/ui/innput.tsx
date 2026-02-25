import React from "react";

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={[
        "w-full rounded bg-slate-100 px-4 py-3 text-sm",
        "outline-none border border-transparent focus:border-slate-300",
        props.className ?? "",
      ].join(" ")}
    />
  );
}