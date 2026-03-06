import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import feedparser
from streamlit_autorefresh import st_autorefresh

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="Global Energy Terminal",
    layout="wide"
)

# ----------------------------------------------------
# AUTO REFRESH (15 seconds)
# ----------------------------------------------------

st_autorefresh(interval=15000, key="energy_refresh")

# ----------------------------------------------------
# TERMINAL STYLE
# ----------------------------------------------------

st.markdown("""
<style>

body {
background-color:#0a0a0a;
}

[data-testid="metric-container"] {
background-color:#111;
border:1px solid #333;
padding:10px;
border-radius:6px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# DATA FUNCTIONS
# ----------------------------------------------------

@st.cache_data(ttl=120)
def load_energy_prices():

    tickers = [
        "BZ=F",   # Brent
        "CL=F",   # WTI
        "NG=F",   # Henry Hub
        "TTF=F",  # Dutch TTF
        "EURUSD=X",
        "DX-Y.NYB",
        "^TNX"
    ]

    try:
        df = yf.download(
            tickers,
            period="5d",
            interval="15m",
            group_by="ticker",
            progress=False
        )

        return df.ffill()

    except:
        return pd.DataFrame()

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

data = load_energy_prices()

if data.empty:
    st.error("Market data unavailable")
    st.stop()

def series(ticker):

    try:
        return data[ticker]["Close"].dropna()
    except:
        return pd.Series()

brent = series("BZ=F")
wti = series("CL=F")
ng = series("NG=F")
ttf = series("TTF=F")
eurusd = series("EURUSD=X")
dxy = series("DX-Y.NYB")
us10y = series("^TNX")

# ----------------------------------------------------
# PRICE EXTRACTION
# ----------------------------------------------------

def last(series):
    return series.iloc[-1] if not series.empty else 0

brent_price = last(brent)
wti_price = last(wti)
ng_price = last(ng)

if not ttf.empty and not eurusd.empty:
    ttf_usd = (ttf * eurusd) / 3.412
else:
    ttf_usd = pd.Series()

ttf_price = last(ttf_usd)

dxy_price = last(dxy)
us10y_price = last(us10y)

# ----------------------------------------------------
# LIVE TERMINAL TICKER
# ----------------------------------------------------

ticker_html = f"""
<div style="
background:#000;
padding:12px;
font-family:monospace;
color:#00ff9f;
font-size:16px;
border-bottom:1px solid #333;
">

BRENT {brent_price:.2f} |
WTI {wti_price:.2f} |
HENRY HUB {ng_price:.2f} |
TTF {ttf_price:.2f} |
DXY {dxy_price:.2f} |
US10Y {us10y_price:.2f}

</div>
"""

st.markdown(ticker_html, unsafe_allow_html=True)

# ----------------------------------------------------
# TITLE
# ----------------------------------------------------

st.title("🌍 Global Energy Terminal")

# ----------------------------------------------------
# METRICS
# ----------------------------------------------------

m1,m2,m3,m4,m5 = st.columns(5)

m1.metric("Brent", f"${brent_price:.2f}")
m2.metric("WTI", f"${wti_price:.2f}")
m3.metric("Henry Hub", f"${ng_price:.2f}")
m4.metric("TTF", f"${ttf_price:.2f}")
m5.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

st.divider()

# ----------------------------------------------------
# OIL CHART
# ----------------------------------------------------

fig_oil = go.Figure()

if not brent.empty:
    fig_oil.add_trace(go.Scatter(
        x=brent.index,
        y=brent,
        name="Brent",
        line=dict(width=2)
    ))

if not wti.empty:
    fig_oil.add_trace(go.Scatter(
        x=wti.index,
        y=wti,
        name="WTI",
        line=dict(width=2, dash="dot")
    ))

fig_oil.update_layout(
    template="plotly_dark",
    height=400,
    title="Crude Oil"
)

# ----------------------------------------------------
# GAS CHART
# ----------------------------------------------------

fig_gas = go.Figure()

if not ng.empty:
    fig_gas.add_trace(go.Scatter(
        x=ng.index,
        y=ng,
        name="Henry Hub",
        line=dict(width=2)
    ))

if not ttf_usd.empty:
    fig_gas.add_trace(go.Scatter(
        x=ttf_usd.index,
        y=ttf_usd,
        name="TTF (USD)",
        line=dict(width=2)
    ))

fig_gas.update_layout(
    template="plotly_dark",
    height=400,
    title="Natural Gas"
)

# ----------------------------------------------------
# MACRO CHART
# ----------------------------------------------------

fig_macro = go.Figure()

if not dxy.empty:
    fig_macro.add_trace(go.Scatter(
        x=dxy.index,
        y=dxy,
        name="Dollar Index"
    ))

if not us10y.empty:
    fig_macro.add_trace(go.Scatter(
        x=us10y.index,
        y=us10y,
        name="US 10Y Yield"
    ))

fig_macro.update_layout(
    template="plotly_dark",
    height=400,
    title="Macro Drivers"
)

# ----------------------------------------------------
# MAIN DASHBOARD
# ----------------------------------------------------

c1,c2,c3 = st.columns(3)

with c1:
    st.plotly_chart(fig_oil, use_container_width=True)

with c2:
    st.plotly_chart(fig_gas, use_container_width=True)

with c3:
    st.plotly_chart(fig_macro, use_container_width=True)

# ----------------------------------------------------
# SPREADS
# ----------------------------------------------------

st.subheader("Energy Market Spreads")

spread1 = brent_price - wti_price
spread2 = ttf_price - ng_price

s1,s2 = st.columns(2)

s1.metric("Brent – WTI", f"${spread1:.2f}")
s2.metric("TTF – Henry Hub", f"${spread2:.2f}")

# ----------------------------------------------------
# ALERTS
# ----------------------------------------------------

st.subheader("⚠️ Energy Market Alerts")

alerts = [
"OPEC+ meeting expected this month",
"Red Sea shipping disruptions continue",
"US crude inventories trending higher"
]

for a in alerts:
    st.warning(a)

# ----------------------------------------------------
# ENERGY NEWS
# ----------------------------------------------------

st.subheader("📰 Energy News")

try:
    feed = feedparser.parse("https://www.reuters.com/markets/energy/rss")

    for entry in feed.entries[:6]:
        st.write("•", entry.title)

except:
    st.write("News feed unavailable")

# ----------------------------------------------------
# FINANCIAL IMPACT
# ----------------------------------------------------

st.subheader("Oil Price Impact")

daily_volume = 5000000

impact_df = pd.DataFrame({
    "Scenario":[
        "+10 BPS Move",
        "+100 BPS Move",
        "+$1 Price Rise"
    ],
    "Daily Cost":[
        f"${daily_volume * brent_price * 0.001:,.0f}",
        f"${daily_volume * brent_price * 0.01:,.0f}",
        f"${daily_volume:,.0f}"
    ]
})

st.table(impact_df)

csv = impact_df.to_csv(index=False).encode()

st.download_button(
    "Download Impact Report",
    csv,
    "energy_report.csv",
    "text/csv"
)
