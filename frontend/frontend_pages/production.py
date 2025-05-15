import streamlit as st
import pandas as pd
import altair as alt
import requests
from datetime import datetime

def show(API_URL, API_URL_CONSUM):
    st.subheader(f"📈 Evoluție productie realizata {datetime.now().date()} - Solar vs Eolian")
    
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
        current_hour = datetime.now().hour
        df = df[df["hour"] < current_hour]
        df = df.rename(columns={"production_real": "Productie (MWh)", "energy_source": "Sursă"})

        # Agregăm consumul total pe fiecare oră și pe fiecare sursă
        grouped = df.groupby(["hour", "Sursă"])["Productie (MWh)"].sum().reset_index()

        # Graficul principal
        base_chart = alt.Chart(grouped).mark_line(point=True).encode(
            x=alt.X("hour:O", title="Oră din zi", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Productie (MWh):Q", title="Producție totală (MWh)"),
            color=alt.Color("Sursă:N", scale=alt.Scale(scheme="set2")),
            tooltip=["hour", "Sursă", "Productie (MWh)"]
        )

        # Evidențiere ora curentă - 1
        highlight_points = alt.Chart(grouped[grouped["hour"] == current_hour - 1]).mark_point(
            filled=True,
            size=150,
            color="red",
            stroke="black"
        ).encode(
            x="hour:O",
            y="Productie (MWh):Q",
            color=alt.Color("Sursă:N", legend=None)
        )

        # Adăugăm text cu valoarea de producție
        highlight_text = alt.Chart(grouped[grouped["hour"] == current_hour - 1]).mark_text(
            align='left',
            dx=5,
            dy=-10,
            fontSize=10,
            color="black"
        ).encode(
            x="hour:O",
            y="Productie (MWh):Q",
            text=alt.Text("Productie (MWh):Q", format=".2f"),
            color=alt.Color("Sursă:N", legend=None)
        )

        # Final chart
        chart = (base_chart + highlight_points + highlight_text).properties(
            title="Producție energetică azi",
            width=680,
            height=280
        )

        st.altair_chart(chart, use_container_width=True)   
    except Exception as e:
        st.error(f"❌ Eroare: {e}")

    st.markdown("---")

    # CONSUM
    st.subheader(f"📈 Evoluție consum realizat {datetime.now().date()} - Solar vs Eolian")

    try:
        response = requests.get(API_URL_CONSUM)
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
        current_hour = datetime.now().hour
        df = df[df["hour"] < current_hour]
        df = df.rename(columns={"consumption_real": "Consum (MWh)", "energy_source": "Sursă"})

        # Agregăm consumul total pe fiecare oră și pe fiecare sursă
        grouped = df.groupby(["hour", "Sursă"])["Consum (MWh)"].sum().reset_index()

        # Line chart cu 2 linii: solar și wind
        base_chart = alt.Chart(grouped).mark_line(point=True).encode(
            x=alt.X("hour:O", title="Oră din zi", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Consum (MWh):Q", title="Consum total (MWh)"),
            color=alt.Color("Sursă:N", scale=alt.Scale(scheme="set2")),
            tooltip=["hour", "Sursă", "Consum (MWh)"]
        )
       
        # Evidențiere ora curentă - 1
        highlight_points = alt.Chart(grouped[grouped["hour"] == current_hour - 1]).mark_point(
            filled=True,
            size=150,
            color="red",
            stroke="black"
        ).encode(
            x="hour:O",
            y="Consum (MWh):Q",
            color=alt.Color("Sursă:N", legend=None)
        )

        # Adăugăm text cu valoarea de producție
        highlight_text = alt.Chart(grouped[grouped["hour"] == current_hour - 1]).mark_text(
            align='left',
            dx=5,
            dy=-10,
            fontSize=12,
            color="black"
        ).encode(
            x="hour:O",
            y="Consum (MWh):Q",
            text=alt.Text("Consum (MWh):Q", format=".2f"),
            color=alt.Color("Sursă:N", legend=None)
        )

        # Final chart
        chart = (base_chart + highlight_points + highlight_text).properties(
            title="Consum energetică azi",
            width=700,
            height=300
        )

        st.altair_chart(chart, use_container_width=True)
        

    except Exception as e:
        st.error(f"❌ Eroare: {e}")
