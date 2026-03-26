"use client";

import { motion } from "framer-motion";

export default function MetricCard({
  label,
  value,
  type = "neutral",
  delay = 0,
  format = "percent",
}: {
  label: string;
  value: number;
  type?: "auto" | "neutral" | "danger";
  delay?: number;
  format?: "percent" | "number";
}) {
  let colorClass: string;
  if (type === "auto") {
    colorClass = value >= 0 ? "text-orange" : "text-text-muted";
  } else if (type === "danger") {
    colorClass = "text-text-muted";
  } else {
    colorClass = "text-text";
  }

  const formatted =
    format === "percent"
      ? `${value >= 0 ? "+" : ""}${(value * 100).toFixed(2)}%`
      : value.toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="bg-card border border-border rounded-2xl p-6
        hover:border-orange-dim/40 hover:shadow-[0_4px_30px_rgba(232,82,42,0.06)]
        transition-all duration-500 group"
    >
      <div className="text-[0.6rem] uppercase tracking-[0.18em] text-text-muted font-semibold mb-3
        group-hover:text-text-dim transition-colors">
        {label}
      </div>
      <div className={`text-3xl font-black tracking-tighter ${colorClass}`}>
        {formatted}
      </div>
    </motion.div>
  );
}
