import streamlit as st
import yfinance as yf
import random

# =====================================================================
# 1. MESIN PEMINDAI (BACKEND)
# =====================================================================

def simulasi_bandarmologi(ticker):
    """
    Fungsi placeholder untuk Bandarmologi. 
    Ganti dengan koneksi API Bandarmologi sungguhan jika Anda memilikinya.
    """
    status = random.choice(["Akumulasi", "Distribusi", "Netral"])
    dana_milyar = round(random.uniform(0.5, 150.0), 1)
    
    if status == "Distribusi":
        dana_milyar = -abs(dana_milyar)
        
    return status, dana_milyar

@st.cache_data(ttl=3600) # Cache data selama 1 jam agar tidak lemot jika di-refresh
def scan_saham_dividen(daftar_pantauan):
    """
    Memindai maksimal 10 saham, mengambil riwayat harga 1 bulan, 
    menghitung persentase drop, dan mencari Support/Resistance.
    """
    hasil_scan = []
    
    # Validasi: Pastikan list tidak kosong dan potong maksimal 10 saham
    if not daftar_pantauan:
        return []
        
    daftar_pantauan_terbatas = daftar_pantauan[:10]
    
    for ticker in daftar_pantauan_terbatas:
        try:
            # Format ticker untuk Yahoo Finance (Bursa Efek Indonesia = .JK)
            ticker_yf = f"{ticker}.JK" if not ticker.endswith(".JK") else ticker
            
            saham = yf.Ticker(ticker_yf)
            # Ambil data 1 bulan terakhir
            hist = saham.history(period="1mo")
            
            # Skip jika data kosong atau tidak cukup untuk dianalisa
            if hist.empty or len(hist) < 5: 
                continue
            
            harga_sekarang = hist['Close'].iloc[-1]
            harga_sebulan_lalu = hist['Close'].iloc[0]
            
            # Hitung persentase penurunan
            penurunan_persen = ((harga_sebulan_lalu - harga_sekarang) / harga_sebulan_lalu) * 100
            
            # Filter hanya saham yang anjlok lebih dari 5%
            if penurunan_persen > 5.0:
                support_1b = hist['Low'].min()
                resistan_1b = hist['High'].max()
                
                status_bandar, dana_masuk = simulasi_bandarmologi(ticker)
                
                hasil_scan.append({
                    'ticker': ticker.replace('.JK', ''),
                    'penurunan_persen': float(penurunan_persen),
                    'harga_sekarang': float(harga_sekarang),
                    'harga_sebulan_lalu': float(harga_sebulan_lalu),
                    'support': float(support_1b),
                    'resistan': float(resistan_1b),
                    'status_bandar': status_bandar,
                    'dana_masuk_milyar': float(dana_masuk)
                })
                
        except Exception as e:
            # Jika ada error pada 1 saham, log error dan lanjut ke saham berikutnya
            print(f"Gagal memproses {ticker}: {e}")
            continue
            
    # Urutkan berdasarkan persentase drop tertinggi
    hasil_scan = sorted(hasil_scan, key=lambda x: x['penurunan_persen'], reverse=True)
    return hasil_scan


# =====================================================================
# 2. ANTARMUKA PENGGUNA (FRONTEND STREAMLIT)
# =====================================================================
# =====================================================================
# 2. ANTARMUKA PENGGUNA (FRONTEND STREAMLIT)
# =====================================================================

def render_tab_saham_deviden_diskon(daftar_pantauan):
    """
    Fungsi utama yang akan dipanggil di file utama (main.py) untuk merender UI.
    """
    st.subheader("💰 Radar Saham Deviden Diskon (Bottom Fishing)")
    st.write("Mendeteksi maksimal **10 saham** dari Daftar Pantauan yang harganya anjlok >5% dalam **1 Bulan Terakhir**.")
    
    # Render UI Scanning
    with st.spinner("Memindai saham di market (Data 1 Bulan) & Menganalisa Bandarmologi..."):
        top_diskon = scan_saham_dividen(daftar_pantauan)
        
    # Render Hasil
    if top_diskon:
        st.success(f"✅ **Ditemukan {len(top_diskon)} Saham Sedang Diskon!**")
        
        # GRID SYSTEM: Maksimal 4 kolom per baris agar tidak terlalu sempit
        MAX_COLS = 4 
        
        # Memecah list saham ke dalam beberapa baris
        for i in range(0, len(top_diskon), MAX_COLS):
            baris_saham = top_diskon[i:i+MAX_COLS]
            
            # PERBAIKAN 1: Selalu gunakan MAX_COLS agar lebar kartu tetap sama (tidak melar di baris terakhir)
            cols_diskon = st.columns(MAX_COLS)
            
            for j, data in enumerate(baris_saham):
                with cols_diskon[j]:
                    # Konfigurasi Visual Bandarmologi
                    status_bandar = data.get('status_bandar', 'Netral')
                    if status_bandar == 'Akumulasi':
                        warna_bandar, ikon_bandar = '#10b981', '🟢' # Hijau
                    elif status_bandar == 'Distribusi':
                        warna_bandar, ikon_bandar = '#ef4444', '🔴' # Merah
                    else:
                        warna_bandar, ikon_bandar = '#f59e0b', '🟡' # Kuning
                        
                    # PERBAIKAN 2: Penambahan min-height, margin dirapikan, flexbox untuk teks
                    st.markdown(f"""
                    <div style="
                        background-color: #1e1e1e; 
                        padding: 15px; 
                        border-radius: 10px; 
                        border-left: 5px solid #ef4444; 
                        border-right: 1px solid #333; 
                        border-top: 1px solid #333; 
                        border-bottom: 1px solid #333; 
                        margin-bottom: 15px; 
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                        min-height: 260px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h2 style="margin:0; color: #f87171; font-family: monospace; font-size: 1.4rem;">{data['ticker']}</h2>
                            </div>
                            <h1 style="margin: 5px 0 10px 0; color: white; font-size: 1.5rem;">▼ {data['penurunan_persen']:.2f}%</h1>
                            
                            <div style="background-color: #2d2d2d; padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                                <p style="margin:0 0 4px 0; color: #e5e7eb; font-size: 0.85rem;">Harga Skrg : <b style="color:white;">Rp {data['harga_sekarang']:,.0f}</b></p>
                                <p style="margin:0; color: #9ca3af; font-size: 0.8rem;">1 Bln Lalu : <del>Rp {data.get('harga_sebulan_lalu', 0):,.0f}</del></p>
                            </div>
                            
                            <div style="margin-bottom: 10px;">
                                <p style="margin:0 0 3px 0; color: #10b981; font-size: 0.85rem;" title="Tertinggi 1 Bulan">🔼 Res : Rp {data['resistan']:,.0f}</p>
                                <p style="margin:0; color: #ef4444; font-size: 0.85rem;" title="Terendah 1 Bulan">🔽 Sup : Rp {data['support']:,.0f}</p>
                            </div>
                        </div>
                        
                        <div>
                            <hr style="border-color: #4b5563; margin: 10px 0;">
                            <p style="margin:0 0 3px 0; color: #9ca3af; font-size: 0.75rem;">Bandarmologi (Estimasi 1B):</p>
                            <p style="margin:0; color: {warna_bandar}; font-size: 0.85rem; font-weight: 600;">
                                {ikon_bandar} {status_bandar} <br> (Rp {data.get('dana_masuk_milyar', 0):,.1f} M)
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Saat ini belum ada saham dari daftar pantauan yang anjlok lebih dari 5% dalam 1 bulan terakhir.")
