import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import feedparser
import urllib.parse

st.set_page_config(page_title="AI Stack Story", layout="wide")

# -----------------------------
# NEW TITLE (UPDATED)
# -----------------------------
st.title("⚡ Why AI Stack Matters - Big Players in Each AI Layer")
st.subheader("Energy → Chips → Infrastructure → Models → Applications")


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
# CHART (IMPROVED CLARITY)
# -----------------------------
def chart(hist, name):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        line=dict(color="royalblue"),
        name="Stock Price"
    ))

    fig.update_layout(
        title=f"{name} — Stock Price (1Y)",
        height=350,
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# NEWS (FIXED RSS)
# -----------------------------
def show_news(company_name, ticker):
    st.subheader("📰 Latest News")

    query = urllib.parse.quote_plus(f"{company_name} {ticker}")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    entries = feed.entries[:6]

    if not entries:
        st.warning("No news available right now.")
        return

    for entry in entries:
        st.markdown(f"""
**[{entry.get('title','No title')}]({entry.get('link','#')})**  
_{entry.get('published','')}_  
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

    chart(hist, name)

    tab1, tab2, tab3 = st.tabs(["📊 Financials", "🧠 Story", "📰 News"])

    # -----------------------------
    # FINANCIALS
    # -----------------------------
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

    # -----------------------------
    # STORY (EXPANDED)
    # -----------------------------
    with tab2:
        st.subheader("Why This Company Matters in the AI Stack")

        st.markdown(story["long_story"])

    # -----------------------------
    # NEWS
    # -----------------------------
    with tab3:
        show_news(name, ticker)


# -----------------------------
# STORY MAP (EXPANDED INSIGHTS)
# -----------------------------
story_map = [
    {
        "name": "NextEra Energy",
        "ticker": "NEE",
        "stage": "Stage 1",
        "icon": "⚡",
        "title": "Energy — Foundation Layer",
        "description": "Energy powers all AI computation and data centers.",
        "long_story": """
NextEra Energy sits at the foundation of the entire AI revolution because every AI system ultimately depends on electricity. As data centers expand globally to support model training and inference, power demand is becoming one of the most critical constraints in the AI ecosystem. Without scalable and reliable energy infrastructure, none of the higher layers—chips, cloud, or models—can operate at full capacity.

This makes the energy layer structurally essential rather than optional. Companies in this segment indirectly benefit from AI growth because they provide the physical capacity that enables computation at scale. In the long run, energy becomes the “gatekeeper” of AI expansion, determining how fast the entire stack can grow.
"""
    },
    {
        "name": "NVIDIA",
        "ticker": "NVDA",
        "stage": "Stage 2",
        "icon": "🔩",
        "title": "Chips — Compute Layer",
        "long_story": """
NVIDIA is the compute engine of the AI stack. It transforms raw electrical energy into usable intelligence through highly parallel GPU architectures optimized for machine learning workloads. Every major AI breakthrough—from large language models to generative systems—relies on GPU acceleration.

This layer is critical because it determines how efficiently intelligence can be created. The faster and more scalable the compute layer becomes, the more powerful AI models can grow. NVIDIA effectively sits at the bottleneck between energy and intelligence, capturing enormous value as demand for AI training and inference continues to accelerate globally.
"""
    },
    {
        "name": "Microsoft",
        "ticker": "MSFT",
        "stage": "Stage 3",
        "icon": "🏗️",
        "title": "Infrastructure — Scale Layer",
        "long_story": """
Microsoft provides the infrastructure backbone of AI through Azure, enabling companies to deploy and scale AI systems globally without managing physical hardware. This abstraction layer is what turns raw compute into accessible utility.

The importance of this layer is scalability. Even if chips and models exist, they are useless without distributed systems that make them usable at enterprise scale. Microsoft captures value by embedding AI into cloud services, making it the default platform for enterprise AI adoption and long-term recurring revenue.
"""
    },
    {
        "name": "Alphabet",
        "ticker": "GOOGL",
        "stage": "Stage 4",
        "icon": "🧠",
        "title": "Models — Intelligence Layer",
        "long_story": """
Alphabet operates at the intelligence layer, where raw data is transformed into predictive and generative capability. Through advanced AI models, it powers search, advertising optimization, and emerging generative AI systems.

This layer is critical because it defines the actual “thinking capability” of the AI stack. Without strong models, infrastructure and compute cannot produce meaningful outcomes. Alphabet’s advantage comes from its massive data ecosystem and integration of AI into core products like Search and YouTube, making intelligence directly monetizable.
"""
    },
    {
        "name": "Meta",
        "ticker": "META",
        "stage": "Stage 5",
        "icon": "📱",
        "title": "Applications — Monetization Layer",
        "long_story": """
Meta represents the application layer where AI directly generates revenue. Its platforms use AI for feed ranking, content recommendation, and advertising optimization, turning intelligence into user engagement and monetized attention.

This layer is critical because it closes the loop of the AI stack. While lower layers create intelligence, applications convert it into cash flow. Meta benefits from AI by increasing ad efficiency, improving targeting precision, and maximizing time spent on platform—making AI a direct driver of revenue growth.
"""
    }
]


# -----------------------------
# RENDER
# -----------------------------
for c in story_map:
    company_section(c["name"], c["ticker"], c)