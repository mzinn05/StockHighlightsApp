import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import requests
import time

# Set page config as the first command
st.set_page_config(page_title="StockHighlights", layout="wide", page_icon="📈")

# Theme toggle in sidebar
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

st.sidebar.header("Settings ⚙️")
st.session_state.theme = st.sidebar.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)

# Glossary in sidebar
st.sidebar.header("Glossary 📖")
with st.sidebar.expander("Key Terms"):
    st.markdown("""
    - **RSI (Relative Strength Index)**: Measures momentum. Below 30 may indicate a stock is oversold and could rise.
    - **Analyst Recommendation**: Based on RSI: Buy (RSI < 50), Hold (50-70), Sell (>70).
    - **Momentum**: Average price change over 5 days. Positive momentum suggests an upward trend.
    - **Change**: Percentage change in price from the day's open to close.
    """)

# Apply theme with refined styling and consistent contrast
if st.session_state.theme == "Light":
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to bottom, #F9F9F9, #E6F3FA);
                color: #333333;
            }
            .stDataFrame {background-color: #FFFFFF; border: 1px solid #E0E0E0; color: #333333;}
            .stCard {background-color: #F0F8FF; border-radius: 10px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #ADD8E6; color: #333333;}
            .stNews {background-color: #E6F3FA; border-radius: 10px; padding: 10px; margin-top: 10px; border: 1px solid #87CEEB; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #000000;}
            .stSection {background: linear-gradient(90deg, #E6F3FA, #F0F8FF); padding: 10px; border-radius: 8px;}
            h1 {font-family: 'Arial', sans-serif; color: #333333;}
            h3 {font-family: 'Verdana', sans-serif; color: #333333;}
            a {color: #0066cc; text-decoration: none;}
            a:hover {color: #003366; text-decoration: underline;}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to bottom, #1E1E1E, #2E2E2E);
                color: #FFFFFF;
            }
            .stDataFrame {background-color: #2E2E2E; border: 1px solid #444444; color: #FFFFFF;}
            .stCard {background-color: #2E2E2E; border-radius: 10px; padding: 15px; border: 1px solid #555555; color: #FFFFFF;}
            .stNews {background-color: #3A3A3A; border-radius: 10px; padding: 10px; margin-top: 10px; border: 1px solid #666666; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #E0E0E0;}
            .stSection {background: linear-gradient(90deg, #3A3A3A, #2E2E2E); padding: 10px; border-radius: 8px;}
            h1 {font-family: 'Arial', sans-serif; color: #FFFFFF;}
            h3 {font-family: 'Verdana', sans-serif; color: #FFFFFF;}
            a {color: #66b3ff; text-decoration: none;}
            a:hover {color: #99ccff; text-decoration: underline;}
        </style>
    """, unsafe_allow_html=True)

# Header with lighter gradient
st.markdown("""
    <h1 style='text-align: center; background: linear-gradient(90deg, #87CEEB, #98FB98); -webkit-background-clip: text; color: transparent; font-size: 48px;'>
        StockHighlights - {}</h1>
""".format(datetime.now().strftime('%Y-%m-%d')), unsafe_allow_html=True)

# Sidebar tips
st.sidebar.markdown("**Investor Tips for Beginners** 🎯")
st.sidebar.markdown("""
- **Start Small** 📈: Invest in what you understand.
- **Diversify** 🌐: Spread your investments.
- **Watch RSI** 🔍: Below 30 may mean a buy signal.
- **Stay Updated** 📰: Follow daily news!
""")

# Cached data fetching with spinner
@st.cache_data
def fetch_data(ticker, period="1mo"):
    with st.spinner(f"Fetching data for {ticker}..."):
        time.sleep(1)  # Simulate loading time
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            return data if not data.empty else None
        except Exception as e:
            st.error(f"Failed to fetch data for {ticker}: {e}")
            return None

# Cached RSI calculation
@st.cache_data
def calculate_rsi(data, periods=14):
    if data.empty or "Close" not in data.columns:
        return pd.Series(dtype=float)
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(span=periods, adjust=False).mean()
    avg_loss = loss.ewm(span=periods, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Cached news fetching
@st.cache_data
def fetch_news(query="stock market"):
    with st.spinner("Fetching news..."):
        time.sleep(1)  # Simulate loading time
        try:
            api_key = st.secrets.get("news", {}).get("api_key")
            if not api_key:
                st.warning("News API key not found in secrets. Please configure secrets.toml.")
                return []
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=5"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("articles", [])
            else:
                st.warning("News API request failed. Try again later.")
                return []
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return []

# Interactive chart with smaller size and debug print
def plot_chart(ticker, data, title):
    print("Plot chart function is called for:", ticker)  # Debug print
    if data is None or data.empty:
        print(f"No data available for {ticker}")
        return None
    fig = go.Figure()
    trend_color = "#32CD32" if data["Close"].iloc[-1] >= data["Close"].iloc[0] else "#FF4500"
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data["Close"], 
        mode="lines", 
        name="Close Price", 
        line=dict(color=trend_color),
        hovertemplate="Date: %{x}<br>Price: %{y:.2f}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white" if st.session_state.theme == "Light" else "plotly_dark",
        height=200,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Market Overview
def get_market_overview():
    indices = {"^GSPC": "S&P 500 (US)", "^DJI": "Dow Jones (US)", "^IXIC": "NASDAQ (US)", "^GSPTSE": "TSX Composite (CA)"}
    overview_data = {}
    for symbol, name in indices.items():
        data = fetch_data(symbol, period="1d")
        if data is not None:
            current_price = data["Close"].iloc[-1]
            change = ((current_price - data["Open"].iloc[0]) / data["Open"].iloc[0]) * 100
            overview_data[name] = {"Price": current_price, "Change": change}
    return overview_data

# Stock data with caching
@st.cache_data
def get_stock_data(stock_list, period="1mo"):
    stock_data = {}
    for symbol in stock_list:
        data = fetch_data(symbol, period)
        if data is not None:
            current_price = data["Close"].iloc[-1]
            day_change = ((current_price - data["Open"].iloc[-1]) / data["Open"].iloc[-1]) * 100
            momentum = (data["Close"].iloc[-1] - data["Close"].iloc[-5]) / 5 if len(data) >= 5 else 0
            rsi = calculate_rsi(data).iloc[-1] if not calculate_rsi(data).empty else 0
            analyst_pick = "Buy" if rsi < 50 else "Hold" if rsi < 70 else "Sell"
            risk = "High" if abs(day_change) > 5 else "Medium"
            stock_data[symbol] = {
                "Price": current_price, "Change": day_change,
                "Momentum": momentum, "RSI": rsi, "Analyst": analyst_pick, "Risk": risk, "Data": data
            }
    return stock_data

# Economic picks
def get_economic_picks():
    picks = ["SHOP.TO", "BNS.TO", "AMD", "TGT", "TD.TO", "CNQ.TO"]
    return get_stock_data(picks)

# Get top 3 picks with strong upward trend
def get_top_3_picks(stock_data_dict):
    stock_data_list = list(stock_data_dict.values())
    sorted_data = sorted(stock_data_list, key=lambda x: (x["Change"], x["Momentum"]), reverse=True)
    top_picks = [stock for stock in sorted_data if stock["Change"] > 0 and stock["Momentum"] > 0.005][:3]
    if len(top_picks) < 3:
        additional_picks = [stock for stock in sorted_data if stock["Change"] > 0 and stock not in top_picks][:3 - len(top_picks)]
        top_picks.extend(additional_picks)
    return top_picks[:3]

# Interactive stock selector
def display_stock_selector(stock_data_dict):
    selected_ticker = st.selectbox("Select a stock to view details", list(stock_data_dict.keys()))
    if selected_ticker:
        stock = stock_data_dict[selected_ticker]
        st.write(f"**{selected_ticker} Details**: Price: {stock['Price']:.2f}, Change: {stock['Change']:.2f}%, Momentum: {stock['Momentum']:.2f}, RSI: {stock['RSI']:.2f}, Analyst: {stock['Analyst']}")
        st.plotly_chart(plot_chart(selected_ticker, stock["Data"], f"{selected_ticker} - 30 Days"), use_container_width=True, key=f"selected_chart_{selected_ticker}")

# Main App
def main_app():
    # Refresh button
    if st.button("Refresh Data 🔄"):
        st.cache_data.clear()  # Clear cache on refresh
        st.experimental_rerun()

    # Market Summary
    st.subheader("Market Summary 📰", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        news = fetch_news("stock market")
        if news:
            for article in news:
                st.markdown(f"<div class='stNews'>- <a href='{article['url']}' target='_blank' style='color: #000000;'>{article['title']}</a></div>", unsafe_allow_html=True)
        else:
            st.warning("No news available at the moment or API key issue.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Market Overview
    st.subheader("Market Overview 🌍", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        overview = get_market_overview()
        cols = st.columns(4)
        for i, (name, info) in enumerate(overview.items()):
            with cols[i]:
                st.markdown(f"""
                    <div class='stCard'>
                        <h3 style='color: {'#32CD32' if info['Change'] >= 0 else '#FF4500'}'>{name}</h3>
                        <p>Price: {info['Price']:.2f}</p>
                        <p>Change: {info['Change']:.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Top 3 Picks to Invest In
    st.subheader("Top 3 Picks to Invest In 🌟", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        trending_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "WMT", "RY.TO", "TD.TO", "ENB.TO"]
        trending_data = get_stock_data(trending_stocks)
        top_3_picks = get_top_3_picks(trending_data)
        if top_3_picks:
            st.write("Stocks with strong upward trends (Positive Change & Momentum):")
            for idx, pick in enumerate(top_3_picks):
                symbol = [k for k, v in trending_data.items() if v == pick][0]  # Find the symbol for the pick
                st.write(f"- 📈 {symbol}: Price: {pick['Price']:.2f}, Change: {pick['Change']:.2f}%, Momentum: {pick['Momentum']:.2f}")
                if pick["Data"] is not None:
                    chart = plot_chart(symbol, pick["Data"], f"{symbol} - 30 Days")
                    if chart:
                        st.plotly_chart(
                            chart,
                            use_container_width=True,
                            key=f"top3_pick_chart_{symbol}_{idx}"
                        )
                    else:
                        st.warning(f"Could not generate chart for {symbol}")
                else:
                    st.warning(f"No data available to generate chart for {symbol}")
        else:
            st.warning("No stocks with a strong upward trend found today. Try refreshing or check back later!")
        st.markdown("</div>", unsafe_allow_html=True)

    # Interactive Stock Selector
    st.subheader("Explore Individual Stocks 🔍", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        all_stocks = trending_stocks + ["PLTR", "SQ", "ROKU", "ZM", "CRSP", "DOCU", "PINS", "ETSY", "FVRR", "ENPH", "BCE.TO", "CNQ.TO"]
        all_stock_data = get_stock_data(all_stocks)
        display_stock_selector(all_stock_data)
        st.markdown("</div>", unsafe_allow_html=True)

    # Pagination for Trending Stocks
    st.subheader("Top Trending Stocks 📈", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        trending_data = get_stock_data(trending_stocks)
        trending_df = pd.DataFrame(
            [(k, v["Price"], v["Change"], v["Momentum"], v["RSI"], v["Analyst"], v["Risk"]) for k, v in trending_data.items()]
        ).sort_values(by=2, ascending=False).head(10)  # Sort by "Change" (index 2)
        trending_df.columns = ["Symbol", "Price", "Change", "Momentum", "RSI", "Analyst", "Risk"]
        st.dataframe(
            trending_df.style.applymap(
                lambda x: "color: #FF4500;" if isinstance(x, float) and x < 0 else "color: #32CD32;" if isinstance(x, float) and x >= 0 else "",
                subset=["Change"]
            ).format({"Price": "{:.2f}", "Change": "{:.2f}%", "Momentum": "{:.2f}", "RSI": "{:.2f}"})
        )
        for idx, (symbol, data) in enumerate(trending_data.items()):
            if idx < 10:  # Limit to top 10
                if data["Data"] is not None:
                    chart = plot_chart(symbol, data["Data"], f"{symbol} - 30 Days")
                    if chart:
                        st.plotly_chart(
                            chart,
                            use_container_width=True,
                            key=f"trending_chart_{symbol}_{idx}"
                        )
                    else:
                        st.warning(f"Could not generate chart for {symbol}")
                else:
                    st.warning(f"No data available to generate chart for {symbol}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Up-and-Coming Stocks (with pagination)
    st.subheader("Top Up-and-Coming Stocks 🚀", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        potential_stocks = ["PLTR", "SQ", "ROKU", "ZM", "CRSP", "DOCU", "PINS", "ETSY", "FVRR", "ENPH", "BCE.TO", "CNQ.TO"]
        potential_data = get_stock_data(potential_stocks)
        potential_df = pd.DataFrame(
            [(k, v["Price"], v["Change"], v["Momentum"], v["RSI"], v["Analyst"], v["Risk"]) for k, v in potential_data.items()]
        ).sort_values(by=3, key=abs, ascending=False).head(10)  # Sort by "Momentum" (index 3)
        potential_df.columns = ["Symbol", "Price", "Change", "Momentum", "RSI", "Analyst", "Risk"]
        st.dataframe(
            potential_df.style.applymap(
                lambda x: "color: #FF4500;" if isinstance(x, float) and x < 0 else "color: #32CD32;" if isinstance(x, float) and x >= 0 else "",
                subset=["Change"]
            ).format({"Price": "{:.2f}", "Change": "{:.2f}%", "Momentum": "{:.2f}", "RSI": "{:.2f}"})
        )
        for idx, (symbol, data) in enumerate(potential_data.items()):
            if idx < 10:  # Limit to top 10
                if data["Data"] is not None:
                    chart = plot_chart(symbol, data["Data"], f"{symbol} - 30 Days")
                    if chart:
                        st.plotly_chart(
                            chart,
                            use_container_width=True,
                            key=f"upcoming_chart_{symbol}_{idx}"
                        )
                    else:
                        st.warning(f"Could not generate chart for {symbol}")
                else:
                    st.warning(f"No data available to generate chart for {symbol}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Economic News Picks
    st.subheader("Stocks to Watch Based on Economic News 💡", divider="blue")
    with st.container():
        st.markdown("<div class='stSection'>", unsafe_allow_html=True)
        econ_data = get_economic_picks()
        econ_df = pd.DataFrame(
            [(k, v["Price"], v["Change"], v["Momentum"], v["RSI"], v["Analyst"], v["Risk"]) for k, v in econ_data.items()]
        )
        econ_df.columns = ["Symbol", "Price", "Change", "Momentum", "RSI", "Analyst", "Risk"]
        st.dataframe(
            econ_df.style.applymap(
                lambda x: "color: #FF4500;" if isinstance(x, float) and x < 0 else "color: #32CD32;" if isinstance(x, float) and x >= 0 else "",
                subset=["Change"]
            ).format({"Price": "{:.2f}", "Change": "{:.2f}%", "Momentum": "{:.2f}", "RSI": "{:.2f}"})
        )
        for idx, (symbol, data) in enumerate(econ_data.items()):
            if data["Data"] is not None:
                chart = plot_chart(symbol, data["Data"], f"{symbol} - 30 Days")
                if chart:
                    st.plotly_chart(
                        chart,
                        use_container_width=True,
                        key=f"econ_chart_{symbol}_{idx}"
                    )
                else:
                    st.warning(f"Could not generate chart for {symbol}")
            else:
                st.warning(f"No data available to generate chart for {symbol}")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main_app()