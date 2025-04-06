# pages/home.py

import streamlit as st

def show(primary, text, card_bg):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
            <div style='background-color:{card_bg}; padding:25px; border-radius:15px; box-shadow:0 4px 8px rgba(0,0,0,0.2);'>
                <h2 style='color:{primary};'>👋 Bun venit!</h2>
                <p style='font-size:18px; color:{text};'>
                    Aceasta este platforma ta de management energetic verde. Poți vizualiza în timp real consumul și producția, analiza comportamentul clienților și urmări evoluția rețelei tale VPP.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4299/4299926.png", width=250)
