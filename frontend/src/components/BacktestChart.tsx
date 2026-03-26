"use client";

import {
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Line,
  ComposedChart,
} from "recharts";

interface CurvePoint {
  time: string;
  strategy: number;
  buyhold: number;
}

export default function BacktestChart({ curve }: { curve: CurvePoint[] }) {
  return (
    <div className="w-full h-[300px] bg-card border border-border rounded-2xl p-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={curve}>
          <defs>
            <linearGradient id="strategyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#E8522A" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#E8522A" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="time"
            tick={{ fill: "#555555", fontSize: 10 }}
            axisLine={{ stroke: "#1a1a1a" }}
            tickLine={false}
            tickFormatter={(v) => v.slice(5)}
          />
          <YAxis
            tick={{ fill: "#555555", fontSize: 10 }}
            axisLine={{ stroke: "#1a1a1a" }}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              background: "#111111",
              border: "1px solid #1a1a1a",
              borderRadius: "8px",
              fontSize: "12px",
              color: "#888888",
            }}
            formatter={(value, name) => {
              const label = name === "strategy" ? "ML 策略" : "买入持有";
              const num =
                typeof value === "number"
                  ? value
                  : typeof value === "string"
                    ? Number(value)
                    : Array.isArray(value) && typeof value[0] === "number"
                      ? value[0]
                      : null;

              return [num === null || Number.isNaN(num) ? String(value ?? "") : `${num.toFixed(2)}%`, label];
            }}
          />
          <ReferenceLine y={0} stroke="#222222" strokeDasharray="4 4" />
          <Area
            type="monotone"
            dataKey="strategy"
            stroke="#E8522A"
            strokeWidth={2}
            fill="url(#strategyGrad)"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="buyhold"
            stroke="#555555"
            strokeWidth={1.5}
            strokeDasharray="6 4"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
