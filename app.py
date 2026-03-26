"""Stock Predictor — Streamlit Application with premium dark UI."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ── Page config ─────────────────────────────────────────
st.set_page_config(page_title="ORACLE", page_icon="◆", layout="wide")

# ── Design tokens ───────────────────────────────────────
C_BG = "#000000"
C_SURFACE = "#0a0a0a"
C_CARD = "#111111"
C_BORDER = "#1a1a1a"
C_ORANGE = "#D4864A"
C_ORANGE_LIGHT = "#E8A06A"
C_ORANGE_DIM = "#8B5E3C"
C_GREEN = "#2ECC71"
C_RED = "#E74C3C"
C_TEXT = "#F5F5F5"
C_TEXT_DIM = "#888888"
C_TEXT_MUTED = "#555555"

# Plotly layout template
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color=C_TEXT_DIM, size=12),
    xaxis=dict(gridcolor="#1a1a1a", zerolinecolor="#1a1a1a"),
    yaxis=dict(gridcolor="#1a1a1a", zerolinecolor="#1a1a1a"),
    legend=dict(font=dict(color=C_TEXT_DIM)),
    margin=dict(l=50, r=20, t=20, b=30),
)


# ── CSS injection ───────────────────────────────────────
def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Serif+SC:wght@700;900&display=swap');

/* ── Reset Streamlit defaults ── */
.stApp {{
    background-color: {C_BG};
    color: {C_TEXT};
}}

/* Hide Streamlit branding */
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display: none;}}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Noto Serif SC', 'Inter', serif !important;
    color: {C_TEXT} !important;
    font-weight: 900 !important;
    letter-spacing: -0.02em;
}}

h1 {{
    font-size: 3.2rem !important;
    background: linear-gradient(135deg, {C_ORANGE}, {C_ORANGE_LIGHT});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding-bottom: 0 !important;
    line-height: 1.1 !important;
}}

p, span, label, .stMarkdown {{
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: {C_TEXT_DIM};
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {C_SURFACE} !important;
    border-right: 1px solid {C_BORDER} !important;
}}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: {C_TEXT} !important;
    -webkit-text-fill-color: {C_TEXT} !important;
    background: none !important;
    font-size: 1.1rem !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, {C_ORANGE}, {C_ORANGE_DIM}) !important;
    color: {C_BG} !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, {C_ORANGE_LIGHT}, {C_ORANGE}) !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(212, 134, 74, 0.3) !important;
}}

.stButton > button:active {{
    transform: translateY(0);
}}

/* ── Select, Slider, Radio ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {{
    background-color: {C_CARD} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 6px !important;
    color: {C_TEXT} !important;
}}

.stSlider > div > div > div {{
    color: {C_ORANGE} !important;
}}

div[data-baseweb="slider"] div {{
    background-color: {C_ORANGE} !important;
}}

.stRadio > div {{
    gap: 0.5rem;
}}

.stRadio > div > label {{
    background-color: {C_CARD} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 6px !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s ease !important;
}}

.stRadio > div > label[data-checked="true"],
.stRadio > div > label:has(input:checked) {{
    background-color: {C_ORANGE} !important;
    border-color: {C_ORANGE} !important;
    color: {C_BG} !important;
}}

/* ── Metric cards ── */
div[data-testid="stMetric"] {{
    background: linear-gradient(145deg, {C_CARD}, #0d0d0d);
    border: 1px solid {C_BORDER};
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    transition: all 0.3s ease;
}}

div[data-testid="stMetric"]:hover {{
    border-color: {C_ORANGE_DIM};
    box-shadow: 0 4px 20px rgba(212, 134, 74, 0.08);
}}

div[data-testid="stMetric"] label {{
    color: {C_TEXT_MUTED} !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
}}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: {C_TEXT} !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Dataframe ── */
.stDataFrame {{
    border: 1px solid {C_BORDER} !important;
    border-radius: 12px !important;
    overflow: hidden;
}}

/* ── Divider ── */
hr {{
    border-color: {C_BORDER} !important;
    opacity: 0.5;
}}

/* ── Spinner ── */
.stSpinner > div {{
    border-top-color: {C_ORANGE} !important;
}}

/* ── Custom card class ── */
.metric-card {{
    background: linear-gradient(145deg, {C_CARD}, #0d0d0d);
    border: 1px solid {C_BORDER};
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}

.metric-card:hover {{
    border-color: {C_ORANGE_DIM};
    box-shadow: 0 8px 30px rgba(212, 134, 74, 0.06);
    transform: translateY(-2px);
}}

.metric-label {{
    color: {C_TEXT_MUTED};
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
}}

.metric-value {{
    font-size: 2.4rem;
    font-weight: 900;
    font-family: 'Inter', sans-serif;
    line-height: 1;
    letter-spacing: -0.03em;
}}

.metric-value.bullish {{ color: {C_GREEN}; }}
.metric-value.bearish {{ color: {C_RED}; }}
.metric-value.orange {{ color: {C_ORANGE}; }}
.metric-value.neutral {{ color: {C_TEXT}; }}

.section-header {{
    font-family: 'Noto Serif SC', serif;
    font-size: 1.6rem;
    font-weight: 900;
    color: {C_TEXT};
    margin: 2.5rem 0 1.2rem 0;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid {C_BORDER};
    letter-spacing: -0.02em;
}}

.section-header span {{
    color: {C_ORANGE} !important;
    font-family: 'Noto Serif SC', serif !important;
}}

.model-pill {{
    display: inline-block;
    background: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    color: {C_TEXT_DIM};
    font-family: 'Inter', sans-serif;
    margin: 0.2rem;
    font-weight: 500;
}}

.prob-bar {{
    height: 6px;
    border-radius: 3px;
    background: {C_CARD};
    margin-top: 0.4rem;
    overflow: hidden;
}}

.prob-bar-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}}

.subtitle-text {{
    color: {C_TEXT_MUTED};
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    margin-top: -0.5rem;
    margin-bottom: 2rem;
    letter-spacing: 0.02em;
}}

/* ── Tabs styling ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    background: {C_CARD};
    border-radius: 8px;
    padding: 4px;
    border: 1px solid {C_BORDER};
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 6px;
    color: {C_TEXT_DIM};
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    padding: 0.5rem 1.2rem;
}}

.stTabs [aria-selected="true"] {{
    background: {C_ORANGE} !important;
    color: {C_BG} !important;
}}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] {{
    color: {C_TEXT_MUTED} !important;
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background-color: {C_CARD} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 8px !important;
    color: {C_TEXT} !important;
}}

</style>
""", unsafe_allow_html=True)


inject_css()

# ── i18n ────────────────────────────────────────────────
LANG = {
    "en": {
        "title": "ORACLE",
        "subtitle": "Machine Learning Stock Prediction Engine",
        "tagline": "QQQ  /  GOOGL  /  PLTR  ·  Next ~2 Weeks",
        "settings": "CONTROL PANEL",
        "select_symbol": "TARGET",
        "chart_days": "TIMEFRAME",
        "models": "MODELS",
        "generate": "PREDICT",
        "disclaimer": "For educational and research purposes only. Not investment advice.",
        "price_chart": "Price Action",
        "price_axis": "Price ($)",
        "volume_axis": "Volume",
        "prediction_title": "Prediction",
        "direction_label": "DIRECTION",
        "ensemble_prob": "CONFIDENCE",
        "data_as_of": "DATA AS OF",
        "model_breakdown": "Model Signals",
        "col_model": "Model",
        "col_bullish_prob": "Bullish Prob",
        "model_perf": "Model Performance",
        "backtest_title": "Backtest",
        "strategy_return": "STRATEGY",
        "buyhold_return": "BUY & HOLD",
        "max_drawdown": "MAX DRAWDOWN",
        "sharpe_ratio": "SHARPE",
        "feature_importance": "Feature Importance",
        "importance_axis": "Importance",
        "return_axis": "Return (%)",
        "ml_strategy": "ML Strategy",
        "buy_hold": "Buy & Hold",
        "spinner_predict": "Analyzing market signals...",
        "spinner_backtest": "Simulating trades...",
        "bullish": "BULLISH",
        "bearish": "BEARISH",
        "lang_toggle": "LANG",
        "test_set": "Test Set",
    },
    "zh": {
        "title": "ORACLE",
        "subtitle": "机器学习股票预测引擎",
        "tagline": "QQQ  /  GOOGL  /  PLTR  ·  未来约两周",
        "settings": "控制面板",
        "select_symbol": "标的",
        "chart_days": "时间窗口",
        "models": "模型",
        "generate": "生成预测",
        "disclaimer": "仅供学习研究，不构成投资建议。",
        "price_chart": "价格走势",
        "price_axis": "价格 ($)",
        "volume_axis": "成交量",
        "prediction_title": "预测结果",
        "direction_label": "方向",
        "ensemble_prob": "置信度",
        "data_as_of": "数据截至",
        "model_breakdown": "各模型信号",
        "col_model": "模型",
        "col_bullish_prob": "看涨概率",
        "model_perf": "模型表现",
        "backtest_title": "回测结果",
        "strategy_return": "策略收益",
        "buyhold_return": "买入持有",
        "max_drawdown": "最大回撤",
        "sharpe_ratio": "夏普比率",
        "feature_importance": "特征重要性",
        "importance_axis": "重要性",
        "return_axis": "收益率 (%)",
        "ml_strategy": "ML 策略",
        "buy_hold": "买入持有",
        "spinner_predict": "分析市场信号中...",
        "spinner_backtest": "模拟交易中...",
        "bullish": "看涨",
        "bearish": "看跌",
        "lang_toggle": "语言",
        "test_set": "测试集",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "zh")
    return LANG[lang].get(key, key)


# ── Config ──────────────────────────────────────────────
SYMBOLS = ["QQQ", "GOOGL", "PLTR"]
SYMBOL_NAMES = {"QQQ": "Nasdaq 100 ETF", "GOOGL": "Google", "PLTR": "Palantir"}
MODEL_DIR = Path("models")
DATA_DIR = Path("data")


@st.cache_data(ttl=3600)
def load_price_data(symbol: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{symbol}.csv", index_col=0, parse_dates=True)


@st.cache_resource
def load_model_result(symbol: str) -> dict:
    return joblib.load(MODEL_DIR / f"{symbol}_models.pkl")


def get_prediction(symbol: str) -> dict:
    result = load_model_result(symbol)
    models = result["models"]
    weights = result["weights"]
    scaler = result["scaler"]

    from src.features import build_features
    X, _ = build_features(symbol)
    X_latest = X.iloc[[-1]]
    X_scaled = scaler.transform(X_latest)

    predictions = {}
    for name, model in models.items():
        predictions[name] = model.predict_proba(X_scaled)[:, 1][0]

    ensemble_proba = sum(weights[n] * predictions[n] for n in models)
    predictions["Ensemble"] = ensemble_proba

    return {
        "date": X_latest.index[0].strftime("%Y-%m-%d"),
        "predictions": predictions,
        "ensemble": ensemble_proba,
        "direction": "bullish" if ensemble_proba > 0.5 else "bearish",
    }


def get_backtest(symbol: str) -> dict:
    from src.backtest import run_backtest
    return run_backtest(symbol)


# ── Chart functions ─────────────────────────────────────

def plot_candlestick(df: pd.DataFrame, symbol: str, n_days: int = 120):
    df_plot = df.tail(n_days)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.78, 0.22], vertical_spacing=0.03,
    )

    # Candlestick with orange/copper theme
    fig.add_trace(go.Candlestick(
        x=df_plot.index, open=df_plot["Open"], high=df_plot["High"],
        low=df_plot["Low"], close=df_plot["Close"], name="Price",
        increasing_line_color=C_ORANGE, increasing_fillcolor=C_ORANGE,
        decreasing_line_color="#444444", decreasing_fillcolor="#2a2a2a",
    ), row=1, col=1)

    # SMA with subtle colors
    for window, color, dash in [(20, C_ORANGE_DIM, None), (50, C_TEXT_MUTED, "dot")]:
        sma = df_plot["Close"].rolling(window).mean()
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=sma, name=f"SMA {window}",
            line=dict(width=1.2, color=color, dash=dash),
        ), row=1, col=1)

    # Volume bars
    colors = [C_ORANGE if c >= o else "#333333"
              for c, o in zip(df_plot["Close"], df_plot["Open"])]
    fig.add_trace(go.Bar(
        x=df_plot.index, y=df_plot["Volume"], name=t("volume_axis"),
        marker_color=colors, opacity=0.4, showlegend=False,
    ), row=2, col=1)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=520, xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", y=1.06, font=dict(color=C_TEXT_DIM, size=11)),
    )
    fig.update_xaxes(gridcolor="#111111", showgrid=False)
    fig.update_yaxes(title_text=t("price_axis"), row=1, col=1,
                     gridcolor="#111111", title_font=dict(size=11))
    fig.update_yaxes(title_text="", row=2, col=1, gridcolor="#111111")

    return fig


def plot_backtest(bt: dict):
    pf = bt["portfolio_values"]
    bh = bt["buy_hold_values"]

    pf_norm = (pf["value"] / pf["value"].iloc[0] - 1) * 100
    bh_norm = (bh["value"] / bh["value"].iloc[0] - 1) * 100

    fig = go.Figure()

    # Fill area under strategy curve
    fig.add_trace(go.Scatter(
        x=pf_norm.index, y=pf_norm, name=t("ml_strategy"),
        line=dict(color=C_ORANGE, width=2.5),
        fill="tozeroy", fillcolor="rgba(212, 134, 74, 0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=bh_norm.index, y=bh_norm, name=t("buy_hold"),
        line=dict(color=C_TEXT_MUTED, width=1.5, dash="dot"),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#222222", line_width=1)

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=350,
        yaxis_title=t("return_axis"),
        legend=dict(orientation="h", y=1.08),
    )
    fig.update_xaxes(showgrid=False)

    return fig


def plot_feature_importance(symbol: str, top_n: int = 12):
    result = load_model_result(symbol)
    models = result["models"]
    feature_names = result["feature_names"]

    xgb_model = models.get("XGBoost")
    if xgb_model is None or not hasattr(xgb_model, "feature_importances_"):
        return None

    fi = pd.Series(xgb_model.feature_importances_, index=feature_names).nlargest(top_n)

    # Gradient colors from orange to dim
    n = len(fi)
    colors = [f"rgba(212, 134, 74, {0.3 + 0.7 * (n - i) / n})" for i in range(n)]

    fig = go.Figure(go.Bar(
        x=fi.values, y=fi.index, orientation="h",
        marker_color=colors,
        marker_line=dict(width=0),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        xaxis_title=t("importance_axis"),
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False)

    return fig


def plot_model_radar(metrics: dict):
    """Radar chart comparing models."""
    categories = ["Accuracy", "AUC", "F1", "Precision", "Recall"]
    fig = go.Figure()

    model_colors = {
        "RandomForest": C_TEXT_MUTED,
        "XGBoost": C_ORANGE,
        "LightGBM": C_ORANGE_DIM,
        "Ensemble": C_ORANGE_LIGHT,
    }

    for name, m in metrics.items():
        values = [m["accuracy"], m["auc"], m["f1"], m["precision"], m["recall"]]
        values.append(values[0])  # close the polygon
        cats = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=values, theta=cats, name=name,
            line=dict(color=model_colors.get(name, C_TEXT_DIM), width=2),
            fill="toself",
            fillcolor=f"rgba(212, 134, 74, 0.05)" if name == "Ensemble" else "rgba(0,0,0,0)",
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor="#1a1a1a", linecolor="#1a1a1a",
                tickfont=dict(size=10, color=C_TEXT_MUTED),
            ),
            angularaxis=dict(
                gridcolor="#1a1a1a", linecolor="#1a1a1a",
                tickfont=dict(size=11, color=C_TEXT_DIM),
            ),
        ),
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


# ── Custom HTML components ──────────────────────────────

def render_hero(symbol: str, df: pd.DataFrame):
    """Hero section with key stats."""
    last_close = df["Close"].iloc[-1]
    prev_close = df["Close"].iloc[-2]
    change = (last_close / prev_close - 1) * 100
    change_color = C_GREEN if change >= 0 else C_RED
    sign = "+" if change >= 0 else ""

    high_52w = df["Close"].tail(252).max()
    low_52w = df["Close"].tail(252).min()

    st.markdown(f"""
<div style="display: flex; align-items: baseline; gap: 1.5rem; margin-bottom: 0.5rem;">
    <div style="font-family: 'Inter', sans-serif; font-size: 3.5rem; font-weight: 900;
                color: {C_TEXT}; letter-spacing: -0.04em; line-height: 1;">{symbol}</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 400;
                color: {C_TEXT_MUTED}; letter-spacing: 0.02em;">{SYMBOL_NAMES.get(symbol, "")}</div>
</div>
<div style="display: flex; align-items: baseline; gap: 1.2rem; margin-bottom: 2rem;">
    <div style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 700;
                color: {C_TEXT}; letter-spacing: -0.02em;">${last_close:.2f}</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 1.1rem; font-weight: 600;
                color: {change_color};">{sign}{change:.2f}%</div>
    <div style="flex: 1;"></div>
    <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; color: {C_TEXT_MUTED};
                letter-spacing: 0.1em; text-transform: uppercase;">
        52W: ${low_52w:.0f} — ${high_52w:.0f}
    </div>
</div>
""", unsafe_allow_html=True)


def render_prediction_card(pred: dict):
    """Big prediction display."""
    direction_key = pred["direction"]
    direction_text = t(direction_key)
    prob = pred["ensemble"]
    prob_pct = f"{prob:.1%}"
    color = C_GREEN if direction_key == "bullish" else C_RED
    arrow = "&#9650;" if direction_key == "bullish" else "&#9660;"

    st.markdown(f"""
<div class="metric-card" style="text-align: center; padding: 3rem 2rem;">
    <div style="font-size: 4rem; color: {color}; line-height: 1; margin-bottom: 0.5rem;">
        {arrow}
    </div>
    <div style="font-family: 'Noto Serif SC', serif; font-size: 2rem; font-weight: 900;
                color: {color}; margin-bottom: 0.3rem; letter-spacing: -0.02em;">
        {direction_text}
    </div>
    <div style="font-family: 'Inter', sans-serif; font-size: 3.5rem; font-weight: 900;
                color: {C_TEXT}; letter-spacing: -0.04em; line-height: 1.1;">
        {prob_pct}
    </div>
    <div class="metric-label" style="margin-top: 0.8rem;">{t("ensemble_prob")}</div>
    <div style="color: {C_TEXT_MUTED}; font-size: 0.8rem; margin-top: 1rem;
                font-family: 'Inter', sans-serif;">
        {t("data_as_of")}: {pred["date"]}
    </div>
</div>
""", unsafe_allow_html=True)


def render_model_signal(name: str, prob: float):
    """Individual model signal bar."""
    pct = prob * 100
    color = C_GREEN if prob > 0.55 else (C_RED if prob < 0.45 else C_ORANGE)

    st.markdown(f"""
<div style="display: flex; align-items: center; gap: 1rem; margin: 0.6rem 0;
            padding: 0.8rem 1rem; background: {C_CARD}; border-radius: 8px;
            border: 1px solid {C_BORDER};">
    <div style="font-family: 'Inter', sans-serif; font-size: 0.8rem; font-weight: 600;
                color: {C_TEXT_DIM}; min-width: 110px; letter-spacing: 0.02em;">{name}</div>
    <div style="flex: 1;">
        <div class="prob-bar">
            <div class="prob-bar-fill" style="width: {pct}%; background: linear-gradient(90deg, {color}, {C_ORANGE});"></div>
        </div>
    </div>
    <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 700;
                color: {color}; min-width: 50px; text-align: right;">{prob:.1%}</div>
</div>
""", unsafe_allow_html=True)


def render_section_header(text: str, accent_word: str = ""):
    """Section header with optional accent."""
    if accent_word and accent_word in text:
        parts = text.split(accent_word, 1)
        html = f'{parts[0]}<span>{accent_word}</span>{parts[1]}'
    else:
        html = text
    st.markdown(f'<div class="section-header">{html}</div>', unsafe_allow_html=True)


# ── Main App ────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

# ── Sidebar ──
with st.sidebar:
    st.markdown(f"""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <div style="font-family: 'Inter', sans-serif; font-size: 1.5rem; font-weight: 900;
                color: {C_ORANGE}; letter-spacing: 0.2em;">ORACLE</div>
    <div style="font-family: 'Inter', sans-serif; font-size: 0.6rem; color: {C_TEXT_MUTED};
                letter-spacing: 0.3em; text-transform: uppercase; margin-top: 0.2rem;">
        ML PREDICTION ENGINE</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    # Language toggle
    lang_options = {"zh": "中文", "en": "EN"}
    current_lang = st.session_state["lang"]
    selected_lang = st.radio(
        t("lang_toggle"),
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=0 if current_lang == "zh" else 1,
        horizontal=True,
    )
    if selected_lang != current_lang:
        st.session_state["lang"] = selected_lang
        st.rerun()

    st.markdown("")
    symbol = st.selectbox(t("select_symbol"), SYMBOLS, index=0,
                          format_func=lambda x: f"{x}  ·  {SYMBOL_NAMES[x]}")
    chart_days = st.slider(t("chart_days"), 30, 500, 120)

    model_options = ["RandomForest", "XGBoost", "LightGBM", "Ensemble"]
    selected_models = st.multiselect(t("models"), model_options, default=["Ensemble"])

    st.markdown("")
    run_predict = st.button(t("generate"), type="primary", use_container_width=True)

    st.markdown("")
    st.caption(t("disclaimer"))


# ── Main content ──
df = load_price_data(symbol)

# Hero
render_hero(symbol, df)

# Price chart
st.plotly_chart(plot_candlestick(df, symbol, chart_days), use_container_width=True)

# Prediction
if run_predict:
    with st.spinner(t("spinner_predict")):
        pred = get_prediction(symbol)

    render_section_header(t("prediction_title"))

    col_pred, col_signals = st.columns([1, 1.5])

    with col_pred:
        render_prediction_card(pred)

    with col_signals:
        st.markdown(f"""
<div class="metric-label" style="margin-bottom: 0.8rem; margin-top: 0.5rem;">
    {t("model_breakdown")}
</div>
""", unsafe_allow_html=True)
        for name, prob in pred["predictions"].items():
            if name != "Ensemble":
                render_model_signal(name, prob)

    # Model Performance
    render_section_header(f'{t("model_perf")} · {t("test_set")}')

    result = load_model_result(symbol)

    col_radar, col_table = st.columns([1, 1])

    with col_radar:
        radar_fig = plot_model_radar(result["metrics"])
        st.plotly_chart(radar_fig, use_container_width=True)

    with col_table:
        metrics_data = []
        for name, m in result["metrics"].items():
            metrics_data.append({
                t("col_model"): name,
                "Accuracy": f"{m['accuracy']:.3f}",
                "AUC": f"{m['auc']:.3f}",
                "F1": f"{m['f1']:.3f}",
                "Precision": f"{m['precision']:.3f}",
                "Recall": f"{m['recall']:.3f}",
            })
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True, hide_index=True)

    # Backtest
    render_section_header(t("backtest_title"))

    with st.spinner(t("spinner_backtest")):
        bt = get_backtest(symbol)

    if "error" not in bt:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            val = bt["total_return"]
            color_cls = "bullish" if val >= 0 else "bearish"
            st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">{t("strategy_return")}</div>
    <div class="metric-value {color_cls}">{val:+.2%}</div>
</div>""", unsafe_allow_html=True)
        with c2:
            val = bt["bh_total_return"]
            color_cls = "bullish" if val >= 0 else "bearish"
            st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">{t("buyhold_return")}</div>
    <div class="metric-value {color_cls}">{val:+.2%}</div>
</div>""", unsafe_allow_html=True)
        with c3:
            val = bt["max_drawdown"]
            st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">{t("max_drawdown")}</div>
    <div class="metric-value bearish">{val:.2%}</div>
</div>""", unsafe_allow_html=True)
        with c4:
            val = bt["sharpe"]
            color_cls = "bullish" if val > 0 else "bearish"
            st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">{t("sharpe_ratio")}</div>
    <div class="metric-value {color_cls}">{val:.2f}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        st.plotly_chart(plot_backtest(bt), use_container_width=True)

    # Feature importance
    render_section_header(t("feature_importance"))
    fi_fig = plot_feature_importance(symbol)
    if fi_fig:
        st.plotly_chart(fi_fig, use_container_width=True)
