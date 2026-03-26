"use client";

import { PriceStats } from "@/lib/api";
import { motion } from "framer-motion";

export default function Hero({
  symbol,
  symbolName,
  stats,
}: {
  symbol: string;
  symbolName: string;
  stats: PriceStats | null;
}) {
  if (!stats) return null;

  const isUp = stats.change_pct >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mb-8"
    >
      <div className="flex items-baseline gap-4 mb-2">
        <h1 className="text-6xl font-black tracking-tighter text-text">
          {symbol}
        </h1>
        <span className="text-sm text-text-muted tracking-wide">
          {symbolName}
        </span>
      </div>
      <div className="flex items-baseline gap-4">
        <span className="text-4xl font-bold tracking-tight text-text">
          ${stats.last_close.toFixed(2)}
        </span>
        <span
          className={`text-lg font-semibold ${
            isUp ? "text-orange" : "text-text-muted"
          }`}
        >
          {isUp ? "+" : ""}
          {stats.change_pct.toFixed(2)}%
        </span>
        <div className="flex-1" />
        <span className="text-xs text-text-muted tracking-widest uppercase">
          52W: ${stats.low_52w.toFixed(0)} — ${stats.high_52w.toFixed(0)}
        </span>
      </div>
    </motion.div>
  );
}
