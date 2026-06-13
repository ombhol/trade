# saham_dividen_diskon.py
import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures

def proses_saham_diskon(ticker):
    try:
        # 1. Ambil data 1 bulan untuk jaga-jaga hari libur panjang
        df = yf.download(f"{ticker}.JK", period="1mo", interval="1d", progress=False)
        
        # 2. Tangani format tabel versi terbaru dari Yahoo Finance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 3. Bersihkan data kosong saat market sedang berjalan
        df = df.dropna(subset=['Close', 'High', 'Low'])
        
        # Pastikan ada cukup data
        if len(df) < 10: 
            return None
        
        # 4. [PERBAIKAN CERDAS]: Tarik 10 Hari Bursa Terakhir (2 Minggu)
        # Agar puncak harga sebelum dibanting PASTI tertangkap.
        df_pantau = df.tail(10)
        
        harga_sekarang = float(df_pantau['Close'].iloc[-1])
        
        # Mencari pucuk (titik tertinggi) dalam 2 minggu terakhir sebelum jatuh
        harga_puncak = float(df_pantau['High'].max())
        
        # Harga closing tepat 1 minggu (5 hari bursa) lalu
        harga_minggu_lalu = float(df_pantau['Close'].iloc[-6])
        
        # 5. Hitung Penurunan dengan 2 Skenario (Ambil yang paling parah)
        # Skenario A: Diskon dari pucuknya
        penurunan_dari_pucuk = ((harga_sekarang - harga_puncak) / harga_puncak) * 100
        # Skenario B: Diskon dari harga minggu lalu
        penurunan_mingguan = ((harga_sekarang - harga_minggu_lalu) / harga_minggu_lalu) * 100
        
        # Ambil persentase minus yang paling dalam
        diskon_terdalam = min(penurunan_dari_pucuk, penurunan_mingguan)
        
        # 6. Filter: Hanya ambil yang anjlok lebih dari 5%
        if diskon_terdalam <= -5.0:
            
            # Tentukan harga acuan mana yang membuat dia jatuh paling dalam untuk ditampilkan
            harga_referensi = harga_puncak if diskon_terdalam == penurunan_dari_pucuk else harga_minggu_lalu
            label_referensi = "Harga Pucuk (2w)" if diskon_terdalam == penurunan_dari_pucuk else "Harga (1w lalu)"
            
            return {
                "ticker": ticker,
                "harga_sekarang": harga_sekarang,
                "harga_minggu_lalu": harga_referensi,
                "label_referensi": label_referensi,
                "penurunan_persen": diskon_terdalam,
                "support": float(df_pantau['Low'].min()),
                "resistan": float(df_pantau['High'].max())
            }
    except Exception:
        pass
    return None

@st.cache_data(ttl=60)
def scan_saham_dividen(watchlist):
    hasil = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(proses_saham_diskon, t): t for t in watchlist}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res: 
                hasil.append(res)
    
    # 7. Urutkan mulai dari yang paling hancur/minus terdalam
    hasil_sorted = sorted(hasil, key=lambda x: x['penurunan_persen'])
    
    # [PERBAIKAN]: Tampilkan TOP 10 
    return hasil_sorted[:10]
