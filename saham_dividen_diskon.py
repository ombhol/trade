# saham_dividen_diskon.py
import streamlit as st
import yfinance as yf
import concurrent.futures
from data_fetcher import clean_yfinance_columns

def proses_saham_diskon(ticker):
    try:
        # 1. Ambil data 1 bulan untuk memastikan kita dapat data 1 minggu bursa penuh (minimal 6 hari)
        df = yf.download(f"{ticker}.JK", period="1mo", interval="1d", progress=False)
        df = clean_yfinance_columns(df)
        
        if df.empty or len(df) < 6: 
            return None
        
        # Harga hari ini vs Harga 1 Minggu Lalu (5 hari bursa sebelumnya)
        harga_skrg = float(df['Close'].iloc[-1])
        harga_minggu_lalu = float(df['Close'].iloc[-6])
        
        # 2. Hitung persentase penurunan
        penurunan_persen = ((harga_skrg - harga_minggu_lalu) / harga_minggu_lalu) * 100
        
        # Filter HANYA yang turun lebih dari 5%
        if penurunan_persen <= -5.0:
            # 4. Titik Support & Resistan dari range 1 minggu terakhir
            high_1w = float(df['High'].iloc[-6:].max())
            low_1w = float(df['Low'].iloc[-6:].min())
            
            return {
                "ticker": ticker,
                "harga_sekarang": harga_skrg,
                "harga_minggu_lalu": harga_minggu_lalu,
                "penurunan_persen": penurunan_persen,
                "support": low_1w,
                "resistan": high_1w
            }
    except Exception:
        pass
    return None

@st.cache_data(ttl=300) # Data di-cache 5 menit agar tidak membebani server
def scan_saham_dividen(watchlist):
    hasil = []
    # Screening paralel agar proses pencarian cepat
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(proses_saham_diskon, t): t for t in watchlist}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res: 
                hasil.append(res)
    
    # 5. Urutkan dari yang penurunannya paling dalam (paling minus), ambil Top 3
    hasil_sorted = sorted(hasil, key=lambda x: x['penurunan_persen'])
    return hasil_sorted[:3]
