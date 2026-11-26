import math
import re

import streamlit as st
import yfinance as yf


def valid_symbol(symbol):
    return bool(re.fullmatch(r'[A-Z0-9&._-]{1,30}\.(NS|BO)', symbol))


@st.cache_data(ttl=120, show_spinner=False)
def quote(symbol):
    try:
        data = yf.Ticker(symbol).history(period='5d', auto_adjust=False)
        row = data['Close'].dropna()
        price = float(row.iloc[-1])
        if math.isfinite(price) and price > 0:
            return price, str(row.index[-1])
        return None, None
    except Exception:
        return None, None
