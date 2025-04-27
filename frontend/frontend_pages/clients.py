# pages/clients.py

import streamlit as st
import pandas as pd
import requests
import altair as alt
from fpdf import FPDF
import io
from frontend_pages.addclients import show_add_client_form

def show(API_CLIENTS, primary):
    st.subheader("📋 Lista Clienților")

    # ➕ ADD CLIENT FORM
    show_add_client_form(API_CLIENTS)

    # Dacă tocmai s-a adăugat un client nou, reîncarcăm lista
    if st.session_state.get("refresh_clients", False):
        st.success("🔄 Lista de clienți a fost actualizată!")
        st.session_state["refresh_clients"] = False  # Resetam flag-ul

    try:
        response = requests.get(API_CLIENTS)
        if response.status_code == 200:
            clients = response.json()
            df = pd.DataFrame(clients)
   
            # st.dataframe(df)

            cols = st.columns(2)

            for i, (_, row) in enumerate(df.iterrows()):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #9cd9b2, #ffffff);
                        border: 1px solid #e6e6e6;
                        border-radius: 12px;
                        padding: 20px;
                        margin: 10px 5px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                        font-family: "Segoe UI", sans-serif;
                    '>
                        <div style='font-size: 20px; font-weight: 600; color: #2c3e50; margin-bottom: 8px;'>
                            {row['name']}
                        </div>
                        <div style='color: #7f8c8d; margin-bottom: 10px;'>
                            📍 {row['location']}
                        </div>
                        <div style='font-size: 15px;'> <b>Sursă:</b> {row['energy_source'].capitalize()}</div>
                        <div style='font-size: 15px;'> <b>Producție:</b> {row['max_production_mwh']} MWh</div>
                        <div style='font-size: 15px;'> <b>Consum:</b> {row['max_consumption_mwh']} MWh</div>
                    </div>
                    """, unsafe_allow_html=True)

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
                    start_date = st.date_input("📅 Data de început", pd.to_datetime("2025-01-01"))

                with col2:
                    end_date = st.date_input("📅 Data de sfârșit", pd.to_datetime("2025-01-03"))

                if start_date > end_date:
                    st.warning("⚠️ Data de început nu poate fi după data de sfârșit.")
                else:
                    url = f"{API_CLIENTS}{selected_client['id']}/readings/"
                    r = requests.get(url)
                    if r.status_code == 200:
                        data = pd.DataFrame(r.json())

                        # Conversie sigură în datetime și eliminare fus orar
                        data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True, errors='coerce')
                        data["timestamp"] = data["timestamp"].dt.tz_convert(None)

                        #  Asigurare că datele selectate sunt naive (fără fus orar)
                        start_date = pd.to_datetime(start_date).replace(tzinfo=None)
                        end_date = pd.to_datetime(end_date).replace(tzinfo=None)

                        filtered_data = data[
                            (data["timestamp"] >= start_date) &
                            (data["timestamp"] <= end_date)
                            ]

                        if filtered_data.empty:
                            st.info(" Nu există date în intervalul selectat.")
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
                                y=alt.Y('Valoare:Q', title="MWh"),
                                color=alt.Color('Tip:N', scale=alt.Scale(scheme='dark2'))
                            ).properties(
                                title=f"Evoluție consum și producție - {selected_client['name']}",
                                width=800,
                                height=400
                            ).configure_title(fontSize=20)

                            st.altair_chart(chart, use_container_width=True)

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

                                # Export CSV
                            csv = filtered_data.to_csv(index=False).encode('utf-8')

                            st.download_button(
                                    label="⬇️ Descarcă datele în CSV",
                                    data=csv,
                                    file_name=f"{selected_client['name'].replace(' ', '_')}_date_{start_date}_to_{end_date}.csv",
                                    mime='text/csv'
                                )
                            # Buton pentru generare raport PDF
                            if st.button("📝 Generează raport PDF"):
                                pdf = FPDF()
                                pdf.add_page()
                                pdf.set_font("Arial", size=12)

                                pdf.set_title(f"Raport VPP - {selected_client['name']}")

                                pdf.cell(200, 10, txt=f"Raport energetic pentru {selected_client['name']}", ln=True,
                                         align='C')
                                pdf.cell(200, 10, txt=f" Interval: {start_date} - {end_date}", ln=True, align='C')
                                pdf.ln(10)

                                pdf.cell(100, 10, txt=f" Total Productie: {total_production:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Media Productie: {avg_production:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Max Productie: {max_production:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Min Productie: {min_production:.2f} kWh", ln=True)
                                pdf.ln(5)
                                pdf.cell(100, 10, txt=f" Total Consum: {total_consumption:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Media Consum: {avg_consumption:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Max Consum: {max_consumption:.2f} kWh", ln=True)
                                pdf.cell(100, 10, txt=f" Min Consum: {min_consumption:.2f} kWh", ln=True)

                                # Save PDF in memory
                                pdf_buffer = io.BytesIO()
                                pdf_output_str = pdf.output(dest='S').encode('latin-1')
                                pdf_buffer = io.BytesIO(pdf_output_str)

                                # Buton de download
                                st.download_button(
                                    label=" Descarca raportul PDF",
                                    data=pdf_buffer,
                                    file_name=f"Raport_{selected_client['name'].replace(' ', '_')}.pdf",
                                    mime='application/pdf'
                                )

                    else:
                        st.error("❌ Nu s-au putut încărca datele energetice.")
    except Exception as e:
        st.error(f"Eroare: {e}")
