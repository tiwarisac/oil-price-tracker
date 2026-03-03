
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import requests

# --- CONFIG ---
st.set_page_config(page_title="Global Energy Terminal 2026", layout="wide")

# -------------------------
# CACHED DATA FUNCTIONS
# -------------------------

@st.cache_data(ttl=60)
def get_oil_prices():
    tickers = ['BZ=F', 'CL=F']
    data = yf.download(
        tickers,
        period="5d",
        interval="1m",
        group_by='ticker',
        progress=False
    )
    return data.ffill()

@st.cache_data(ttl=120)
def get_gas_prices():
    tickers = ['NG=F', 'JKM=F', 'TTF=F', 'EURUSD=X']
    data = yf.download(
        tickers,
        period="5d",
        interval="5m",
        group_by='ticker',
        progress=False
    )
    return data.ffill()

def get_real_eia_data(api_key):
    if not api_key:
        return pd.DataFrame({"Week": ["Feb 27"], "Stocks (M)": [851.2], "Change": [+1.9]})
    try:
        url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]=WCESTUS1&sort[0][column]=period&sort[0][direction]=desc&length=5"
        response = requests.get(url).json()
        df = pd.DataFrame(response['response']['data'])
        return df[['period', 'value']].rename(columns={'period': 'Week', 'value': 'Stocks (M)'})
    except:
        return pd.DataFrame()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("Terminal Settings")
EIA_API_KEY = st.sidebar.text_input("EIA API Key", type="password")
country = st.sidebar.selectbox("Importer", ["India", "China", "Germany", "USA"])

volumes = {
    "India": 5000000,
    "China": 11000000,
    "Germany": 2000000,
    "USA": 6000000
}

daily_volume = st.sidebar.number_input("Daily Oil Barrels", value=volumes[country])
alert_threshold = st.sidebar.slider("Brent Alert ($)", 60, 120, 78)

st.title(f"🌍 {country} Energy Desk | 2026 Live")

# -------------------------
# FETCH OIL DATA
# -------------------------

oil_data = get_oil_prices()

brent_series = oil_data['BZ=F']['Close'].dropna()
wti_series = oil_data['CL=F']['Close'].dropna()

# -------------------------
# FETCH GAS DATA
# -------------------------

gas_data = get_gas_prices()

ng_series = gas_data['NG=F']['Close'].dropna()
jkm_series = gas_data['JKM=F']['Close'].dropna()
ttf_series = gas_data['TTF=F']['Close'].dropna()
eurusd_series = gas_data['EURUSD=X']['Close'].dropna()

# Convert TTF (EUR/MWh) → USD/MMBtu
ttf_usd_mmbtu = (ttf_series * eurusd_series) / 3.412

# -------------------------
# TOP METRICS
# -------------------------

if not brent_series.empty:

    brent_price = brent_series.iloc[-1]
    wti_price = wti_series.iloc[-1]
    ng_price = ng_series.iloc[-1] if not ng_series.empty else 0
    jkm_price = jkm_series.iloc[-1] if not jkm_series.empty else 0
    ttf_price = ttf_usd_mmbtu.iloc[-1] if not ttf_usd_mmbtu.empty else 0

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    m1.metric("Brent (ICE)", f"${brent_price:.2f}")
    m2.metric("WTI (NYMEX)", f"${wti_price:.2f}")
    m3.metric("NYMEX NG", f"${ng_price:.2f}/MMBtu")
    m4.metric("JKM LNG", f"${jkm_price:.2f}/MMBtu")
    m5.metric("TTF (USD adj)", f"${ttf_price:.2f}/MMBtu")
    m6.metric("Last Sync", datetime.now().strftime("%H:%M:%S"))

    st.markdown("---")

    col_chart, col_inv = st.columns([3, 1])

    with col_chart:
        fig_oil = go.Figure()

        fig_oil.add_trace(go.Scatter(
            x=brent_series.index,
            y=brent_series,
            name="Brent",
            line=dict(color='#00CC96', width=2)
        ))

        fig_oil.add_trace(go.Scatter(
            x=wti_series.index,
            y=wti_series,
            name="WTI",
            line=dict(color='#EF553B', width=2, dash='dot')
        ))

        fig_oil.update_layout(
            title="Crude Oil Price Comparison",
            template="plotly_dark",
            height=400,
            hovermode="x unified"
        )

        st.plotly_chart(fig_oil, use_container_width=True)

    with col_inv:
        st.subheader("EIA Inventory Hub")
        st.dataframe(get_real_eia_data(EIA_API_KEY), hide_index=True)
        st.caption("Data: US Commercial Crude Stocks")

    st.markdown("### 🔥 Global Natural Gas Benchmarks (USD/MMBtu)")

    fig_gas = go.Figure()

    fig_gas.add_trace(go.Scatter(
        x=ng_series.index,
        y=ng_series,
        name="NYMEX NG",
        line=dict(color='orange', width=2)
    ))

    fig_gas.add_trace(go.Scatter(
        x=jkm_series.index,
        y=jkm_series,
        name="JKM LNG",
        line=dict(color='cyan', width=2)
    ))

    fig_gas.add_trace(go.Scatter(
        x=ttf_usd_mmbtu.index,
        y=ttf_usd_mmbtu,
        name="TTF (USD adj)",
        line=dict(color='magenta', width=2)
    ))

    fig_gas.update_layout(
        template="plotly_dark",
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig_gas, use_container_width=True)

    spread1 = jkm_price - ng_price
    spread2 = ttf_price - ng_price

    s1, s2 = st.columns(2)
    s1.metric("JKM – NG Spread", f"${spread1:.2f}")
    s2.metric("TTF – NG Spread", f"${spread2:.2f}")

    st.markdown("### 💰 Oil Financial Impact Analysis")

    impact_df = pd.DataFrame({
        "Scenario": ["+10 BPS Move", "+100 BPS Move", "+$1.00 Rise"],
        "Daily Cost Increase": [
            f"${(daily_volume * brent_price * 0.001):,.2f}",
            f"${(daily_volume * brent_price * 0.01):,.2f}",
            f"${daily_volume:,.2f}"
        ],
        "Market Implication": ["Marginal", "Significant", "Major Shift"]
    })

    st.table(impact_df)

    csv_data = impact_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Impact Report (CSV)",
        data=csv_data,
        file_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="energy_download_btn"
    )

    time.sleep(30)
    st.rerun()
