import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="AI Memory Stock Dashboard", layout="wide")

# -----------------------------
# CONFIG
# -----------------------------
st.title("📊 AI Memory Chip Stock Dashboard")
st.subheader("SanDisk vs Peers: Growth vs Cyclicality vs AI Demand")

stocks = {
    "SanDisk": "SNDK",
    "Micron": "MU",
    "Western Digital": "WDC"
}

# -----------------------------
# FUNCTIONS
# -----------------------------
def get_data(ticker):
    t = yf.Ticker(ticker)
    return t, t.info, t.history(period="1y"), t.financials

def cycle_risk(info, hist):
    """
    Simple heuristic:
    - High volatility = higher cycle risk
    - Negative margins = higher risk
    - High revenue growth reduces risk slightly
    """
    volatility = hist["Close"].pct_change().std()

    margin = info.get("profitMargins") or 0
    growth = info.get("revenueGrowth") or 0

    score = (
        volatility * 50
        - margin * 20
        - growth * 10
    )

    return round(score, 2)

def ai_demand_score(info, hist):
    """
    Proxy AI exposure score:
    - revenue growth
    - margin strength
    - momentum
    """
    momentum = hist["Close"].pct_change().mean() * 100
    growth = (info.get("revenueGrowth") or 0) * 100
    margin = (info.get("profitMargins") or 0) * 100

    score = (growth * 0.5) + (margin * 0.3) + (momentum * 0.2)

    return round(score, 2)

# -----------------------------
# LOAD DATA
# -----------------------------
data = {}

for name, ticker in stocks.items():
    data[name] = get_data(ticker)

# -----------------------------
# PRICE COMPARISON
# -----------------------------
st.header("📈 Stock Price Comparison")

fig = go.Figure()

for name, (t, info, hist, fin) in data.items():
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name=name))

fig.update_layout(title="1Y Stock Price Comparison", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

st.write("""
This chart shows how market sentiment differs across the semiconductor storage ecosystem.  
SanDisk typically reflects stronger AI-driven momentum, while peers show more cyclical behavior.
""")

# -----------------------------
# FUNDAMENTALS TABLE
# -----------------------------
st.header("📊 Key Fundamental Comparison")

rows = []

for name, (t, info, hist, fin) in data.items():
    rows.append({
        "Company": name,
        "Revenue Growth": info.get("revenueGrowth"),
        "Profit Margin": info.get("profitMargins"),
        "Forward PE": info.get("forwardPE"),
        "Volatility": hist["Close"].pct_change().std(),
        "Cycle Risk Score": cycle_risk(info, hist),
        "AI Demand Score": ai_demand_score(info, hist)
    })

df = pd.DataFrame(rows)

st.dataframe(df)

st.write("""
- Revenue Growth → demand acceleration  
- Profit Margin → pricing power  
- Cycle Risk Score → how sensitive the stock is to semiconductor cycles  
- AI Demand Score → proxy for exposure to AI infrastructure demand  
""")

# -----------------------------
# RISK VISUALIZATION
# -----------------------------
st.header("⚠️ Cycle Risk vs AI Exposure")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Company"],
    y=df["Cycle Risk Score"],
    name="Cycle Risk",
    marker_color="red"
))

fig.add_trace(go.Bar(
    x=df["Company"],
    y=df["AI Demand Score"],
    name="AI Demand Score",
    marker_color="green"
))

fig.update_layout(barmode="group", title="Risk vs AI Exposure")
st.plotly_chart(fig, use_container_width=True)

st.write("""
This is the most important chart:

- High AI score + high cycle risk = **high growth but unstable**
- Lower cycle risk = more stable earnings base

SanDisk typically sits in a hybrid zone:
AI-driven upside layered on top of a cyclical semiconductor foundation.
""")

# -----------------------------
# INDIVIDUAL BREAKDOWN
# -----------------------------
st.header("🧠 Deep Dive per Company")

for name, (t, info, hist, fin) in data.items():

    st.subheader(name)

    col1, col2, col3 = st.columns(3)

    col1.metric("Revenue Growth", info.get("revenueGrowth"))
    col2.metric("Profit Margin", info.get("profitMargins"))
    col3.metric("Forward PE", info.get("forwardPE"))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"]))
    fig.update_layout(title=f"{name} Price Trend")
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    Interpretation:
    This section shows whether the company behaves like a cyclical semiconductor stock or a structural AI beneficiary.  
    Strong upward price trends paired with improving margins usually indicate AI-driven re-rating.
    """)

# -----------------------------
# FINAL SUMMARY
# -----------------------------
st.header("📌 Final Investment Interpretation")

st.write("""
### What this dashboard tells you:

- Semiconductor storage stocks are **highly cyclical by nature**
- AI demand is temporarily masking that cyclicality
- The key investment question is sustainability of AI-driven demand

### Simple framework:
- High AI Score + Low Cycle Risk → structural winner  
- High AI Score + High Cycle Risk → momentum trade (riskier)  
- Low AI Score + High Cycle Risk → traditional cyclical exposure  

SanDisk currently sits in the **high growth / medium-high risk zone**.
""")