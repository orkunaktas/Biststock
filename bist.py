import numpy as np
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

# Streamlit sidebar'dan hisse sembolü alınır
symbol = st.sidebar.text_input("Hisse senedi sembolü", value="ASELS")
st.title(symbol + " Hisse Senedi Grafiği")

# Başlangıç ve bitiş tarihleri Streamlit sidebar'dan alınır
start_date = st.sidebar.date_input("Başlangıç Tarihi", value=datetime(2024, 1, 1))
end_date = st.sidebar.date_input("Bitiş Tarihi", value=datetime.now())

# Yfinance ile sembole göre hisse verisi indirilir
df = yf.download(symbol + '.IS', start=start_date, end=end_date)

# Hisse verileri kontrolü
if df.empty:
    st.error("Hisse verileri alınamadı. Lütfen sembolü kontrol edin veya farklı bir tarih aralığı deneyin.")
else:
    # Hisse senedi kapanış fiyatı grafiği
    st.subheader("Hisse Senedi Trend Grafiği")
    st.line_chart(df["Close"])

    # Hisse senedi hacim grafiği
    st.subheader("Hisse Senedi Hacim Grafiği")
    st.bar_chart(df['Volume'])

    # Hisse senedi fiyat tablosu - Tarihleri ters çevir
    st.subheader("Hisse Senedi Fiyatlar Tablosu")
    st.write(df.sort_index(ascending=False))  # Tarihleri ters sırala

    # Hisse Senedi İstatistikleri
    st.subheader("Hisse Senedi İstatistikleri")
    st.write(f"Son Fiyat: {df['Close'][-1]}")
    st.write(f"52 Haftalık Yüksek: {df['Close'].max()}")
    st.write(f"52 Haftalık Düşük: {df['Close'].min()}")

    # Hareketli Ortalama Hesaplama
    ma_short = df['Close'].rolling(window=20).mean()  # 20 günlük MA
    ma_long = df['Close'].rolling(window=50).mean()   # 50 günlük MA

    # Hareketli Ortalamaların Grafiği
    st.subheader("Hareketli Ortalamalar")
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Kapanış Fiyatı'))
    fig_ma.add_trace(go.Scatter(x=df.index, y=ma_short, mode='lines', name='20 Günlük MA'))
    fig_ma.add_trace(go.Scatter(x=df.index, y=ma_long, mode='lines', name='50 Günlük MA'))
    st.plotly_chart(fig_ma)

    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi

    st.subheader("RSI Grafiği")
    st.line_chart(df['RSI'])

    # Bollinger Bantları Hesaplama
    window = 20
    std = df['Close'].rolling(window).std()
    df['Bollinger_Upper'] = ma_short + (std * 2)
    df['Bollinger_Lower'] = ma_short - (std * 2)

    st.subheader("Bollinger Bantları")
    fig_bollinger = go.Figure()
    fig_bollinger.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Kapanış Fiyatı'))
    fig_bollinger.add_trace(go.Scatter(x=df.index, y=ma_short, mode='lines', name='Orta Bant (20 Günlük MA)', line=dict(color='orange')))  # Orta bant eklendi
    fig_bollinger.add_trace(go.Scatter(x=df.index, y=df['Bollinger_Upper'], mode='lines', name='Üst Bant'))
    fig_bollinger.add_trace(go.Scatter(x=df.index, y=df['Bollinger_Lower'], mode='lines', name='Alt Bant'))
    st.plotly_chart(fig_bollinger)

    # Mum Grafiği
    if st.sidebar.checkbox("Mum Grafiği Göster"):
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                               open=df['Open'],
                                               high=df['High'],
                                               low=df['Low'],
                                               close=df['Close'])])
        st.plotly_chart(fig)

    # Kullanıcı geri bildirimi
    feedback = st.sidebar.text_area("Geri Bildirim veya Öneri bırakın")
    if st.sidebar.button("Gönder"):
        st.sidebar.success("Geri bildiriminiz için teşekkür ederiz!")
