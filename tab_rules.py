import streamlit as st

def render_tab_rules():
    st.subheader("📖 Panduan Penggunaan & SOP Day Trader BEI")
    
    st.markdown("""
    ### 🎯 5 Langkah Eksekusi Taktis
    1. **Atur Amunisi (Sidebar Kiri):** Masukkan Total Modal yang siap di-tradingkan dan atur batas persentase *Cut Loss* (Risiko). Biarkan sistem menghitung batas lot maksimum yang aman untuk Anda beli.
    2. **Perhatikan Sesi Jam (Indikator Atas):** * **Pagi (09:00 - 10:00 WIB):** Sesi paling agresif. Volatilitas sangat tinggi, cocok untuk eksekusi kilat.
       * **Siang (10:00 - 14:00 WIB):** Rawan *sideways* dan *false breakout*. Disarankan untuk menahan diri (*wait & see*).
       * **Sore (14:00 - 16:00 WIB):** Waktu ideal untuk mencari sinyal akumulasi saham guna strategi Beli Sore Jual Pagi (BSJP).
    3. **Pantau Scanner (Top 3):** Sistem akan menyaring puluhan saham dari Daftar Pantauan untuk memunculkan emiten yang volume intraday-nya sedang diakumulasi oleh uang pintar.
    4. **Deep Dive Emiten:** Ketik kode saham incaran dari daftar *Top 3* ke kolom **Analisis Saham Spesifik** di sidebar kiri untuk membedah target harga terperinci. Gunakan *Bypass Harga Real-Time* jika harga telat (*delay*).
    5. **Eksekusi Order (Aplikasi Sekuritas):** Patuhi **Skenario Entry Anti-Guyur** (disarankan mecicil 2 titik) dan pastikan jumlah lot yang Anda input di sekuritas tidak melebihi rekomendasi **Safe Lot Size**.

    ---
    ### ⚠️ Rules Sistem & Keamanan Portofolio
    * **Keamanan Anti-Ban (Teknis):** Sistem menggunakan eksekusi asinkronus `yfinance` untuk *Scanner* agar server terhindar dari pemblokiran otomatis, sementara bagian analisa mendalam diinjeksi dengan harga presisi *real-time* langsung dari *Google Finance* atau input manual (*Override*).
    * **Disiplin Cut Loss:** Eksekusi Cut Loss di aplikasi Anda tanpa kompromi bila harga penutupan menyentuh angka **Stop Loss Strict**. Jangan pernah melakukan *averaging down* (menangkap pisau jatuh) saat tren harian berstatus *Downtrend*.
    * **Validasi Likuiditas Manual:** Meskipun sistem sudah menyaring saham dengan Turnover minimal Rp 100 Juta, Anda **WAJIB** mengecek ketebalan lot *Bid-Offer* dan *Running Trade* secara langsung di aplikasi sekuritas (seperti Stockbit/Trimegah) sebelum menekan tombol Hajar Kanan (HAKA).
    """)
