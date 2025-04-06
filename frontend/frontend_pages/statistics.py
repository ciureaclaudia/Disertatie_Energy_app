# pages/statistics.py

import streamlit as st

def show(primary):
    st.subheader("📊 Statistici generale")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style="background:{primary}; padding:20px; border-radius:15px; color:white; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
                <h4>🔋 Producție Totală</h4>
                <h2>2.4 MWh</h2>
                <p>+5% față de ieri</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background:#f44336; padding:20px; border-radius:15px; color:white; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
                <h4>⚡ Consum Total</h4>
                <h2>2.0 MWh</h2>
                <p>-3% față de ieri</p>
            </div>
        """, unsafe_allow_html=True)
