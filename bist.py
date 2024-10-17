import numpy as np
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit sidebar'dan hisse sembolü alınır
symbol = st.sidebar.text_input("Hisse senedi sembolü", value="ASELS")
st.title(symbol + " Hisse Senedi Grafiği")

# Başlangıç ve bitiş tarihleri Streamlit sidebar'dan alınır
start_date = st.sidebar.date_input("Başlangıç Tarihi", value=datetime(2024, 1, 1))
end_date = st.sidebar.date_input("Bitiş Tarihi", value=datetime.now())  # Parantez düzeltildi

# Yfinance ile sembole göre hisse verisi indirilir
df = yf.download(symbol + '.IS', start=start_date, end=end_date)

# Hisse senedi kapanış fiyatı grafiği
st.subheader("Hisse Senedi Trend Grafiği")
st.line_chart(df["Close"])  # Kapanış fiyatları

# Hisse senedi fiyat tablosu
st.subheader("Hisse Senedi Fiyatlar Tablosu")
st.write(df)
