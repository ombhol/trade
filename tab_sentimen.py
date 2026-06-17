import streamlit as st
from data_fetcher import ambil_berita_indonesia

def render_tab_sentimen(ticker_utama):
    st.subheader(f"📰 Katalis Media: {ticker_utama}")
    berita_lokal = ambil_berita_indonesia(ticker_utama)
    if berita_lokal:
        for item in berita_lokal:
            st.markdown(f"🔹 **[{item['title']}]({item['link']})**")
            st.caption(f"🗞️ Sumber: {item['source']} | 🕒 {item['date']}")
    else:
        st.info("Market hening. Tidak ada sentimen berita penggerak.")
