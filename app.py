import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="Pro Finans Terminali", layout="wide")
st.title("🚀 Pro Borsa: Takip, Kar/Zarar ve Alarm")

# 1. VARLIK LİSTESİ
varliklar = {
    "Dolar (USD/TL)": "USDTRY=X",
    "Euro (EUR/TL)": "EURTRY=X",
    "Gram Altın (TL)": "GAU=X", # Bazı sağlayıcılarda farklılık gösterebilir
    "Altın (Ons)": "GC=F",
    "Gümüş (Ons)": "SI=F",
    "Platin": "PL=F",
    "Paladyum": "PA=F",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD"
}

# 2. YAN PANEL - KONTROL VE HESAPLAMA
st.sidebar.header("📋 Portföy Yönetimi")
secilen_etiket = st.sidebar.selectbox("İşlem Yapılacak Varlık:", list(varliklar.keys()))
alis_fiyati = st.sidebar.number_input("Alış Fiyatınız (Birim):", min_value=0.0, value=0.0)
miktar = st.sidebar.number_input("Elinizdeki Miktar:", min_value=0.0, value=1.0)

st.sidebar.markdown("---")
st.sidebar.header("🔔 Fiyat Alarmı")
alarm_fiyati = st.sidebar.number_input("Alarm Seviyesi Belirle:", min_value=0.0, value=0.0)

# 3. VERİ ÇEKME
def anlik_fiyat_al(sembol):
    data = yf.Ticker(sembol)
    return data.history(period="1d")['Close'].iloc[-1]

try:
    sembol = varliklar[secilen_etiket]
    guncel_fiyat = anlik_fiyat_al(sembol)
    
    # 4. KAR/ZARAR HESABI
    toplam_maliyet = miktar * alis_fiyati
    guncel_deger = miktar * guncel_fiyat
    kar_zarar_tutari = guncel_deger - toplam_maliyet
    kar_zarar_orani = ((guncel_fiyat - alis_fiyati) / alis_fiyati * 100) if alis_fiyati > 0 else 0.0

    # ÜST METRİKLER
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anlık Fiyat", f"{guncel_fiyat:,.2f}")
    c2.metric("Güncel Bakiyeniz", f"{guncel_deger:,.2f}")
    
    if alis_fiyati > 0:
        c3.metric("Kar/Zarar (Tutar)", f"{kar_zarar_tutari:,.2f}", delta=f"{kar_zarar_tutari:,.2f}")
        c4.metric("Kar/Zarar (%)", f"%{kar_zarar_orani:.2f}", delta=f"{kar_zarar_orani:.2f}%")

    # 5. ALARM KONTROLÜ
    if alarm_fiyati > 0:
        if guncel_fiyat >= alarm_fiyati:
            st.error(f"🚨 ALARM: {secilen_etiket} hedef fiyat olan {alarm_fiyati} seviyesine ulaştı!")
            st.balloons() # Görsel kutlama/uyarı
        else:
            st.info(f"💡 Alarm Kurulu: Fiyat {alarm_fiyati} seviyesine ulaştığında uyarılacaksınız.")

    # 6. GRAFİK (Son 24 Saatlik Değişim)
    st.markdown("---")
    df = yf.download(sembol, period="1d", interval="15m")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=f"{secilen_etiket} - 15 Dakikalık Mum Grafiği", template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning("Veriler güncellenirken bir hata oluştu. Piyasalar kapalı olabilir veya bağlantı hatası.")

# OTO-YENİLEME (Opsiyonel)
st.caption("Uygulama her manuel işlemde verileri yeniler. Otomatik canlı takip için sayfayı yenileyebilirsiniz.")
