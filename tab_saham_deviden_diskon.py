import streamlit as st
from saham_dividen_diskon import scan_saham_dividen

def render_tab_saham_deviden_diskon(daftar_pantauan):
    st.subheader("💰 Radar Saham Deviden Diskon (Bottom Fishing)")
    st.write("Mendeteksi saham dari Daftar Pantauan yang harganya anjlok >5% dalam 1 Minggu Terakhir.")
    
    with st.spinner("Memindai saham diskon di market..."):
        top_10_diskon = scan_saham_dividen(daftar_pantauan)
        
    if top_10_diskon:
        st.success(f"✅ **Top {len(top_10_diskon)} Saham Diskon Ditemukan!**")
        
        # GRID SYSTEM: Maksimal 5 kolom per baris agar rapi dan tidak berdesakan
        MAX_COLS = 5 
        for i in range(0, len(top_10_diskon), MAX_COLS):
            baris_saham = top_10_diskon[i:i+MAX_COLS]
            cols_diskon = st.columns(len(baris_saham))
            
            for j, data in enumerate(baris_saham):
                with cols_diskon[j]:
                    # Margin-bottom ditambahkan agar ada jarak vertikal antar baris
                    st.markdown(f"""
                    <div style="background-color: #2b1f1f; padding: 15px; border-radius: 12px; border-left: 5px solid #ef4444; margin-bottom: 15px;">
                        <h2 style="margin:0; color: #f87171;">{data['ticker']}</h2>
                        <h1 style="margin: 5px 0; color: white; font-size: 1.8rem;">{data['penurunan_persen']:.2f}%</h1>
                        <p style="margin:0; color: #e5e7eb; font-size: 0.9rem;">Harga Skrg: <b>Rp {data['harga_sekarang']:,.0f}</b></p>
                        <p style="margin:0; color: #9ca3af; font-size: 0.8rem;"><del>{data.get('label_referensi', 'Harga Referensi')}: Rp {data['harga_minggu_lalu']:,.0f}</del></p>
                        <hr style="border-color: #4b5563; margin: 10px 0;">
                        <p style="margin:0; color: #10b981; font-size: 0.85rem;">🔼 Res: Rp {data['resistan']:,.0f}</p>
                        <p style="margin:0; color: #ef4444; font-size: 0.85rem;">🔽 Sup: Rp {data['support']:,.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Saat ini belum ada saham di daftar pantauan yang turun lebih dari 5% dalam 1 minggu terakhir.")
