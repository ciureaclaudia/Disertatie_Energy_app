# pages/production.py

import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

def show():
    st.subheader("🔋 Producție din surse regenerabile")
    st.line_chart({
        "Panouri Fotovoltaice": [100, 120, 110, 130, 150],
        "Turbine Eoliene": [80, 90, 95, 100, 105]
    })
