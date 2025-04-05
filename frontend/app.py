import streamlit as st
from streamlit_option_menu import option_menu
import requests
import pandas as pd
import altair as alt

# === Configura pagina ===
st.set_page_config(
    page_title="⚡ VPP Dashboard",
    page_icon="🌿",
    layout="wide"
)

API_CLIENTS = "http://127.0.0.1:8000/api/clients/"

# === Tema / Mod vizual ===
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/solar-panel.png", width=80)
    selected = option_menu(
        menu_title="🌿 Meniu VPP",
        options=["Acasă", "Producție", "Consum", "Clienți", "Statistici"],
        icons=["house", "battery-charging", "lightning", "people", "bar-chart-line"],
        default_index=0,
        orientation="vertical"
    )
    mode = st.toggle("🌗 Dark Mode")

# === Paletă culori ===
primary = "#4CAF50" if not mode else "#90EE90"
bg = "#f5f7fa" if not mode else "#1c1c1e"
text = "#212121" if not mode else "#ffffff"
card_bg = "#ffffff" if not mode else "#2b2b2b"

# === HEADER ===
st.markdown(f"""
    <style>
        .main {{
            background-color: {bg};
        }}
    </style>
    <div style='text-align:center; padding:20px; background:linear-gradient(to right, {primary}, #81c784); border-radius:10px;'>
        <h1 style='color:white;'>⚡ Virtual Power Plant Dashboard</h1>
        <p style='color:white;'>Monitorizează producția, consumul și performanța energetică</p>
    </div>
""", unsafe_allow_html=True)

# === PAGINI ===

if selected == "Acasă":
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

elif selected == "Producție":
    st.subheader("🔋 Producție din surse regenerabile")
    st.line_chart({
        "Panouri Fotovoltaice": [100, 120, 110, 130, 150],
        "Turbine Eoliene": [80, 90, 95, 100, 105]
    })

elif selected == "Consum":
    st.subheader("⚡ Consum total al clienților")
    st.area_chart({
        "Client 1": [20, 30, 25, 35, 40],
        "Client 2": [15, 25, 20, 30, 35]
    })

elif selected == "Clienți":
    st.subheader("📋 Lista Clienților")
    try:
        response = requests.get(API_CLIENTS)
        if response.status_code == 200:
            clients = response.json()
            df = pd.DataFrame(clients)
            st.dataframe(df)

            client_names = [client["name"] for client in clients]
            selected_client_name = st.selectbox("🔍 Alege un client", client_names)

            selected_client = next((c for c in clients if c["name"] == selected_client_name), None)

            if selected_client:
                st.markdown(f"<h3 style='color:{primary};'>{selected_client['name']}</h3>", unsafe_allow_html=True)
                st.write(f"📍 Locație: {selected_client['location']}")
                st.write(f"🔌 Tip sursă: {selected_client['energy_source']}")

                # Selectare interval de timp
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("📅 Data de început", pd.to_datetime("2024-01-01"))
                with col2:
                    end_date = st.date_input("📅 Data de sfârșit", pd.to_datetime("2024-12-31"))

                if start_date > end_date:
                    st.warning("⚠️ Data de început nu poate fi după data de sfârșit.")
                else:
                    url = f"{API_CLIENTS}{selected_client['id']}/readings/"
                    r = requests.get(url)
                    if r.status_code == 200:
                        data = pd.DataFrame(r.json())
                        # Elimină timezone-ul pentru a evita conflicte la comparație
                        data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_localize(None)

                        # Filtrare după data selectată
                        filtered_data = data[
                            (data["timestamp"] >= pd.to_datetime(start_date)) &
                            (data["timestamp"] <= pd.to_datetime(end_date))
                            ]

                        if filtered_data.empty:
                            st.info("📭 Nu există date în intervalul selectat.")
                        else:
                            chart_data = filtered_data.rename(columns={
                                "consumption_real": "Consum",
                                "production_real": "Productie"
                            })

                            chart = alt.Chart(chart_data).transform_fold(
                                ['Consum', 'Productie'],
                                as_=['Tip', 'Valoare']
                            ).mark_line(point=True).encode(
                                x=alt.X('timestamp:T', title="Timp"),
                                y=alt.Y('Valoare:Q', title="kWh"),
                                color=alt.Color('Tip:N', scale=alt.Scale(scheme='dark2'))
                            ).properties(
                                title=f"Evoluție consum și producție - {selected_client['name']}",
                                width=800,
                                height=400
                            ).configure_title(fontSize=20)

                            st.altair_chart(chart, use_container_width=True)

                            # Rezumat numeric
                            total_production = filtered_data["production_real"].sum()
                            total_consumption = filtered_data["consumption_real"].sum()

                            avg_production = filtered_data["production_real"].mean()
                            avg_consumption = filtered_data["consumption_real"].mean()

                            max_production = filtered_data["production_real"].max()
                            min_production = filtered_data["production_real"].min()

                            max_consumption = filtered_data["consumption_real"].max()
                            min_consumption = filtered_data["consumption_real"].min()

                            st.markdown("---")
                            st.markdown(f"<h4 style='color:{primary};'>📊 Rezumat pentru perioada selectată</h4>",
                                        unsafe_allow_html=True)

                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric("🔋 Total Producție (MWh)", f"{total_production:.2f}")
                                st.metric("📈 Media Zilnică Producție", f"{avg_production:.2f}")
                                st.metric("⬆️ Maxim Producție", f"{max_production:.2f}")
                                st.metric("⬇️ Minim Producție", f"{min_production:.2f}")

                            with col2:
                                st.metric("⚡ Total Consum (MWh)", f"{total_consumption:.2f}")
                                st.metric("📉 Media Zilnică Consum", f"{avg_consumption:.2f}")
                                st.metric("⬆️ Maxim Consum", f"{max_consumption:.2f}")
                                st.metric("⬇️ Minim Consum", f"{min_consumption:.2f}")
                    else:
                        st.error("❌ Nu s-au putut încărca datele energetice.")

    except Exception as e:
        st.error(f"Eroare: {e}")

elif selected == "Statistici":
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


