"use client";

import { Prediction } from "@/lib/api";
import { motion } from "framer-motion";

export default function PredictionCard({ data }: { data: Prediction }) {
  const isBull = data.direction === "bullish";
  const color = isBull ? "text-orange" : "text-text-muted";
  const glow = isBull
    ? "shadow-[0_0_60px_rgba(232,82,42,0.12)]"
    : "shadow-none";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={`bg-card border border-border rounded-2xl p-10 text-center ${glow}
        hover:border-orange-dim transition-all duration-500`}
    >
      {/* Arrow */}
      <motion.div
        initial={{ y: isBull ? 10 : -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className={`text-6xl ${color} mb-2`}
      >
        {isBull ? "▲" : "▼"}
      </motion.div>

      {/* Direction */}
      <div className={`font-serif text-2xl font-black ${color} mb-1`}>
        {isBull ? "看涨" : "看跌"}
      </div>

      {/* Probability */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="text-5xl font-black tracking-tighter text-text mt-4"
      >
        {(data.ensemble * 100).toFixed(1)}%
      </motion.div>

      <div className="text-[0.65rem] uppercase tracking-[0.2em] text-text-muted mt-3 font-semibold">
        置信度
      </div>

      <div className="text-xs text-text-muted mt-4">
        数据截至 {data.date}
        {data.horizon && ` · 预测 ${data.horizon} 交易日`}
      </div>
    </motion.div>
  );
}
