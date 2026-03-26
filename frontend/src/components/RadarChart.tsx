"use client";

import {
  Radar,
  RadarChart as ReRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Metrics } from "@/lib/api";

const MODEL_COLORS: Record<string, string> = {
  RandomForest: "#555555",
  XGBoost: "#E8522A",
  LightGBM: "#A83A1E",
  Ensemble: "#FF6B3D",
};

export default function RadarChartPanel({ metrics }: { metrics: Metrics }) {
  const dimensions = ["accuracy", "auc", "f1", "precision", "recall"];
  const labels: Record<string, string> = {
    accuracy: "Accuracy",
    auc: "AUC",
    f1: "F1",
    precision: "Precision",
    recall: "Recall",
  };

  const data = dimensions.map((dim) => {
    const point: Record<string, string | number> = { metric: labels[dim] };
    for (const [model, vals] of Object.entries(metrics)) {
      point[model] = vals[dim as keyof typeof vals];
    }
    return point;
  });

  return (
    <div className="w-full h-[350px]">
      <ResponsiveContainer width="100%" height="100%">
        <ReRadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="#1a1a1a" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "#888888", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 1]}
            tick={{ fill: "#555555", fontSize: 9 }}
            axisLine={false}
          />
          {Object.keys(metrics).map((model) => (
            <Radar
              key={model}
              name={model}
              dataKey={model}
              stroke={MODEL_COLORS[model] || "#888"}
              fill={MODEL_COLORS[model] || "#888"}
              fillOpacity={model === "Ensemble" ? 0.1 : 0.02}
              strokeWidth={model === "Ensemble" ? 2 : 1.5}
            />
          ))}
          <Legend
            wrapperStyle={{ fontSize: "11px", color: "#888" }}
          />
        </ReRadarChart>
      </ResponsiveContainer>
    </div>
  );
}
