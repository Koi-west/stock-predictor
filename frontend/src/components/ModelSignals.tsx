"use client";

import { motion } from "framer-motion";

export default function ModelSignals({
  models,
}: {
  models: Record<string, number>;
}) {
  const entries = Object.entries(models).filter(([name]) => name !== "Ensemble");

  return (
    <div className="space-y-3">
      <div className="text-[0.65rem] uppercase tracking-[0.2em] text-text-muted font-semibold mb-4">
        各模型信号
      </div>
      {entries.map(([name, prob], i) => {
        const pct = prob * 100;
        const color =
          prob > 0.55 ? "#E8522A" : prob < 0.45 ? "#555555" : "#888888";

        return (
          <motion.div
            key={name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 * i }}
            className="flex items-center gap-4 p-4 bg-card rounded-xl border border-border
              hover:border-orange-dim/50 transition-all duration-300"
          >
            <span className="text-sm font-semibold text-text-dim min-w-[120px] tracking-wide">
              {name}
            </span>
            <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 1, delay: 0.3 + 0.1 * i, ease: "easeOut" }}
                className="h-full rounded-full"
                style={{
                  background: `linear-gradient(90deg, ${color}, #E8522A)`,
                }}
              />
            </div>
            <span
              className="text-base font-bold min-w-[55px] text-right"
              style={{ color }}
            >
              {(prob * 100).toFixed(1)}%
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
