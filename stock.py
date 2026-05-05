import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="The AI Investment Story", layout="wide")

st.title("⚡ The AI Investment Story")
st.subheader("How Energy becomes Intelligence → and Intelligence becomes Profit")

# -----------------------------
# HELPERS
# -----------------------------
def load(ticker):
    t = yf.Ticker(ticker)
    return t.history(period="1y"), t.info

def chart(hist, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"]))
    fig.update_layout(title=title, height=400)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# STORY INTRO
# -----------------------------
st.markdown("""
## 🎬 The Big Idea

AI is not a software trend.

It is an **industrial stack**:

> ⚡ Energy → 🔩 Chips → 🏗️ Infrastructure → 🧠 Models → 📱 Applications

Each layer depends on the one below it.

Money flows upward through this stack.
""")

st.divider()

# -----------------------------
# 1. ENERGY LAYER
# -----------------------------
st.header("⚡ Stage 1: Energy — The Hidden Bottleneck")

hist, info = load("NEE")

chart(hist, "NextEra Energy — Powering the AI Era")

st.write("""
AI requires massive electricity.

Data centers are becoming some of the largest power consumers in history.

👉 Without energy, nothing else in AI works.

Energy is the **foundation layer of intelligence production**.
""")

st.divider()

# -----------------------------
# 2. CHIPS LAYER
# -----------------------------
st.header("🔩 Stage 2: Chips — Turning Energy into Intelligence")

hist, info = load("NVDA")

chart(hist, "NVIDIA — The AI Compute Engine")

st.write("""
Chips are where energy becomes computation.

NVIDIA dominates because:
- GPUs parallelize intelligence
- AI training scales with compute
- Demand is exponential

👉 Chips are the **conversion layer of AI value creation**.
""")

st.divider()

# -----------------------------
# 3. INFRASTRUCTURE
# -----------------------------
st.header("🏗️ Stage 3: Infrastructure — Scaling Intelligence")

hist, info = load("MSFT")

chart(hist, "Microsoft — Azure AI Infrastructure")

st.write("""
Infrastructure companies scale AI globally.

They provide:
- cloud compute
- storage
- enterprise AI deployment

👉 This is where AI becomes **accessible at global scale**.
""")

st.divider()

# -----------------------------
# 4. MODELS
# -----------------------------
st.header("🧠 Stage 4: AI Models — Intelligence Itself")

hist, info = load("GOOGL")

chart(hist, "Alphabet — AI Model Development")

st.write("""
Models are the “brain layer” of AI.

They:
- learn from data
- generate predictions
- power downstream applications

👉 This is where intelligence is actually created.
""")

st.divider()

# -----------------------------
# 5. APPLICATIONS
# -----------------------------
st.header("📱 Stage 5: Applications — Monetizing Intelligence")

hist, info = load("META")

chart(hist, "Meta — AI-Driven Consumer Platforms")

st.write("""
Applications are where AI becomes revenue.

Examples:
- social feeds
- ads optimization
- content generation

👉 This is where intelligence becomes **cash flow**.
""")

st.divider()

# -----------------------------
# FINAL MESSAGE
# -----------------------------
st.header("📌 The Full Story")

st.markdown("""
### 🔁 The Flow of Value

1. Energy powers compute  
2. Chips convert energy into intelligence  
3. Infrastructure scales intelligence  
4. Models create intelligence  
5. Applications monetize intelligence  

---

### 🧠 Key Insight

You are not investing in companies.

You are investing in **layers of a machine that turns electricity into profit**.

---

### 🚀 Why this matters

Early in cycles:
- Chips lead

Mid-cycle:
- Infrastructure leads

Late cycle:
- Applications dominate

---

### 📊 The real edge

Understanding **where we are in the stack** matters more than picking individual stocks.
""")