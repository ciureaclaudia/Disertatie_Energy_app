import streamlit as st
import requests
import pandas as pd
import altair as alt

API_CLIENTS = "http://127.0.0.1:8000/api/clients/"

st.title("Lista clientilor")

try:
    response = requests.get(API_CLIENTS)
    if response.status_code == 200:
        clients = response.json()
        for client in clients:
            st.subheader(client["name"])
            st.write(f"Locatie: {client['location']}")
            st.write(f"Tip sursa: {client['energy_source']}")

            if st.button(f"Vezi grafic pentru {client['name']}", key=client["id"]):
                with st.spinner("Se încarcă datele ..."):
                    url = f"{API_CLIENTS}{client['id']}/readings/"
                    r = requests.get(url)
                    if r.status_code == 200:
                        data = pd.DataFrame(r.json())
                        data["timestamp"] = pd.to_datetime(data["timestamp"])

                        # Renumește coloanele pentru grafic combinat
                        chart_data = data.rename(columns={
                            "consumption_real": "Consum",
                            "production_real": "Productie"
                        })

                        chart = alt.Chart(chart_data).transform_fold(
                            ['Consum', 'Productie'],
                            as_=['Tip', 'Valoare']
                        ).mark_line().encode(
                            x='timestamp:T',
                            y='Valoare:Q',
                            color='Tip:N'
                        ).properties(
                            title=f"Evolutie consum si productie - {client['name']}",
                            width=700
                        )

                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.error("Nu s-au putut incarca datele energetice.")
    else:
        st.error("Nu s-au putut incarca clientii.")
except Exception as e:
    st.error(f"Eroare: {e}")