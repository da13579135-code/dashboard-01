import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import feedparser
import urllib.parse

st.set_page_config(page_title="AI Infrastructure Terminal", layout="wide")

st.title("AI Infrastructure Dashboard")

# -----------------------------
# INTRO PARAGRAPH
# -----------------------------
st.markdown("""
This dashboard analyzes companies across the AI infrastructure stack, including energy, compute, and networking layers. 
It combines market data, news sentiment, and a probabilistic forecasting model based on Monte Carlo simulation using Geometric Brownian Motion. 
The goal is to provide a structured view of how different parts of the AI ecosystem behave financially and how uncertainty evolves over time.
""")

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.title("Settings")

forecast_days = st.sidebar.slider(
    "Forecast horizon (days)",
    30, 365, 180
)

simulations = st.sidebar.slider(
    "Monte Carlo paths",
    100, 2000, 500, step=100
)

confidence_level = st.sidebar.slider(
    "Confidence level",
    0.50, 0.99, 0.80
)

history_period = "2y"

# -----------------------------
# FORMATTERS
# -----------------------------
def format_money(x):
    if x is None:
        return "N/A"
    if x >= 1e12:
        return f"${x/1e12:.2f}T"
    if x >= 1e9:
        return f"${x/1e9:.2f}B"
    return f"${x:.0f}"

def format_percent(x):
    return "N/A" if x is None else f"{x * 100:.1f}%"

# -----------------------------
# DATA
# -----------------------------
@st.cache_data(ttl=300)
def load_history(ticker):
    return yf.Ticker(ticker).history(period=history_period)

@st.cache_data(ttl=60)
def load_info(ticker):
    return yf.Ticker(ticker).info

# -----------------------------
# SENTIMENT
# -----------------------------
POSITIVE_WORDS = {
    "beat", "growth", "strong", "surge",
    "record", "outperform", "profit", "bullish", "upgrade"
}

NEGATIVE_WORDS = {
    "miss", "weak", "loss", "decline",
    "downgrade", "bearish", "slump", "warning"
}

def compute_sentiment(items):
    if not items:
        return 0.0, 0

    total = 0

    for item in items:
        text = (item.title + " " + str(getattr(item, "summary", ""))).lower()

        pos = sum(word in text for word in POSITIVE_WORDS)
        neg = sum(word in text for word in NEGATIVE_WORDS)

        total += (pos - neg)

    return float(np.clip(total / max(len(items), 1), -1, 1)), len(items)

def display_news(company, ticker):
    query = urllib.parse.quote_plus(f"{company} {ticker} stock")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    items = feed.entries[:5]

    if not items:
        return 0.0

    sentiment, count = compute_sentiment(items)

    if sentiment > 0.1:
        label = "🟢 Positive"
    elif sentiment < -0.1:
        label = "🔴 Negative"
    else:
        label = "🟡 Neutral"

    with st.expander(f"News ({count}) - {label}"):
        for i in items:
            st.markdown(f"- [{i.title}]({i.link})")

    return sentiment

# -----------------------------
# GBM FORECAST
# -----------------------------
def run_gbm(df):
    prices = df["Close"].values
    returns = np.diff(np.log(prices))

    mu = np.mean(returns)
    sigma = np.std(returns)

    last_price = prices[-1]

    shocks = np.random.standard_normal((forecast_days, simulations))

    drift = (mu - 0.5 * sigma**2)
    cumulative = np.cumsum(drift + sigma * shocks, axis=0)

    paths = last_price * np.exp(cumulative)

    alpha = (1 - confidence_level) / 2

    upper = np.percentile(paths, (1 - alpha) * 100, axis=1)
    lower = np.percentile(paths, alpha * 100, axis=1)
    mean = np.mean(paths, axis=1)

    dates = pd.date_range(df.index[-1], periods=forecast_days + 1, freq="B")[1:]

    return dates, mean, upper, lower, mu, sigma

# -----------------------------
# CHART
# -----------------------------
def plot(df, name):

    dates, mean, upper, lower, mu, sigma = run_gbm(df)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Historical",
        line=dict(color="#3b82f6")
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=mean,
        name="Forecast",
        line=dict(color="#f97316", dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=upper,
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=lower,
        fill="tonexty",
        fillcolor="rgba(249,115,22,0.15)",
        line=dict(width=0),
        name=f"{confidence_level:.0%} Confidence Band"
    ))

    fig.update_layout(
        title=name,
        height=380,
        yaxis_title="Price ($)"
    )

    st.plotly_chart(fig, use_container_width=True)

    return mu, sigma

# -----------------------------
# COMPANY
# -----------------------------
def company(name, ticker):

    df = load_history(ticker)
    info = load_info(ticker)

    if df is None:
        st.warning(f"No data for {ticker}")
        return

    st.subheader(f"{name} ({ticker})")

    c1, c2, c3, c4 = st.columns(4)

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    change = info.get("regularMarketChangePercent")

    c1.metric("Price", f"${price:.2f}" if price else "N/A")
    c2.metric("Market Cap", format_money(info.get("marketCap")))
    c3.metric("P/E", info.get("trailingPE", "N/A"))

    if change is not None:
        c4.metric(
            "Today",
            format_percent(change / 100),
            delta=f"{change:.2f}%",
            delta_color="normal" if change > 0 else "inverse"
        )
    else:
        c4.metric("Today", "N/A")

    sentiment = display_news(name, ticker)

    plot(df, name)

# -----------------------------
# STACK
# -----------------------------
STACK = [
    ("Energy", [("Bloom Energy","BE"), ("NextEra Energy","NEE")]),
    ("Compute", [("Nebius","NBIS"), ("IREN","IREN")]),
    ("Networking", [("Astera Labs","ALAB"), ("Credo","CRDO")]),
]

# -----------------------------
# APP
# -----------------------------
for layer, comps in STACK:
    st.header(layer)

    c1, c2 = st.columns(2)

    with c1:
        company(*comps[0])
    with c2:
        company(*comps[1])

    st.divider()