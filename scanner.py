# scanner.py
import streamlit as st
import yfinance as yf
import concurrent.futures
from data_fetcher import clean_yfinance_columns
from indicators import calculate_indicators

def proses_satu_saham(ticker):
    try:
        df = yf.download(f"{ticker}.JK", period="5d", interval="5m", progress=False)
        df = clean_yfinance_columns(df)
        if df.empty: return None
        
        df = calculate_indicators(df)
        df_clean = df.dropna(subset=['VWAP', 'EMA20', 'Turnover_MA20'])
        if df_clean.empty: return None
        
        curr = df_clean.iloc[-1]
        if curr['Close'] <= 50 or curr['Turnover_MA20'] < 100000000:
            return None
            
        skor = 0
        if curr['Close'] > curr['VWAP']: skor += 30
        if curr['Close'] > curr['EMA20']: skor += 20
        if 40 < curr['RSI'] < 65: skor += 20
        elif curr['RSI'] >= 70: skor -= 20
        
        if curr['Volume'] > (curr['Vol_MA20'] * 3): skor += 30
        elif curr['Volume'] > curr['Vol_MA20']: skor += 10
        
        if skor >= 60:
            # Ekstraksi indikator lanjutan untuk mesin pemilah strategi per sesi
            high_today = float(df_clean[df_clean['Date'] == curr['Date']]['High'].max())
            vol_spike = float(curr['Volume'] / curr['Vol_MA20']) if curr['Vol_MA20'] > 0 else 1.0
            
            return {
                "ticker": ticker, 
                "skor": skor, 
                "harga": float(curr['Close']), 
                "vwap": float(curr['VWAP']),
                "rsi": float(curr['RSI']),
                "vol_spike": vol_spike,
                "high_today": high_today
            }
    except Exception:
        pass
    return None

@st.cache_data(ttl=60) 
def scan_top_saham(watchlist):
    hasil_scan = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(proses_satu_saham, ticker): ticker for ticker in watchlist}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                hasil_scan.append(result)
    return sorted(hasil_scan, key=lambda x: x['skor'], reverse=True)[:3]
