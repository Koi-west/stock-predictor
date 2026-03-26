"""Central configuration for stock predictor."""

# ── Symbol Categories ────────────────────────────────────

SYMBOL_CATEGORIES = {
    "美股科技": {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "GOOGL": "Alphabet",
        "AMZN": "Amazon",
        "META": "Meta",
        "NVDA": "Nvidia",
        "TSLA": "Tesla",
        "PLTR": "Palantir",
    },
    "指数": {
        "QQQ": "Nasdaq 100",
    },
    "中概股": {
        "BILI": "Bilibili",
        "BIDU": "Baidu",
        "BABA": "Alibaba",
        "PDD": "Pinduoduo",
        "JD": "JD.com",
    },
    "港股": {
        "3690.HK": "美团",
        "0700.HK": "腾讯",
        "1810.HK": "小米",
        "1024.HK": "快手",
        "2513.HK": "智谱 AI",
        "0100.HK": "MiniMax",
    },
    "加密货币": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
    },
    "能源": {
        "NEE": "NextEra Energy",
        "DUK": "Duke Energy",
        "NRGV": "Energy Vault",
    },
    "存储 / 半导体": {
        "MU": "Micron",
        "WDC": "Western Digital",
        "STX": "Seagate",
    },
    "黄金": {
        "GLD": "SPDR Gold",
    },
}

# Flat list of all symbols (for data fetching)
SYMBOLS = []
SYMBOL_NAMES = {}
for _cat, _items in SYMBOL_CATEGORIES.items():
    for _sym, _name in _items.items():
        SYMBOLS.append(_sym)
        SYMBOL_NAMES[_sym] = _name

# Macro / cross-asset tickers (fetched for feature engineering)
MACRO_TICKERS = {
    "VIX": "^VIX",
    "TLT": "TLT",   # 20-year Treasury bond ETF
    "UUP": "UUP",   # US Dollar Index ETF
    "SPY": "SPY",   # S&P 500 (for relative strength)
}

# Data parameters
DATA_START = "2021-01-01"
DATA_DIR = "data"
MODEL_DIR = "models"

# Feature parameters
SMA_WINDOWS = [5, 10, 20, 50]
EMA_WINDOWS = [12, 26]
RSI_WINDOW = 14
ATR_WINDOW = 14
BB_WINDOW = 20
VOLUME_MA_WINDOW = 20

# Target: forward return horizon (trading days)
FORWARD_DAYS = 10  # ~2 weeks

# Train/val/test split dates
TRAIN_END = "2025-06-30"
VAL_END = "2025-12-31"
# Test: everything after VAL_END

# Model hyperparameter search iterations
N_SEARCH_ITER = 50
