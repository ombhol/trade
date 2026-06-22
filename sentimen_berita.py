# sentimen_berita.py
import streamlit as st
from data_fetcher import ambil_berita_indonesia

def render_sentimen_tab(ticker):
    st.subheader(f"📰 Katalis Media: {ticker}")
    berita_lokal = ambil_berita_indonesia(ticker)
    
    if berita_lokal:
        for item in berita_lokal:
            st.markdown(f"🔹 **[{item['title']}]({item['link']})**")
            st.caption(f"🗞️ Sumber: {item['source']} | 🕒 {item['date']}")
    else:
        st.info("Market hening. Tidak ada sentimen berita penggerak.")
