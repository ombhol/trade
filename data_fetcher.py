# data_fetcher.py
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def ambil_harga_realtime_google(ticker):
    """Mengambil harga saham BEI real-time dari Google Finance."""
    url = f"https://www.google.com/finance/quote/{ticker}:IDX"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            elemen_harga = soup.find('div', {'class': 'ymr60b'})
            if elemen_harga:
                harga_teks = elemen_harga.text.replace("Rp", "").replace(".", "").replace(",", "").strip()
                return float(harga_teks)
    except Exception:
        pass
    return None

def clean_yfinance_columns(df):
    """Pembersihan paksa MultiIndex dari yfinance versi 0.2.40+"""
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

@st.cache_data(ttl=1800)
def ambil_berita_indonesia(ticker):
    daftar_berita = []
    try:
        query = urllib.parse.quote(f"{ticker} saham")
        url = f"https://news.google.com/rss/search?q={query}&hl=id-ID&gl=ID&ceid=ID:id"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            root = ET.fromstring(response.read())
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            if " - " in title: title = title.rsplit(" - ", 1)[0]
            source = item.find('source').text if item.find('source') is not None else "Media"
            pub_date = item.find('pubDate').text[:16] if item.find('pubDate') is not None else ""
            daftar_berita.append({"title": title, "link": item.find('link').text, "source": source, "date": pub_date})
    except Exception: pass
    return daftar_berita

@st.cache_data(ttl=60)
def get_market_data(ticker):
    try:
        df_5m = yf.download(f"{ticker}.JK", period="5d", interval="5m", progress=False)
        df_1d = yf.download(f"{ticker}.JK", period="3mo", interval="1d", progress=False)
        
        df_5m = clean_yfinance_columns(df_5m)
        df_1d = clean_yfinance_columns(df_1d)
            
        return df_5m, df_1d
    except Exception: 
        return pd.DataFrame(), pd.DataFrame()
