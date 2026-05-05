import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import urllib.parse

st.set_page_config(page_title="The AI Investment Story", layout="wide")

st.title("⚡ The AI Investment Story+")
st.subheader("From Energy → Chips → Infrastructure → Models → Applications")


# -----------------------------
# CACHE
# -----------------------------
@st.cache_resource
def get_ticker(ticker: str):
    return yf.Ticker(ticker)


@st.cache_data
def load_history(ticker: str):
    return yf.Ticker(ticker).history(period="1y")


@st.cache_data
def load_info(ticker: str):
    return yf.Ticker(ticker).info


# -----------------------------
# CHART
# -----------------------------
def chart(hist, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        line=dict(color="royalblue")
    ))
    fig.update_layout(title=title, height=350)
    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# FIXED NEWS (URL ENCODED + RSS)
# -----------------------------
def show_news(company_name, ticker):
    st.subheader("📰 Latest News")

    # ✅ FIX: encode query properly (prevents InvalidURL error)
    query = urllib.parse.quote_plus(f"{company_name} {ticker}")

    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    entries = feed.entries[:6]

    if not entries:
        st.warning("No news available right now.")
        return

    for entry in entries:
        title = entry.get("title", "No title")
        link = entry.get("link", "#")
        published = entry.get("published", "")

        st.markdown(f"""
**[{title}]({link})**  
_{published}_  
""")


# -----------------------------
# FINANCIALS
# -----------------------------
def safe_financials(ticker_obj):
    try:
        income = ticker_obj.income_stmt
        if income is None or income.empty:
            return None, None

        revenue = income.loc["Total Revenue"].iloc[0]
        net_income = income.loc["Net Income"].iloc[0]
        return revenue, net_income
    except:
        return None, None


# -----------------------------
# COMPANY SECTION
# -----------------------------
def company_section(name, ticker, story):

    st.header(f"{story['icon']} {story['stage']}: {story['title']}")

    t = get_ticker(ticker)
    hist = load_history(ticker)
    info = load_info(ticker)

    col1, col2, col3 = st.columns(3)

    price = info.get("currentPrice")
    market_cap = info.get("marketCap")
    pe = info.get("trailingPE")

    revenue, net_income = safe_financials(t)

    with col1:
        st.metric("Price", f"${price}" if price else "N/A")

    with col2:
        st.metric("Market Cap", f"{market_cap/1e12:.2f}T" if market_cap else "N/A")

    with col3:
        st.metric("P/E Ratio", f"{pe:.1f}" if pe else "N/A")

    chart(hist, f"{name} — 1Y Performance")

    tab1, tab2, tab3 = st.tabs(["📊 Financials", "🧠 Story", "📰 News"])

    with tab1:
        st.subheader("Revenue & Profit Snapshot")

        if revenue:
            st.write(f"💰 Revenue: **${revenue:,.0f}**")
        else:
            st.write("Revenue data unavailable")

        if net_income:
            st.write(f"📈 Net Income: **${net_income:,.0f}**")
        else:
            st.write("Net income data unavailable")

    with tab2:
        st.subheader("AI Stack Role")
        st.markdown(story["description"])
        st.info(story["insight"])

    with tab3:
        show_news(name, ticker)


# -----------------------------
# STORY MAP
# -----------------------------
story_map = [
    {
        "name": "NextEra Energy",
        "ticker": "NEE",
        "stage": "Stage 1",
        "icon": "⚡",
        "title": "Energy — Foundation",
        "description": "Energy powers all AI computation and data centers.",
        "insight": "AI is driving massive electricity demand growth."
    },
    {
        "name": "NVIDIA",
        "ticker": "NVDA",
        "stage": "Stage 2",
        "icon": "🔩",
        "title": "Chips — Compute Layer",
        "description": "GPUs convert energy into intelligence at scale.",
        "insight": "AI training demand continues exponential growth."
    },
    {
        "name": "Microsoft",
        "ticker": "MSFT",
        "stage": "Stage 3",
        "icon": "🏗️",
        "title": "Infrastructure — Scale Layer",
        "description": "Cloud infrastructure enables global AI deployment.",
        "insight": "Azure is central to enterprise AI adoption."
    },
    {
        "name": "Alphabet",
        "ticker": "GOOGL",
        "stage": "Stage 4",
        "icon": "🧠",
        "title": "Models — Intelligence Layer",
        "description": "AI models generate reasoning and predictions.",
        "insight": "Search + AI integration is key monetization path."
    },
    {
        "name": "Meta",
        "ticker": "META",
        "stage": "Stage 5",
        "icon": "📱",
        "title": "Applications — Monetization Layer",
        "description": "AI powers ads, feeds, and recommendations.",
        "insight": "AI improves ad efficiency and revenue per user."
    }
]


# -----------------------------
# INTRO
# -----------------------------
st.markdown("""
## 🎬 AI Investment Stack Thesis

> ⚡ Energy → 🔩 Chips → 🏗️ Infrastructure → 🧠 Models → 📱 Applications
""")

st.divider()


# -----------------------------
# RENDER APP
# -----------------------------
for c in story_map:
    company_section(c["name"], c["ticker"], c)