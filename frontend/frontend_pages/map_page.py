import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from folium.features import DivIcon
from folium import CustomIcon

def show(API_CLIENTS_COORDINATES):
    st.title("🗺️ Clienți pe hartă")

    st.markdown(
    """
    <style>
    .rotating {
        animation: rotation 1s linear infinite;
        width: 60px;
        margin: 0 20px;
    }

    @keyframes rotation {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .row {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>

    <div class="row">
        <img src="https://cdn-icons-png.flaticon.com/512/169/169367.png" class="rotating">
        <img src="https://cdn-icons-png.flaticon.com/512/169/169367.png" class="rotating">
        <img src="https://cdn-icons-png.flaticon.com/512/169/169367.png" class="rotating">
    </div>
    """,
    unsafe_allow_html=True
)


    try:
        # 1. Ia datele de la API
        response = requests.get(API_CLIENTS_COORDINATES)
        if response.status_code == 200:
            data = response.json()

            # 2. Convertim în DataFrame
            df = pd.DataFrame(data)
            
            # 3. Inițializăm harta in centru
            map_center = [45.9432, 24.9668]
            m = folium.Map(location=map_center, zoom_start=7)

            # 4. MarkerCluster -grupez locatii in cazul in care ele sunt apropiate
            marker_cluster = MarkerCluster().add_to(m)

            # 4. Adaugă markerii în cluster cu iconițe personalizate
            for _, row in df.iterrows():
                energy_source = row.get("energy_source")

                if energy_source == "solar":
                    icon_url = "https://cdn-icons-png.flaticon.com/512/169/169367.png"

                else:
                    icon_url = "https://cdn-icons-png.flaticon.com/512/8584/8584170.png"

               # 5. Adăugăm markere pentru fiecare client
                popup_html = f"""
                <div style="font-family: Arial; font-size: 14px;">
                    <div style="font-weight: bold; font-size: 16px; color: #2c3e50;">{row['name']}</div>
                    <div style="margin-bottom: 4px; color: #7f8c8d;">📍 {row.get('location', 'necunoscut')}</div>
                    <div><b> Sursă:</b> {row.get('energy_source', '-')}</div>
                    <div><b> Producție:</b> {row.get('max_production_mwh', 0)} MWh</div>
                    <div><b> Consum:</b> {row.get('max_consumption_mwh', 0)} MWh</div>
                </div>
                """
                folium.Marker(
                    location=[row['lat'], row['long']],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['name']} ({row.get('energy_source', '-').capitalize()})",
                    icon=CustomIcon(icon_url, icon_size=(40, 40))  # facem icon mai mare
                ).add_to(marker_cluster)

            # 6. Afișăm harta
            with st.container():
                st.markdown("""
                    <style>
                        div[data-testid="stVerticalBlock"] > div:has(.folium-map) {
                            border-radius: 20px;
                            overflow: hidden;
                            box-shadow: 0 4px 8px rgba(0,0,0,1);
                            border: 1px solid #e6e6e6;
                            margin-bottom: 20px;
                        }
                    </style>
                """, unsafe_allow_html=True)
            st_folium(m, width=1000, height=500)

        else:
            st.error("❌ Nu s-au putut încărca coordonatele clientilor.")

    except Exception as e:
        st.error(f"Eroare: {e}")
