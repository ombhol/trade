# saham_dividen_diskon.py
import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures

def proses_saham_diskon(ticker):
    try:
        # 1. Ambil data 15 hari untuk jaminan ketersediaan data, abaikan hari libur
        df = yf.download(f"{ticker}.JK", period="15d", interval="1d", progress=False)
        
        # 2. Wajib untuk mengatasi perubahan format struktur dari YFinance versi terbaru
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 3. Buang data kosong/blank (Sering terjadi saat market live/jam bursa berjalan)
        df = df.dropna(subset=['Close', 'High', 'Low'])
        
        # Jika riwayat trading kurang dari 5 hari, berarti data cacat, lewati.
        if len(df) < 5: 
            return None
        
        # 4. KUNCI UTAMA: Ambil PASTI 5 hari bursa paling terakhir (Representasi Mutlak 1 Minggu)
        df_1_minggu = df.tail(5)
        
        harga_sekarang = float(df_1_minggu['Close'].iloc[-1])
        
        # Ambil harga tertinggi dalam 5 hari tersebut sebagai titik awal jatuhnya harga
        # (Ini yang akan menangkap diskon 14% MPMX jika jatuh dari puncaknya minggu ini)
        harga_puncak_1w = float(df_1_minggu['High'].max())
        
        # 5. Perhitungan Penurunan Murni
        penurunan_persen = ((harga_sekarang - harga_puncak_1w) / harga_puncak_1w) * 100
        
        # Filter ketat: Hanya yang rontok lebih dari 5%
        if penurunan_persen <= -5.0:
            
            # Support dan Resistan paling presisi ditarik dari pergerakan minggu ini
            support_1w = float(df_1_minggu['Low'].min())
            resistan_1w = float(df_1_minggu['High'].max())
            
            return {
                "ticker": ticker,
                "harga_sekarang": harga_sekarang,
                # Variabel ini akan masuk ke UI main.py Anda sebagai referensi harga awal sebelum jatuh
                "harga_minggu_lalu": harga_puncak_1w, 
                "penurunan_persen": penurunan_persen,
                "support": support_1w,
                "resistan": resistan_1w
            }
    except Exception as e:
        # Skip error diam-diam agar thread tetap memproses saham lain
        pass
    return None

@st.cache_data(ttl=60) # Auto-refresh tiap 1 menit
def scan_saham_dividen(watchlist):
    hasil = []
    
    # Scanner mengeksekusi 10 saham secara serentak agar cepat
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(proses_saham_diskon, t): t for t in watchlist}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res: 
                hasil.append(res)
    
    # 6. Urutkan mulai dari saham dengan penurunan (minus) paling tajam/dalam
    hasil_sorted = sorted(hasil, key=lambda x: x['penurunan_persen'])
    
    # Kembalikan hanya Top 3 yang paling hancur
    return hasil_sorted[:3]
