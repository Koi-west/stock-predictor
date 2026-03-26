"use client";

import { useState, useEffect, useCallback } from "react";
import { api, PricePoint, PriceStats, Prediction, Metrics, FeatureItem, BacktestResult, SymbolInfo } from "@/lib/api";
import Hero from "@/components/Hero";
import CandlestickChart from "@/components/CandlestickChart";
import PredictionCard from "@/components/PredictionCard";
import ModelSignals from "@/components/ModelSignals";
import MetricCard from "@/components/MetricCard";
import BacktestChart from "@/components/BacktestChart";
import FeatureImportance from "@/components/FeatureImportance";
import RadarChartPanel from "@/components/RadarChart";
import SectionHeader from "@/components/SectionHeader";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [categories, setCategories] = useState<Record<string, SymbolInfo[]>>({});
  const [symbol, setSymbol] = useState("QQQ");
  const [days, setDays] = useState(120);
  const [horizon, setHorizon] = useState(10);
  const [priceData, setPriceData] = useState<PricePoint[]>([]);
  const [stats, setStats] = useState<PriceStats | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [features, setFeatures] = useState<FeatureItem[]>([]);
  const [backtest, setBacktest] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingPrice, setLoadingPrice] = useState(true);
  const [modelTrained, setModelTrained] = useState<boolean | null>(null);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load categories on mount
  useEffect(() => {
    api.symbols().then((res) => setCategories(res.categories)).catch(console.error);
  }, []);

  // Get display name for current symbol
  const getSymbolName = useCallback(() => {
    for (const items of Object.values(categories)) {
      const found = items.find((s) => s.symbol === symbol);
      if (found) return found.name;
    }
    return symbol;
  }, [categories, symbol]);

  // Fetch price data
  const fetchPrice = useCallback(async () => {
    setLoadingPrice(true);
    try {
      const res = await api.price(symbol, days);
      setPriceData(res.data);
      setStats(res.stats);
    } catch (e) {
      console.error(e);
    }
    setLoadingPrice(false);
  }, [symbol, days]);

  // Check model status
  const checkModel = useCallback(async () => {
    try {
      const res = await api.modelStatus(symbol);
      setModelTrained(res.trained);
    } catch {
      setModelTrained(false);
    }
  }, [symbol]);

  useEffect(() => {
    fetchPrice();
    checkModel();
    setPrediction(null);
    setMetrics(null);
    setFeatures([]);
    setBacktest(null);
    setError(null);
  }, [fetchPrice, checkModel]);

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    try {
      await api.train(symbol);
      setModelTrained(true);
    } catch (e) {
      setError("训练失败，请检查数据");
      console.error(e);
    }
    setTraining(false);
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const [pred, met, feat, bt] = await Promise.all([
        api.predict(symbol, horizon),
        api.metrics(symbol),
        api.features(symbol),
        api.backtest(symbol),
      ]);
      setPrediction(pred);
      setMetrics(met);
      setFeatures(feat);
      setBacktest(bt);
    } catch (e: any) {
      if (e.message?.includes("404")) {
        setError("请先训练模型");
        setModelTrained(false);
      } else {
        setError("预测失败");
      }
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="flex min-h-screen">
      {/* ── Sidebar ── */}
      <aside className="w-[260px] h-screen bg-surface border-r border-border
        flex flex-col fixed left-0 top-0 overflow-hidden">
        {/* Logo */}
        <div className="text-center py-6 px-6">
          <div className="text-2xl font-black tracking-[0.25em] text-gradient-orange">
            ORACLE
          </div>
          <div className="text-[0.55rem] tracking-[0.3em] text-text-muted uppercase mt-1">
            ML Prediction Engine
          </div>
        </div>

        {/* Symbol selector — scrollable */}
        <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4
          scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
          {Object.entries(categories).map(([cat, items]) => (
            <div key={cat}>
              <div className="text-[0.55rem] uppercase tracking-[0.2em] text-text-muted font-semibold mb-1.5 px-1">
                {cat}
              </div>
              <div className="space-y-1">
                {items.map((s) => (
                  <button
                    key={s.symbol}
                    onClick={() => setSymbol(s.symbol)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium
                      transition-all duration-200 ${
                        symbol === s.symbol
                          ? "bg-orange text-bg font-bold"
                          : "text-text-dim hover:text-text hover:bg-card"
                      }`}
                  >
                    <span className="font-bold">{s.symbol}</span>
                    <span className="ml-1.5 opacity-60 text-[0.65rem]">{s.name}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Controls — fixed bottom */}
        <div className="border-t border-border p-4 space-y-4">
          {/* Days slider */}
          <div>
            <div className="text-[0.55rem] uppercase tracking-[0.2em] text-text-muted font-semibold mb-2">
              时间窗口
            </div>
            <input
              type="range"
              min={30}
              max={500}
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full accent-orange h-1 bg-card rounded-full appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5
                [&::-webkit-slider-thumb]:h-3.5 [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-orange [&::-webkit-slider-thumb]:cursor-pointer"
            />
            <div className="text-[0.65rem] text-text-muted text-center mt-1">{days} 天</div>
          </div>

          {/* Prediction horizon */}
          <div>
            <div className="text-[0.55rem] uppercase tracking-[0.2em] text-text-muted font-semibold mb-2">
              预测周期
            </div>
            <div className="grid grid-cols-3 gap-1">
              {[5, 10, 20].map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className={`py-1.5 rounded-lg text-[0.65rem] font-semibold transition-all duration-200 ${
                    horizon === h
                      ? "bg-orange text-bg"
                      : "bg-card border border-border text-text-dim hover:text-text"
                  }`}
                >
                  {h} 天
                </button>
              ))}
            </div>
          </div>

          {/* Train / Predict buttons */}
          {modelTrained === false && (
            <button
              onClick={handleTrain}
              disabled={training}
              className="w-full py-3 rounded-xl font-bold text-xs uppercase tracking-[0.15em]
                bg-card border border-orange text-orange
                hover:bg-orange hover:text-bg
                transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {training ? "训练中..." : "训练模型"}
            </button>
          )}

          <button
            onClick={handlePredict}
            disabled={loading || !modelTrained}
            className="w-full py-3 rounded-xl font-bold text-xs uppercase tracking-[0.15em]
              bg-orange text-bg
              hover:bg-orange-light hover:shadow-lg hover:shadow-[0_0_20px_rgba(232,82,42,0.15)]
              hover:-translate-y-0.5 active:translate-y-0
              transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "分析中..." : "生成预测"}
          </button>

          {error && (
            <div className="text-[0.65rem] text-orange text-center">{error}</div>
          )}

          <p className="text-[0.55rem] text-text-muted leading-relaxed">
            仅供学习研究，不构成投资建议。
          </p>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main className="ml-[260px] flex-1 p-8 max-w-[1200px]">
        <Hero symbol={symbol} symbolName={getSymbolName()} stats={stats} />

        {/* Chart */}
        {loadingPrice ? (
          <div className="h-[420px] bg-card rounded-xl border border-border animate-pulse" />
        ) : (
          <CandlestickChart data={priceData} />
        )}

        {/* Prediction results */}
        <AnimatePresence>
          {prediction && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              {/* Prediction */}
              <SectionHeader>预测结果</SectionHeader>
              <div className="grid grid-cols-5 gap-6">
                <div className="col-span-2">
                  <PredictionCard data={prediction} />
                </div>
                <div className="col-span-3">
                  <ModelSignals models={prediction.models} />
                </div>
              </div>

              {/* Model Performance */}
              <SectionHeader>模型表现 · 测试集</SectionHeader>
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-card border border-border rounded-2xl p-4">
                  {metrics && <RadarChartPanel metrics={metrics} />}
                </div>
                <div className="bg-card border border-border rounded-2xl p-6 overflow-auto">
                  {metrics && (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-text-muted text-[0.65rem] uppercase tracking-widest">
                          <th className="text-left pb-3 font-semibold">模型</th>
                          <th className="text-right pb-3 font-semibold">Acc</th>
                          <th className="text-right pb-3 font-semibold">AUC</th>
                          <th className="text-right pb-3 font-semibold">F1</th>
                          <th className="text-right pb-3 font-semibold">Prec</th>
                          <th className="text-right pb-3 font-semibold">Rec</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(metrics).map(([name, m]) => (
                          <tr key={name} className="border-t border-border/50 hover:bg-surface/50 transition-colors">
                            <td className="py-3 font-medium text-text-dim">{name}</td>
                            <td className="py-3 text-right text-text-muted">{m.accuracy.toFixed(3)}</td>
                            <td className="py-3 text-right text-text-muted">{m.auc.toFixed(3)}</td>
                            <td className="py-3 text-right text-text-muted">{m.f1.toFixed(3)}</td>
                            <td className="py-3 text-right text-text-muted">{m.precision.toFixed(3)}</td>
                            <td className="py-3 text-right text-text-muted">{m.recall.toFixed(3)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>

              {/* Backtest */}
              {backtest && (
                <>
                  <SectionHeader>回测结果</SectionHeader>
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <MetricCard label="策略收益" value={backtest.total_return} type="auto" delay={0} />
                    <MetricCard label="买入持有" value={backtest.bh_total_return} type="auto" delay={0.1} />
                    <MetricCard label="最大回撤" value={backtest.max_drawdown} type="danger" delay={0.2} />
                    <MetricCard label="夏普比率" value={backtest.sharpe} type="auto" delay={0.3} format="number" />
                  </div>
                  <BacktestChart curve={backtest.curve} />
                </>
              )}

              {/* Feature Importance */}
              {features.length > 0 && (
                <>
                  <SectionHeader>特征重要性 · XGBoost</SectionHeader>
                  <div className="bg-card border border-border rounded-2xl p-6">
                    <FeatureImportance data={features} />
                  </div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty state */}
        {!prediction && !loading && (
          <div className="text-center mt-20">
            <div className="text-6xl text-text-muted/20 font-serif font-black mb-4">◆</div>
            <p className="text-text-muted text-sm">
              {modelTrained === false
                ? "该标的尚未训练模型，请先点击「训练模型」"
                : "选择标的，点击「生成预测」开始分析"}
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
