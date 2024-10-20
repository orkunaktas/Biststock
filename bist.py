import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Streamlit sidebar'dan hisse sembolü alınır
symbol = st.sidebar.text_input("Hisse senedi sembolü", value="ASELS")
st.title(f"{symbol} Hisse Senedi Grafiği")

# Başlangıç ve bitiş tarihleri Streamlit sidebar'dan alınır
start_date = st.sidebar.date_input("Başlangıç Tarihi", value=datetime(2024, 1, 1))
end_date = st.sidebar.date_input("Bitiş Tarihi", value=datetime.now())

# Yfinance ile sembole göre hisse verisi indirilir
df = yf.download(symbol + '.IS', start=start_date, end=end_date)

# Hisse verileri kontrolü
if df.empty:
    st.error("Hisse verileri alınamadı. Lütfen sembolü kontrol edin veya farklı bir tarih aralığı deneyin.")
else:
    # Grafik tipi seçme seçenekleri (candle, line, mountain)
    chart_type = st.sidebar.selectbox("Grafik Türünü Seçin", ["line", "candle", "mountain"])

    # Hisse senedi kapanış fiyatı ve hacim grafiği
    st.subheader("Hisse Senedi Trend ve Hacim Grafikleri")

    # İlk olarak trend grafiğini geniş bir formatta çizelim
    fig = go.Figure()

    # Grafik türü seçimine göre grafiği çizdirme
    if chart_type == "line":
        # Kapanış fiyatı çizgisel grafik
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Kapanış Fiyatı', line=dict(color='blue')))
    elif chart_type == "candle":
        # Mum grafik
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                     name='Mum Grafik'))
    elif chart_type == "mountain":
        # Dağ grafik
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', mode='lines', name='Mountain', line=dict(color='green')))

    # Hareketli Ortalama Hesaplama (SMA ve EMA)
    ma_short = df['Close'].rolling(window=20).mean()  # 20 günlük SMA
    ema_long = df['Close'].ewm(span=50, adjust=False).mean()  # 50 günlük EMA

    # Bollinger Bantları
    window = 20
    std = df['Close'].rolling(window).std()
    df['Bollinger_Upper'] = ma_short + (std * 2)
    df['Bollinger_Lower'] = ma_short - (std * 2)

    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi

    # MACD Hesaplama
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()  # 12-günlük EMA
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()  # 26-günlük EMA
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    df['MACD'] = macd
    df['Signal_Line'] = signal

    # Average True Range (ATR) Hesaplama
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = high_low.combine(high_close, max).combine(low_close, max)
    atr = tr.rolling(window=14).mean()
    df['ATR'] = atr

    # Kullanıcının göstermek istediği indikatörler
    indicators = st.sidebar.multiselect("Gösterilecek İndikatörler", 
                                        ["SMA (20)", "EMA (50)", "RSI", "MACD", "Bollinger Bands", "ATR"])

    # Ana grafik: Kapanış fiyatı ve seçilen indikatörler
    if "SMA (20)" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=ma_short, mode='lines', name='SMA (20)', line=dict(color='orange')))
    
    if "EMA (50)" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=ema_long, mode='lines', name='EMA (50)', line=dict(color='purple')))

    if "Bollinger Bands" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=df['Bollinger_Upper'], mode='lines', name='Bollinger Üst Bant', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=df.index, y=df['Bollinger_Lower'], mode='lines', name='Bollinger Alt Bant', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=df.index, y=ma_short, mode='lines', name='Bollinger Orta Bant', line=dict(color='orange')))  # Orta bant ekleme

    # Geniş ve uzun bir trend grafiği
    fig.update_layout(
        height=500,  # Yükseklik ayarı (trendi daha geniş yapmak için)
        margin=dict(l=20, r=20, t=20, b=20),  # Kenar boşlukları daraltılmış
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)  # Legend konumu sol üst köşe
    )
    st.plotly_chart(fig)

    # Hacim grafiği: Daha kısa ve trend grafiği ile aynı genişlikte olacak
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Hacim'))

    # Daha kısa hacim grafiği
    fig_volume.update_layout(
        height=200,  # Daha kısa hacim grafiği
        margin=dict(l=20, r=20, t=20, b=20),  # Kenar boşlukları daraltılmış
    )
    st.plotly_chart(fig_volume)

    # Hisse fiyatları tablosunu gösterme
    st.subheader("Hisse Senedi Fiyatları")
    st.dataframe(df)

    # RSI grafiği
    if "RSI" in indicators:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
        fig_rsi.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title='RSI', range=[0, 100]),
            xaxis_title='Tarih',
            yaxis_title='RSI Değeri',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)  # Legend konumu sol üst köşe
        )
        st.plotly_chart(fig_rsi)

    # MACD grafiği
    if "MACD" in indicators:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='green')))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='red')))
        fig_macd.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title='MACD'),
            xaxis_title='Tarih',
            yaxis_title='MACD Değeri',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)  # Legend konumu sol üst köşe
        )
        st.plotly_chart(fig_macd)

    # ATR grafiği
    if "ATR" in indicators:
        fig_atr = go.Figure()
        fig_atr.add_trace(go.Scatter(x=df.index, y=df['ATR'], mode='lines', name='ATR', line=dict(color='purple')))
        fig_atr.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title='ATR'),
            xaxis_title='Tarih',
            yaxis_title='ATR Değeri',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)  # Legend konumu sol üst köşe
        )
        st.plotly_chart(fig_atr)

    # Aylık yüzdelik değişim grafiği
    st.subheader("Aylık Yüzdelik Değişim Grafiği")
    monthly_return = df['Close'].resample('M').ffill().pct_change() * 100
    colors = np.where(monthly_return > 0, 'green', 'red')  # Pozitif değişim yeşil, negatif değişim kırmızı
    fig_monthly_return = go.Figure()
    fig_monthly_return.add_trace(go.Bar(x=monthly_return.index, y=monthly_return, marker_color=colors))
    fig_monthly_return.update_layout(
        title="Aylık Yüzdelik Değişim",
        xaxis_title="Tarih",
        yaxis_title="Yüzde Değişim",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_monthly_return)
