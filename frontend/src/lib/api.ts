const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface PricePoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceStats {
  last_close: number;
  change_pct: number;
  high_52w: number;
  low_52w: number;
}

export interface Prediction {
  symbol: string;
  date: string;
  direction: "bullish" | "bearish";
  ensemble: number;
  models: Record<string, number>;
  horizon?: number;
}

export interface Metrics {
  [model: string]: {
    accuracy: number;
    auc: number;
    f1: number;
    precision: number;
    recall: number;
  };
}

export interface FeatureItem {
  name: string;
  importance: number;
}

export interface BacktestResult {
  total_return: number;
  bh_total_return: number;
  max_drawdown: number;
  sharpe: number;
  n_trades: number;
  curve: { time: string; strategy: number; buyhold: number }[];
}

export interface SymbolInfo {
  symbol: string;
  name: string;
}

export interface SymbolCategories {
  categories: Record<string, SymbolInfo[]>;
}

export interface ModelStatus {
  symbol: string;
  trained: boolean;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { method: "POST", cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  symbols: () => get<SymbolCategories>("/api/symbols"),
  price: (symbol: string, days = 120) =>
    get<{ data: PricePoint[]; stats: PriceStats }>(`/api/price/${symbol}?days=${days}`),
  predict: (symbol: string, horizon = 10) => get<Prediction>(`/api/predict/${symbol}?horizon=${horizon}`),
  metrics: (symbol: string) => get<Metrics>(`/api/metrics/${symbol}`),
  features: (symbol: string) => get<FeatureItem[]>(`/api/features/${symbol}`),
  backtest: (symbol: string) => get<BacktestResult>(`/api/backtest/${symbol}`),
  modelStatus: (symbol: string) => get<ModelStatus>(`/api/model-status/${symbol}`),
  train: (symbol: string) => post<{ symbol: string; status: string }>(`/api/train/${symbol}`),
};
