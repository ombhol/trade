import streamlit as st
import plotly.graph_objects as go
from utils import sesuaikan_fraksi_bei

def render_tab_eksekusi(entry, vwap_val, curr_5m, persen_kenaikan, jarak_vwap_persen, total_lot, fee_broker, tp1, tp2, sl, batas_arb, turnover_5m_rata_rata, tren_harian, skor_utama, df_5m):
    col_plan, col_rules = st.columns([1.5, 1])
    entry_cicil_1 = sesuaikan_fraksi_bei(entry)
    entry_cicil_2 = sesuaikan_fraksi_bei(vwap_val) if vwap_val > 0 else entry
    if entry_cicil_2 >= entry_cicil_1: entry_cicil_2 = sesuaikan_fraksi_bei(float(curr_5m['EMA20']))

    with col_plan:
        st.markdown("### 🎯 Skenario Entry Anti-Guyur")
        if persen_kenaikan > 5.5 or jarak_vwap_persen > 2.5:
            st.warning(f"🚨 **RAWAN GUYURAN:** Harga sudah melesat jauh dari rata-rata modal bandar (VWAP).")
            st.write(f"🔹 **Tranche 1 (Test Water - 30%):** Rp {entry_cicil_1}")
            st.write(f"🔥 **Tranche 2 (Pullback - 70%):** Rp {entry_cicil_2}")
        else:
            st.success("✅ **ZONA AKUMULASI AMAN:** Harga merapat ke ekuilibrium market harian.")
            st.write(f"🔹 **Tranche 1 (Masuk Awal - 50%):** Rp {entry_cicil_1}")
            st.write(f"🔹 **Tranche 2 (Jaring Bawah - 50%):** Rp {entry_cicil_2}")

        st.markdown("---")
        st.markdown("### 🛡️ Target Realisasi Cuan")
        
        modal_terpakai = entry * total_lot * 100
        if modal_terpakai > 0:
            jual_tp1_val = tp1 * total_lot * 100
            estimasi_fee_tp1 = (modal_terpakai + jual_tp1_val) * fee_broker
            net_rp_tp1 = (jual_tp1_val - modal_terpakai) - estimasi_fee_tp1
            net_persen_tp1 = (net_rp_tp1 / modal_terpakai) * 100
            
            jual_tp2_val = tp2 * total_lot * 100
            estimasi_fee_turn = (modal_terpakai + jual_tp2_val) * fee_broker
            net_rp_tp2 = (jual_tp2_val - modal_terpakai) - estimasi_fee_turn
            net_persen_tp2 = (net_rp_tp2 / modal_terpakai) * 100
            
            if net_persen_tp1 <= 0:
                st.error(f"⚠️ **TP1 (Rp {tp1:,}):** Margin dihabiskan oleh fee broker.")
            else:
                st.success(f"🎯 **TP1 (Quick Scalp 50%): Rp {tp1:,}** | Nett: {net_persen_tp1:.1f}% (~Rp {net_rp_tp1:,.0f})")
                
            st.info(f"🚀 **TP2 (Swing Intraday): Rp {tp2:,}** | Nett: {net_persen_tp2:.1f}% (~Rp {net_rp_tp2:,.0f})")
        else:
            st.warning("Lot size 0. Jarak Stop Loss terlalu lebar atau Likuiditas mati.")
            
        st.error(f"📉 **STOP LOSS STRICT:** Rp {sl:,.0f} *(Batas ARB Hari Ini: Rp {batas_arb:,.0f})*")
        
    with col_rules:
        st.markdown("### 📝 Validasi Real Market")
        if turnover_5m_rata_rata < 100000000:
            st.error(f"❌ **Saham Ilusi (Low Turnover):** Omset 5 mnt hanya Rp {turnover_5m_rata_rata/1000000:,.1f} Jt. Rawan manipulasi Bid/Offer!")
        elif tren_harian == "DOWNTREND 🔴" and skor_utama >= 60:
            st.warning("⚠️ **REBOUND PLAY:** Spekulatif pantulan cepat. Wajib Hit & Run!")
        elif tren_harian == "DOWNTREND 🔴": 
            st.error("❌ **Trend Hancur:** Market membuang emiten ini. Jangan menahan pisau jatuh.")
        elif persen_kenaikan > 8.0: 
            st.error("❌ **Ekstrem FOMO:** Hindari masuk di zona pucuk harian.")
        else: 
            st.success("🚀 **Clear for Takeoff:** Momentum dan struktur uptrend valid.")
            
    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m['Open'], high=df_5m['High'], low=df_5m['Low'], close=df_5m['Close'], name="Harga"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m['VWAP'], line=dict(color='#3b82f6', width=2), name='VWAP'))
    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
