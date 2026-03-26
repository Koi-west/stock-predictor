"use client";

import { FeatureItem } from "@/lib/api";
import { motion } from "framer-motion";

export default function FeatureImportance({ data }: { data: FeatureItem[] }) {
  if (!data.length) return null;
  const maxVal = data[0].importance;

  return (
    <div className="space-y-2">
      {data.map((item, i) => {
        const pct = (item.importance / maxVal) * 100;
        const opacity = 0.3 + 0.7 * ((data.length - i) / data.length);

        return (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.03 * i }}
            className="flex items-center gap-3 group"
          >
            <span className="text-xs text-text-dim font-mono min-w-[130px] text-right
              group-hover:text-text-muted transition-colors">
              {item.name}
            </span>
            <div className="flex-1 h-5 bg-surface rounded overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.8, delay: 0.05 * i, ease: "easeOut" }}
                className="h-full rounded"
                style={{
                  backgroundColor: `rgba(232, 82, 42, ${opacity})`,
                }}
              />
            </div>
            <span className="text-xs font-mono text-text-muted min-w-[45px]">
              {item.importance.toFixed(3)}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
