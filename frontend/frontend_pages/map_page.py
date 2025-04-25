import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

def show(API_CLIENTS_COORDINATES):
    st.title("🗺️ Clienți pe hartă")
    try:
        # 1. Ia datele de la API
        response = requests.get(API_CLIENTS_COORDINATES)
        if response.status_code == 200:
            data = response.json()

            # 2. Convertim în DataFrame
            df = pd.DataFrame(data)
            st.write(df.head())

            # 3. Inițializăm harta pe poziția medie
            map_center = [df['lat'].mean(), df['long'].mean()]
            m = folium.Map(location=map_center, zoom_start=6)

            # 4. Adăugăm markere pentru fiecare client
            for _, row in df.iterrows():
                popup_html = f"""
                <b>{row['name']}</b><br>
                {row['location']}<br>
                <i>Source:</i> {row['energy_source']}<br>
                <i>Production:</i> {row['max_production_mwh']} MWh<br>
                <i>Consumption:</i> {row['max_consumption_mwh']} MWh
                """
                folium.Marker(
                    location=[row['lat'], row['long']],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(color="green" if row['has_production'] else "red", icon="bolt")
                ).add_to(m)

            # 5. Afișăm harta
            st.title("🗺️ Clienți pe hartă")
            st_folium(m, width=900, height=600)

        else:
            st.error("❌ Nu s-au putut încărca coordonatele clientilor.")

    except Exception as e:
        st.error(f"Eroare: {e}")
