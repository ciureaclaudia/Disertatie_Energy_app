import streamlit as st
import requests

def show_add_client_form(API_CLIENTS):
    @st.dialog("Adaugă Client Nou")
    def add_client_dialog():
        st.subheader("Completează datele noului client:")

        name = st.text_input("Nume Client")
        location = st.text_input("Locație")
        lat = st.number_input("Latitudine", format="%.6f")
        long = st.number_input("Longitudine", format="%.6f")
        energy_source = st.selectbox("Sursa Energie", ["solar", "wind", "hydro", "other"])
        max_consumption = st.number_input("Consum maxim (MWh)", format="%.2f")
        max_production = st.number_input("Producție maximă (MWh)", format="%.2f")
        has_consumption = st.checkbox("Are consum?", value=True)
        has_production = st.checkbox("Are producție?", value=True)

        if st.button("✅ Creează Client", key="create_client_btn"):
            with st.spinner("⏳ Se creează clientul..."):
                payload = {
                    "name": name,
                    "location": location,
                    "lat": lat,
                    "long": long,
                    "energy_source": energy_source,
                    "max_consumption_mwh": max_consumption,
                    "max_production_mwh": max_production,
                    "has_consumption": has_consumption,
                    "has_production": has_production
                }
                response = requests.post(API_CLIENTS, json=payload)

                if response.status_code == 201:
                    st.success("✅ Client creat cu succes!")
                    client_id = response.json().get("id")

                    # Salvăm în session_state
                    st.session_state["created_client_id"] = client_id
                    st.session_state["client_created"] = True
                else:
                    st.error(f"❌ Eroare la crearea clientului: {response.status_code}")

        # Dacă clientul a fost creat cu succes ➔ formular de generare date
        if st.session_state.get("client_created"):
            st.write("---")
            st.subheader("Generează date consum/producție pentru client")

            start_date = st.text_input("Data start (YYYY-MM-DDTHH:MM)", key="start_date")
            end_date = st.text_input("Data sfârșit (YYYY-MM-DDTHH:MM)", key="end_date")

            if st.button("⚡ Generează Date", key="generate_data_btn"):
                with st.spinner("⏳ Se generează datele..."):
                    data_payload = {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                    data_response = requests.post(
                        f"{API_CLIENTS}{st.session_state['created_client_id']}/generate_data/",
                        json=data_payload
                    )
                    if data_response.status_code == 201:
                        st.success("✅ Date generate cu succes!")
                        st.session_state["refresh_clients"] = True
                        # Resetam
                        del st.session_state["client_created"]
                        del st.session_state["created_client_id"]
                    else:
                        st.error("❌ Eroare la generarea datelor!")

    # Butonul principal
    if st.button("➕ Add Client"):
        add_client_dialog()
