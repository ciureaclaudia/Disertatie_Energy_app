import streamlit as st
import pandas as pd
import altair as alt
import requests
from datetime import datetime

def show(API_URL):
    st.subheader(f"📈 Evoluție consum {datetime.now().date()} - Solar vs Eolian")
   
    try:
        response = requests.get(API_URL)
        if response.status_code != 200:
            st.error("❌ Eroare la preluarea datelor.")
            return

        data = response.json()
        if not data:
            st.info("ℹ️ Nu există date pentru ziua curentă.")
            return

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df = df.rename(columns={"consumption_real": "Consum (MWh)", "energy_source": "Sursă"})

        # Agregăm consumul total pe fiecare oră și pe fiecare sursă
        grouped = df.groupby(["hour", "Sursă"])["Consum (MWh)"].sum().reset_index()

        # Line chart cu 2 linii: solar și wind
        chart = alt.Chart(grouped).mark_line(point=True).encode(
            x=alt.X("hour:O", title="Oră din zi", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Consum (MWh):Q", title="Consum total (MWh)"),
            color=alt.Color("Sursă:N", scale=alt.Scale(scheme="set2")),
            tooltip=["hour", "Sursă", "Consum (MWh)"]
        ).properties(
            title="Consum energetic azi",
            width=800,
            height=400
        )

        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Eroare: {e}")
