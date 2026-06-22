
# saham_diskon.py
import streamlit as st

def render_saham_diskon_tab(ticker, entry, df_1d, df_5m):
    st.subheader(f"🏷️ Analisis Saham Diskon: {ticker}")
    
    if df_1d.empty or df_5m.empty:
        st.warning("Data tidak mencukupi untuk menghitung kalkulasi diskon.")
        return
        
    # Kalkulasi persentase diskon dari High 5 Hari Terakhir (Daily)
    high_5d = float(df_1d['High'].tail(5).max())
    low_5d = float(df_1d['Low'].tail(5).min())
    
    diskon_dari_pucuk_5d = ((high_5d - entry) / high_5d) * 100 if high_5d > 0 else 0
    
    # Ambil baris terakhir data 5 menit
    curr_5m = df_5m.dropna(subset=['VWAP', 'EMA20']).iloc[-1]
    vwap_val = float(curr_5m['VWAP'])
    rsi_val = float(curr_5m['RSI'])
    
    # Struktur UI Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Harga Tertinggi (5 Hari)", f"Rp {high_5d:,.0f}")
        st.write(f"📉 **Diskon dari Pucuk:** {diskon_dari_pucuk_5d:.1f}%")
        
    with col2:
        st.metric("RSI Intraday (5m)", f"{rsi_val:.1f}")
        if rsi_val < 40:
            st.success("🛒 **Status RSI:** Jenuh Jual (Oversold) - Waktunya Pantau!")
        elif rsi_val > 70:
            st.error("🚨 **Status RSI:** Jenuh Beli (Overbought) - Rawan Profit Taking!")
        else:
            st.info("⚖️ **Status RSI:** Netral / Konsolidasi")
            
    with col3:
        # Mengukur diskon intraday terhadap VWAP (Harga rata-rata modal bandar hari ini)
        if entry < vwap_val:
            diskon_vwap = ((vwap_val - entry) / vwap_val) * 100
            st.metric("Diskon vs VWAP", f"-{diskon_vwap:.1f}%")
            st.success("🔥 **Under VWAP:** Harga saat ini lebih murah dari rata-rata akumulasi market hari ini.")
        else:
            premium_vwap = ((entry - vwap_val) / vwap_val) * 100
            st.metric("Premium vs VWAP", f"+{premium_vwap:.1f}%")
            st.warning("⚠️ **Above VWAP:** Harga sudah naik di atas modal rata-rata market hari ini.")

    st.markdown("---")
    st.markdown("### 📊 Peta Matriks Diskon & Tindakan")
    
    # Logika Penentuan Keputusan Berdasarkan Tingkat Diskon
    if diskon_dari_pucuk_5d > 10 and entry < vwap_val and rsi_val < 50:
        st.success("""
        ### ✅ Rekomendasi: **STRONG ACCUMULATION ZONE**
        * Saham ini sudah terdiskon lebih dari **10%** dari harga tertingginya dalam 5 hari terakhir.
        * Posisi harga di bawah **VWAP**, memberikan *margin of safety* yang aman dari risiko guyuran masif.
        * **Aksi:** Cicil masuk menggunakan *Tranche 1* dan *Tranche 2* secara disiplin di fraksi-fraksi *Bid* yang tebal.
        """)
    elif diskon_dari_pucuk_5d > 5 and entry < vwap_val:
        st.info("""
        ### ⚖️ Rekomendasi: **NORMAL BUY ZONE (CICIL SANTAI)**
        * Saham mengalami koreksi wajar (*Pullback*) dan berada di bawah batas ekuilibrium harian.
        * **Aksi:** Antre beli di dekat area support psikologis atau ikuti petunjuk jaring bawah di tab *Eksekusi Order*.
        """)
    else:
        st.warning("""
        ### ❌ Rekomendasi: **NO DISCOUNT (TUNGGU PULLBACK)**
        * Saham ini tidak berada di area diskon atau harganya sudah berjalan terlalu cepat (pucuk harian).
        * **Aksi:** *Wait and see*. Memaksakan HAKA (*Hajar Kanan*) di area ini memperbesar risiko terkena pembalikan arah (*false breakout*).
        """)
