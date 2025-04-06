# pages/production.py

import streamlit as st

def show():
    st.subheader("🔋 Producție din surse regenerabile")
    st.line_chart({
        "Panouri Fotovoltaice": [100, 120, 110, 130, 150],
        "Turbine Eoliene": [80, 90, 95, 100, 105]
    })
