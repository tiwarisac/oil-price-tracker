# oil-price-tracker
Tacks oil prices of Brent and WTI as Middle East Conflict with Iran surges in March 2026.
# 🛢️ Global Oil Terminal 2026

An interactive Energy Desk and Financial Impact Analysis dashboard built with Streamlit. This tool tracks real-time prices for **Brent Crude (ICE)** and **WTI (NYMEX)**, provides weekly **EIA Inventory** data, and calculates the daily fiscal impact of market shifts on national importers.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 👤 Author
**Sachin Tiwari**
*Lead Developer & Quantitative Analyst*

---

## 🚀 Key Features

- **Real-Time Price Feed:** Live intraday tracking of global oil benchmarks (Brent & WTI) via Yahoo Finance API.
- **Supply-Side Radar:** Integrated EIA (Energy Information Administration) Hub for monitoring US commercial crude stocks.
- **Financial Impact Engine:** Real-time calculation of daily cost changes (BPS moves) for major oil importers (India, China, USA, Germany).
- **Price Alerts:** Dynamic alert system with visual triggers when prices cross user-defined thresholds.
- **Mobile Optimized:** Fully responsive layout designed for iOS and Android access via Safari/Chrome.
- **Exportable Reports:** Download one-click CSV reports of current financial impact analysis.

## 📊 Methodology & Sources

- **Pricing Data:** Sourced via `yfinance` from ICE and NYMEX exchanges.
- **Inventory Data:** Official weekly reports from the **U.S. EIA API v2**.
- **Risk Premium:** The dashboard incorporates a geopolitical risk premium (currently estimated at ~$18/bbl for March 2026) based on research from Goldman Sachs and J.P. Morgan.

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.9+ installed. You will also need a free API key from the [EIA Open Data Portal](https://www.eia.gov/opendata/register.php).

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/oil-price-tracker.git](https://github.com/YOUR_USERNAME/oil-price-tracker.git)
cd oil-price-tracker

3. Install Dependencies
Bash
pip install -r requirements.txt
4. Run Locally
Bash
streamlit run oil_app.py

🌐 Deployment
This app is designed to be deployed on Streamlit Community Cloud:

Push your code to GitHub.

Connect your repo to share.streamlit.io.

For the EIA API Key, use Streamlit "Secrets" for secure production use.

📜 License
This project is open-source and available under the MIT License.

Disclaimer: This dashboard is for educational and analytical purposes. Financial data may be delayed by up to 15 minutes.


