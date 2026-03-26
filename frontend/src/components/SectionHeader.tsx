"use client";

import { motion } from "framer-motion";

export default function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <motion.h2
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="font-serif text-2xl font-black text-text mt-12 mb-6 pb-3
        border-b border-border tracking-tight"
    >
      {children}
    </motion.h2>
  );
}
