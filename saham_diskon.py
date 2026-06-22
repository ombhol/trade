# saham_diskon.py
import streamlit as st
import pandas as pd
import yfinance as yf

# Menggunakan cache agar tidak perlu loading lama setiap kali pindah tab
# Data fundamental hanya ditarik 1x dan disimpan dalam memori (cache)
@st.cache_data(ttl=3600) 
def get_fundamental_data(tickers):
    hasil = []
    for ticker in tickers:
        try:
            # Tambahkan .JK untuk format Yahoo Finance Indonesia
            t_jk = f"{ticker}.JK"
            info = yf.Ticker(t_jk).info
            
            # Ekstraksi Data Fundamental
            pbv = info.get('priceToBook', 0)
            per = info.get('trailingPE', 0)
            roe = info.get('returnOnEquity', 0)
            der = info.get('debtToEquity', 0) # yfinance mengembalikan persentase, misal 40 = 0.4x
            cr = info.get('currentRatio', 0)
            div_yield = info.get('dividendYield', 0)
            div_rp = info.get('trailingAnnualDividendRate') or info.get('dividendRate') or 0 # <--- TAMBAHAN DEVIDEN RP
            eps = info.get('trailingEps', 0)
            harga = info.get('previousClose', 0)

            # Membersihkan nilai None (jika data tidak tersedia di API)
            pbv = pbv if pbv is not None else 0
            per = per if per is not None else 0
            roe = roe if roe is not None else 0
            der = (der / 100) if der is not None else 0 # Konversi ke satuan kali (x)
            cr = cr if cr is not None else 0
            div_yield = div_yield if div_yield is not None else 0
            div_rp = div_rp if div_rp is not None else 0
            eps = eps if eps is not None else 0
            
            # --- SISTEM SCORING BERDASARKAN KRITERIA USER ---
            skor = 0
            if 0 < pbv < 1.0: skor += 1   # Kriteria 1: PBV < 1
            if 0 < per < 15: skor += 1    # Kriteria 1: PER < 15
            if roe > 0.10: skor += 1      # Kriteria 2: ROE > 10%
            if eps > 0: skor += 1         # Kriteria 2: Laba Positif (Tidak Minus)
            if 0 <= der < 1: skor += 1    # Kriteria 3: DER < 1 (Utang Terkontrol)
            if cr > 1: skor += 1          # Kriteria 3: Current Ratio > 1
            if div_yield > 0.04: skor += 1 # Kriteria 4: Div Yield > 4% (Kompensasi Menunggu)
            
            hasil.append({
                'Ticker': ticker,
                'Harga': harga,
                'PBV (x)': round(pbv, 2),
                'PER (x)': round(per, 2),
                'ROE (%)': round(roe * 100, 2),
                'DER (x)': round(der, 2),
                'Current Ratio (x)': round(cr, 2),
                'Dividen (Rp)': round(div_rp, 2), # <--- KOLOM BARU DI TABEL
                'Div Yield (%)': round(div_yield * 100, 2),
                'EPS': round(eps, 2),
                'Skor Validasi': skor
            })
        except Exception:
            # Lewati jika error saat menarik data
            continue
            
    return pd.DataFrame(hasil)

# Menggunakan *args, **kwargs agar tidak error jika main.py mengirim variabel lain
def render_saham_diskon_tab(*args, **kwargs):
    st.subheader("🕵️‍♂️ Fundamental Value Screener (Saham Diskon)")
    
    # 1. Daftar Saham yang Akan Dipantau Sesuai Request User
    target_saham = [
        "MPMX", "ASGR", "LPPF", "ROTI", "CNMA", "RALS", "TAPG", "UNIC", 
        "KKGI", "CITA", "PTBA", "UNVR", "SPTO", "FWCT", "LPIN", "TLDN", 
        "BSSR", "ADRO", "MARK", "TPMA", "SGRO", "TOTL", "ARNA", "POWR", 
        "HRXA", "NRCA", "MSTI", "EAST", "ACES", "TOTO", "SIDO", "AUTO", "TLKM"
    ]
    
    st.write(f"Memantau **{len(target_saham)}** emiten pilihan berdasarkan kriteria Value Investing:")
    
    with st.expander("ℹ️ Parameter Kriteria yang Digunakan", expanded=False):
        st.markdown("""
        1. **Valuasi (Harga Diskon):** PBV < 1, PER < 15
        2. **Profitabilitas (Mesin Uang):** ROE > 10%, Laba Bersih/EPS Positif
        3. **Kesehatan Keuangan (Keamanan):** DER < 1 (Utang kecil), Current Ratio > 1 (Aman jangka pendek)
        4. **Bonus Menunggu:** Dividend Yield menarik (> 4%)
        """)

    with st.spinner("⏳ Menarik laporan keuangan terbaru dari server... (Membutuhkan waktu 10-20 detik)"):
        df_hasil = get_fundamental_data(target_saham)
        
    if df_hasil.empty:
        st.error("❌ Gagal menarik data fundamental. Periksa koneksi internet Anda.")
        return
        
    # Urutkan dari Skor Tertinggi (Paling Sempurna), lalu PBV terendah
    df_hasil = df_hasil.sort_values(by=['Skor Validasi', 'PBV (x)'], ascending=[False, True]).reset_index(drop=True)
    
    # --- 2. REKOMENDASI PEMANTAUAN PALING BAGUS ---
    top_saham = df_hasil.iloc[0]
    st.success(f"### 🏆 Top Rekomendasi: **{top_saham['Ticker']}** (Skor Lulus: {top_saham['Skor Validasi']}/7 Kriteria)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valuasi Diskon", f"PBV {top_saham['PBV (x)']}x", f"PER {top_saham['PER (x)']}x", delta_color="inverse")
    col2.metric("Profitabilitas", f"ROE {top_saham['ROE (%)']}%", f"EPS Rp {top_saham['EPS']:,.0f}")
    col3.metric("Kesehatan", f"DER {top_saham['DER (x)']}x", f"CR {top_saham['Current Ratio (x)']}x", delta_color="inverse")
    col4.metric("Kompensasi", f"Yield {top_saham['Div Yield (%)']}%", f"Rp {top_saham['Dividen (Rp)']:,.0f}/lembar")

    st.markdown("---")
    st.markdown("### 📋 Papan Peringkat Screening (Diurutkan dari Terbaik)")
    
    # Fungsi styling warna untuk sel di dalam tabel
    def highlight_kriteria(row):
        styles = [''] * len(row)
        
        # Temukan index dari setiap kolom
        idx_pbv = row.index.get_loc('PBV (x)')
        idx_per = row.index.get_loc('PER (x)')
        idx_roe = row.index.get_loc('ROE (%)')
        idx_der = row.index.get_loc('DER (x)')
        idx_cr = row.index.get_loc('Current Ratio (x)')
        idx_div_rp = row.index.get_loc('Dividen (Rp)') # <--- TAMBAHAN INDEX
        idx_div = row.index.get_loc('Div Yield (%)')
        idx_eps = row.index.get_loc('EPS')
        
        # Hijau jika lulus kriteria
        if 0 < row['PBV (x)'] <= 1.0: styles[idx_pbv] = 'background-color: rgba(30, 70, 32, 0.5)'
        if 0 < row['PER (x)'] <= 15: styles[idx_per] = 'background-color: rgba(30, 70, 32, 0.5)'
        if row['ROE (%)'] >= 10: styles[idx_roe] = 'background-color: rgba(30, 70, 32, 0.5)'
        if 0 <= row['DER (x)'] < 1: styles[idx_der] = 'background-color: rgba(30, 70, 32, 0.5)'
        if row['Current Ratio (x)'] >= 1: styles[idx_cr] = 'background-color: rgba(30, 70, 32, 0.5)'
        if row['EPS'] > 0: styles[idx_eps] = 'background-color: rgba(30, 70, 32, 0.5)'
        
        # Highlight Deviden RP dan Yield secara bersamaan jika yield > 4%
        if row['Div Yield (%)'] >= 4: 
            styles[idx_div] = 'background-color: rgba(30, 70, 32, 0.5)'
            styles[idx_div_rp] = 'background-color: rgba(30, 70, 32, 0.5)'
        
        return styles
        
    # Tampilkan DataFrame dengan formatting
    st.dataframe(
        df_hasil.style.apply(highlight_kriteria, axis=1).format({
            'Harga': "Rp {:,.0f}",
            'PBV (x)': "{:.2f}",
            'PER (x)': "{:.2f}",
            'ROE (%)': "{:.2f}%",
            'DER (x)': "{:.2f}",
            'Current Ratio (x)': "{:.2f}",
            'Dividen (Rp)': "Rp {:,.0f}", # <--- FORMAT RUPIAH
            'Div Yield (%)': "{:.2f}%",
            'EPS': "Rp {:,.0f}"
        }),
        use_container_width=True,
        hide_index=True,
        height=600 # Memberikan ruang scroll untuk 33 saham
    )
    
    st.caption("💡 **Tips Membaca:** Angka dengan latar belakang **Hijau** berarti saham tersebut LULUS pada kriteria yang Anda tentukan.")
