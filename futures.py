import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import requests
from datetime import datetime
from transformers import pipeline

# --- Page Config ---
st.set_page_config(
    page_title="Futures Dashboard",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Dashboard Settings")
    selected_commodity = st.selectbox(
        "Select Commodity",
        options=["Oil", "Gold", "Wheat", "Natural Gas", "Copper"]
    )
    selected_timeframe = st.selectbox(
        "Select Timeframe",
        options=["1 Day", "1 Week", "1 Month"]
    )

# --- Ticker Mapping ---
commodity_tickers = {
    "Oil": "CL=F",
    "Gold": "GC=F",
    "Wheat": "ZW=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F"
}

# --- Price Fetching ---
def get_latest_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    todays_data = ticker.history(period="1d")
    return todays_data['Close'].iloc[0]

# --- Historical Data Fetching ---
def get_historical_data(ticker_symbol, timeframe='1 Day'):
    ticker = yf.Ticker(ticker_symbol)
    if timeframe == '1 Day':
        return ticker.history(period="1d", interval="5m")
    elif timeframe == '1 Week':
        return ticker.history(period="5d", interval="1h")
    elif timeframe == '1 Month':
        return ticker.history(period="1mo", interval="1d")
    else:
        return ticker.history(period="1d", interval="5m")

# --- NewsAPI Fetch ---
def get_news_headlines(query):
    api_key = "c45d14608c4e4a03a9b83026b15aadc9"  # Replace with your own key if needed
    url = (
        f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        return []

# --- AI Summarizer ---
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# --- Display Header ---
st.title("🌍 Futures Intelligence Dashboard")
st.caption(f"Last Updated: {datetime.now().strftime('%B %d, %Y – %H:%M:%S')}")

# --- Display Live Price ---
st.subheader("📢 Today's Top Futures Insights")
selected_ticker = commodity_tickers.get(selected_commodity)
latest_price = get_latest_price(selected_ticker)
st.metric(label=f"{selected_commodity} Latest Price", value=f"${latest_price:,.2f}")

# --- Display Chart ---
st.subheader("📈 Interactive Price Chart")
historical_data = get_historical_data(selected_ticker, selected_timeframe)

if not historical_data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data['Close'],
        mode='lines',
        name=f'{selected_commodity} Price'
    ))

    fig.update_layout(
        title=f'{selected_commodity} Futures Price Over {selected_timeframe}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No historical data available.")

# --- News Section ---
st.subheader("📰 Latest Commodity News")
news_articles = get_news_headlines(selected_commodity)

if news_articles:
    for article in news_articles:
        st.markdown(f"**[{article['title']}]({article['url']})**")
        st.caption(f"{article['source']['name']} • {article['publishedAt'][:10]}")
        st.write(article['description'])
        st.markdown("---")
else:
    st.write("No news available at the moment.")

st.caption("Powered by NewsAPI.org")

# --- AI Summary Section ---
st.subheader("🤖 News Analysis & Insights")
news_text = " "._

