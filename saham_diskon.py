# saham_diskon.py
import streamlit as st
import pandas as pd
from data_fetcher import get_market_data, ambil_harga_realtime # Pastikan modul ini diimpor

def render_saham_diskon_tab(daftar_pantauan):
    st.subheader("🏷️ Radar Saham Diskon (Top 10)")
    
    if not daftar_pantauan:
        st.warning("⚠️ Daftar pantauan kosong. Silakan isi daftar saham di sidebar.")
        return

    # Menambahkan indikator loading karena melooping banyak saham membutuhkan waktu
    with st.spinner("Memindai tingkat diskon dari seluruh daftar pantauan..."):
        hasil_scan = []
        
        # 1. Pemantauan pada daftar pantauan
        for ticker in daftar_pantauan:
            df_5m, df_1d = get_market_data(ticker)
            
            if df_1d.empty or df_5m.empty:
                continue
                
            # Ambil harga real-time atau gunakan close terakhir jika API gagal
            harga_sekarang = ambil_harga_realtime(ticker)
            if not harga_sekarang or harga_sekarang == 0:
                harga_sekarang = float(df_5m['Close'].iloc[-1])
                
            # Kalkulasi Pucuk 5 Hari Terakhir (Daily)
            high_5d = float(df_1d['High'].tail(5).max())
            diskon_pucuk = ((high_5d - harga_sekarang) / high_5d) * 100 if high_5d > 0 else 0
            
            # Hanya proses saham yang sedang turun/diskon (> 0%)
            if diskon_pucuk > 0:
                curr_5m = df_5m.dropna(subset=['VWAP', 'EMA20']).iloc[-1]
                vwap_val = float(curr_5m['VWAP'])
                rsi_val = float(curr_5m['RSI'])
                
                status_vwap = "Under VWAP 🔥" if harga_sekarang < vwap_val else "Above VWAP ⚠️"
                
                hasil_scan.append({
                    'Ticker': ticker,
                    'Harga': harga_sekarang,
                    'High_5D': high_5d,
                    'Diskon (%)': round(diskon_pucuk, 2),
                    'VWAP': vwap_val,
                    'Status VWAP': status_vwap,
                    'RSI 5m': round(rsi_val, 2)
                })
        
        if not hasil_scan:
            st.info("Belum ada saham dari daftar pantauan yang masuk area diskon saat ini.")
            return
            
        # 3. Urutkan dari yang diskon paling tinggi
        df_hasil = pd.DataFrame(hasil_scan)
        df_hasil = df_hasil.sort_values(by='Diskon (%)', ascending=False).reset_index(drop=True)
        
        # 4. Menampilkan max 10 saham dengan urutan diskon tertinggi
        df_top_10 = df_hasil.head(10)
        
        # 2. Rekomendasi pemantauan paling bagus & alasannya
        # Logika: Cari saham di Top 10 yang harganya di bawah VWAP dan RSI-nya terendah (Jenuh Jual)
        kandidat_ideal = df_top_10[df_top_10['Harga'] < df_top_10['VWAP']]
        
        if not kandidat_ideal.empty:
            # Jika ada yang Under VWAP, pilih yang RSI-nya paling oversold
            rekomendasi = kandidat_ideal.sort_values(by='RSI 5m', ascending=True).iloc[0]
        else:
            # Jika tidak ada yang Under VWAP, ambil saja murni diskon tertinggi
            rekomendasi = df_top_10.iloc[0]
            
        # --- UI LAYOUT REKOMENDASI UTAMA ---
        st.markdown("### 🏆 Rekomendasi Pantauan Terbaik")
        st.success(f"**{rekomendasi['Ticker']}** adalah kandidat diskon terbaik untuk diakumulasi saat ini.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Harga Saat Ini", f"Rp {rekomendasi['Harga']:,.0f}")
            st.write(f"📉 **Diskon dari Pucuk:** {rekomendasi['Diskon (%)']}%")
        with col2:
            st.metric("RSI Intraday (5m)", f"{rekomendasi['RSI 5m']}")
            if rekomendasi['RSI 5m'] < 40:
                st.write("🛒 **Status:** Oversold (Jenuh Jual)")
            elif rekomendasi['RSI 5m'] > 70:
                st.write("🚨 **Status:** Overbought (Jenuh Beli)")
            else:
                st.write("⚖️ **Status:** Netral")
        with col3:
            jarak_vwap = (abs(rekomendasi['VWAP'] - rekomendasi['Harga']) / rekomendasi['VWAP']) * 100
            st.metric("VWAP Harian", f"Rp {rekomendasi['VWAP']:,.0f}")
            if rekomendasi['Harga'] < rekomendasi['VWAP']:
                st.write(f"🔥 **Under VWAP:** Murah -{jarak_vwap:.1f}%")
            else:
                st.write(f"⚠️ **Above VWAP:** Premium +{jarak_vwap:.1f}%")

        # Alasan Dinamis berdasarkan metrik
        alasan_vwap = "Harganya saat ini berada di bawah rata-rata modal bandar intraday (Under VWAP), memberikan *margin of safety* yang aman dari risiko guyuran." if rekomendasi['Harga'] < rekomendasi['VWAP'] else "Meskipun terdiskon dari area pucuk harian, harganya masih di atas rata-rata VWAP, disarankan untuk mengantre di area VWAP agar lebih aman."
        alasan_rsi = "Tekanan jual sudah mereda ditandai dengan RSI yang masuk fase Oversold/Netral, sangat ideal untuk mulai *cicil buy* (Tranche 1)." if rekomendasi['RSI 5m'] < 50 else "RSI masih cukup tinggi, pantau terus dan tunggu koreksi intraday yang lebih dalam sebelum HAKA."

        st.markdown(f"""
        **💡 Alasan Pemilihan {rekomendasi['Ticker']}:**
        * Saham ini mengalami koreksi sehat dengan tingkat diskon **{rekomendasi['Diskon (%)']}%** dari harga tertingginya dalam 5 hari terakhir.
        * {alasan_vwap}
        * {alasan_rsi}
        """)
        
        st.markdown("---")
        
        # --- UI LAYOUT TOP 10 TABLE ---
        st.markdown("### 📋 Top 10 Saham Diskon Tertinggi")
        
        # Merapikan format kolom untuk ditampilkan di tabel
        df_tabel = df_top_10[['Ticker', 'Harga', 'Diskon (%)', 'Status VWAP', 'RSI 5m']].copy()
        df_tabel['Harga'] = df_tabel['Harga'].apply(lambda x: f"Rp {x:,.0f}")
        df_tabel['Diskon (%)'] = df_tabel['Diskon (%)'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            df_tabel,
            use_container_width=True,
            hide_index=True
        )
