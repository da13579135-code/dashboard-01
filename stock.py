import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import feedparser
import urllib.parse
from dataclasses import dataclass

st.set_page_config(page_title="AI Infrastructure Terminal", layout="wide")

# -----------------------------
# CONFIGURATION
# -----------------------------
@dataclass
class Config:
    history_period: str = "2y"
    forecast_days: int = 180
    simulations: int = 500
    confidence_level: float = 0.80
    trading_days_per_year: int = 252

CFG = Config()

# -----------------------------
# FORMATTING
# -----------------------------
def format_money(x: float | None) -> str:
    if x is None:
        return "N/A"
    if x >= 1e12:
        return f"${x / 1e12:.2f}T"
    if x >= 1e9:
        return f"${x / 1e9:.2f}B"
    if x >= 1e6:
        return f"${x / 1e6:.2f}M"
    return f"${x:,.0f}"

def format_percent(x: float | None) -> str:
    return "N/A" if x is None else f"{x * 100:.1f}%"

# -----------------------------
# DATA LOADING
# -----------------------------
@st.cache_data(ttl=300)  # 5-minute TTL for price data
def load_history(ticker: str) -> pd.DataFrame | None:
    try:
        df = yf.Ticker(ticker).history(period=CFG.history_period)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Failed to load {ticker}: {e}")
        return None

@st.cache_data(ttl=60)  # 1-minute TTL for live info
def load_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------
POSITIVE_WORDS = {"beat", "beats", "growth", "strong", "surge", "record", "outperform", "profit", "bullish"}
NEGATIVE_WORDS = {"miss", "misses", "weak", "loss", "decline", "downgrade", "bearish", "slump", "warning"}

def compute_sentiment(items: list) -> tuple[float, int]:
    """Returns normalized sentiment score (-1 to 1) and article count."""
    if not items:
        return 0.0, 0
    
    total_score = 0
    for item in items:
        text = (item.title + " " + getattr(item, "summary", "")).lower()
        pos = sum(word in text for word in POSITIVE_WORDS)
        neg = sum(word in text for word in NEGATIVE_WORDS)
        total_score += pos - neg
    
    # Normalize to [-1, 1] range
    max_possible = len(items) * max(len(POSITIVE_WORDS), len(NEGATIVE_WORDS))
    normalized = total_score / max_possible if max_possible > 0 else 0
    return np.clip(normalized, -1, 1), len(items)

def display_news(company_name: str, ticker: str) -> float:
    """Fetches and displays news, returns sentiment score."""
    query = urllib.parse.quote_plus(f"{company_name} {ticker} stock")
    url = f"[news.google.com](https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en)"
    
    try:
        feed = feedparser.parse(url)
        items = feed.entries[:5]
    except Exception:
        return 0.0
    
    if not items:
        return 0.0
    
    sentiment_score, count = compute_sentiment(items)
    
    # Sentiment indicator
    if sentiment_score > 0.1:
        indicator = "🟢 Positive"
    elif sentiment_score < -0.1:
        indicator = "🔴 Negative"
    else:
        indicator = "🟡 Neutral"
    
    with st.expander(f"📰 News ({count} articles) — {indicator}"):
        for item in items:
            st.markdown(f"• [{item.title}]({item.link})")
    
    return sentiment_score

# -----------------------------
# GBM FORECAST (VECTORIZED)
# -----------------------------
@dataclass
class ForecastResult:
    dates: pd.DatetimeIndex
    mean_path: np.ndarray
    upper_bound: np.ndarray
    lower_bound: np.ndarray
    annual_drift: float
    annual_volatility: float
    expected_return: float

def run_gbm_forecast(df: pd.DataFrame) -> ForecastResult:
    """Vectorized Monte Carlo GBM simulation."""
    prices = df["Close"].values
    log_returns = np.diff(np.log(prices))
    
    mu_daily = np.mean(log_returns)
    sigma_daily = np.std(log_returns)
    
    # Annualized metrics
    mu_annual = mu_daily * CFG.trading_days_per_year
    sigma_annual = sigma_daily * np.sqrt(CFG.trading_days_per_year)
    
    last_price = prices[-1]
    days = CFG.forecast_days
    sims = CFG.simulations
    
    # Vectorized simulation: generate all random shocks at once
    shocks = np.random.standard_normal((days, sims))
    
    # GBM: S(t) = S(0) * exp((μ - σ²/2)t + σW(t))
    drift_component = (mu_daily - 0.5 * sigma_daily**2)
    cumulative_returns = np.cumsum(drift_component + sigma_daily * shocks, axis=0)
    paths = last_price * np.exp(cumulative_returns)
    
    # Percentiles for confidence band
    alpha = (1 - CFG.confidence_level) / 2
    lower_pct = alpha * 100
    upper_pct = (1 - alpha) * 100
    
    future_dates = pd.date_range(df.index[-1], periods=days + 1, freq="B")[1:]
    
    return ForecastResult(
        dates=future_dates,
        mean_path=np.mean(paths, axis=1),
        upper_bound=np.percentile(paths, upper_pct, axis=1),
        lower_bound=np.percentile(paths, lower_pct, axis=1),
        annual_drift=mu_annual,
        annual_volatility=sigma_annual,
        expected_return=(np.mean(paths[-1, :]) - last_price) / last_price
    )

# -----------------------------
# VISUALIZATION
# -----------------------------
def create_forecast_chart(df: pd.DataFrame, name: str, forecast: ForecastResult) -> go.Figure:
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Historical",
        line=dict(color="#3b82f6", width=2)
    ))
    
    # Forecast mean
    fig.add_trace(go.Scatter(
        x=forecast.dates,
        y=forecast.mean_path,
        name="Expected Path",
        line=dict(color="#f97316", width=2, dash="dot")
    ))
    
    # Confidence band
    fig.add_trace(go.Scatter(
        x=forecast.dates,
        y=forecast.upper_bound,
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=forecast.dates,
        y=forecast.lower_bound,
        fill="tonexty",
        fillcolor="rgba(249, 115, 22, 0.15)",
        line=dict(width=0),
        name=f"{CFG.confidence_level:.0%} Confidence"
    ))
    
    fig.update_layout(
        title=dict(text=name, font=dict(size=16)),
        height=380,
        yaxis_title="Price ($)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def display_model_stats(forecast: ForecastResult, sentiment: float):
    drift_direction = "📈 Bullish" if forecast.annual_drift > 0 else "📉 Bearish"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annual Drift", format_percent(forecast.annual_drift))
    col2.metric("Annual Volatility", format_percent(forecast.annual_volatility))
    col3.metric(f"{CFG.forecast_days}d Expected Return", format_percent(forecast.expected_return))
    col4.metric("Sentiment", f"{sentiment:+.2f}")
    
    st.caption(f"Model: GBM Monte Carlo ({CFG.simulations:,} paths) • {drift_direction}")

# -----------------------------
# COMPANY CARD
# -----------------------------
def render_company(name: str, ticker: str):
    df = load_history(ticker)
    info = load_info(ticker)
    
    if df is None or df.empty:
        st.warning(f"No data available for {ticker}")
        return
    
    st.subheader(f"{name} ({ticker})")
    
    # Key metrics row
    c1, c2, c3, c4 = st.columns(4)
    
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    c1.metric("Price", f"${price:.2f}" if price else "N/A")
    c2.metric("Market Cap", format_money(info.get("marketCap")))
    c3.metric("P/E", f"{info.get('trailingPE', 'N/A'):.1f}" if info.get('trailingPE') else "N/A")
    
    change = info.get("regularMarketChangePercent")
    c4.metric("Today", format_percent(change / 100) if change else "N/A", 
              delta=f"{change:.2f}%" if change else None)
    
    # News and sentiment
    sentiment = display_news(name, ticker)
    
    # Forecast
    forecast = run_gbm_forecast(df)
    fig = create_forecast_chart(df, name, forecast)
    st.plotly_chart(fig, use_container_width=True)
    
    display_model_stats(forecast, sentiment)

# -----------------------------
# MAIN APP
# -----------------------------
INFRASTRUCTURE_STACK = [
    ("⚡ Energy", [("Bloom Energy", "BE"), ("NextEra Energy", "NEE")]),
    ("🔩 Compute", [("Nebius", "NBIS"), ("IREN", "IREN")]),
    ("🔌 Networking", [("Astera Labs", "ALAB"), ("Credo", "CRDO")]),
]

st.title("🚀 AI Infrastructure Terminal")

st.markdown("""
**Probabilistic price forecasting** using Geometric Brownian Motion with Monte Carlo simulation.
Confidence bands represent the range where prices are expected to fall with the configured probability.
""")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    CFG.forecast_days = st.slider("Forecast horizon (days)", 30, 365, 180)
    CFG.simulations = st.slider("Monte Carlo paths", 100, 2000, 500, step=100)
    CFG.confidence_level = st.slider("Confidence level", 0.5, 0.99, 0.80)
    
    st.divider()
    st.caption("Data: Yahoo Finance • Model: GBM")

st.divider()

for layer_name, companies in INFRASTRUCTURE_STACK:
    st.header(layer_name)
    col1, col2 = st.columns(2)
    
    with col1:
        render_company(*companies[0])
    with col2:
        render_company(*companies[1])
    
    st.divider()
