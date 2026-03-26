"use client";

import { useEffect, useRef } from "react";
import { createChart, IChartApi, ColorType, CandlestickSeries, LineSeries, HistogramSeries } from "lightweight-charts";
import { PricePoint } from "@/lib/api";

export default function CandlestickChart({ data }: { data: PricePoint[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#555555",
        fontFamily: "KingHwa OldSong, Inter, -apple-system, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#111111" },
        horzLines: { color: "#111111" },
      },
      crosshair: {
        vertLine: { color: "#E8522A", width: 1, style: 2, labelBackgroundColor: "#E8522A" },
        horzLine: { color: "#E8522A", width: 1, style: 2, labelBackgroundColor: "#E8522A" },
      },
      rightPriceScale: {
        borderColor: "#1a1a1a",
      },
      timeScale: {
        borderColor: "#1a1a1a",
        timeVisible: false,
      },
      width: containerRef.current.clientWidth,
      height: 420,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#E8522A",
      downColor: "#333333",
      borderUpColor: "#E8522A",
      borderDownColor: "#444444",
      wickUpColor: "#E8522A",
      wickDownColor: "#444444",
    });

    candleSeries.setData(
      data.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
    );

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    volumeSeries.setData(
      data.map((d) => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? "rgba(232,82,42,0.3)" : "rgba(51,51,51,0.5)",
      }))
    );

    const sma20 = computeSMA(data.map((d) => d.close), 20);
    const sma20Series = chart.addSeries(LineSeries, {
      color: "rgba(255,255,255,0.25)",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    sma20Series.setData(
      sma20
        .map((val, i) => ({ time: data[i].time, value: val }))
        .filter((d): d is { time: string; value: number } => d.value !== null)
    );

    const sma50 = computeSMA(data.map((d) => d.close), 50);
    const sma50Series = chart.addSeries(LineSeries, {
      color: "rgba(255,255,255,0.12)",
      lineWidth: 1,
      lineStyle: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });
    sma50Series.setData(
      sma50
        .map((val, i) => ({ time: data[i].time, value: val }))
        .filter((d): d is { time: string; value: number } => d.value !== null)
    );

    chart.timeScale().fitContent();
    chartRef.current = chart;

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [data]);

  return (
    <div
      ref={containerRef}
      className="w-full rounded-xl border border-border bg-surface/50 p-2"
    />
  );
}

function computeSMA(prices: number[], period: number): (number | null)[] {
  return prices.map((_, i) => {
    if (i < period - 1) return null;
    const slice = prices.slice(i - period + 1, i + 1);
    return slice.reduce((a, b) => a + b, 0) / period;
  });
}
