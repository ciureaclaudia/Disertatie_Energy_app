# pages/consumption.py

import streamlit as st

def show():
    st.subheader("⚡ Consum total al clienților")
    st.area_chart({
        "Client 1": [20, 30, 25, 35, 40],
        "Client 2": [15, 25, 20, 30, 35]
    })
