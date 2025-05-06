# pages/home.py

import streamlit as st
import pandas as pd
import requests
import pytz
import plotly.graph_objects as go


def show(API_LAST_HOUR, primary, text, card_bg):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
            <div style='background-color:{card_bg}; padding:18px; border-radius:20px; box-shadow:0 4px 8px rgba(0,0,0,0.2);'>
                <h2 style='color:{primary};'>👋 Bun venit!</h2>
                <p style='font-size:18px; color:{text};'>
                    Aceasta este platforma ta de management energetic verde. Poți vizualiza în timp real consumul și producția, analiza comportamentul clienților și urmări evoluția rețelei tale VPP.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4299/4299926.png", width=200)

    st.markdown("---")

    try:
    
        response = requests.get(API_LAST_HOUR)
        if response.status_code == 200:

            data = response.json()
            df = pd.DataFrame(data)

            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_convert(pytz.timezone("Europe/Bucharest"))
            df["ora_ro"] = df["timestamp"].dt.strftime("%H:%M")
            df["lt_real"] =df["consumption_real"]-df["production_real"]
            df["lt_forecast"]=df["consumption_forecast"]-df["production_forecast"]
            df["diferenta"] = df["lt_real"] -df["lt_forecast"]
            df["status"] = df["diferenta"].apply(lambda x: "Excedent" if x >= 0 else "Deficit")

            
            st.subheader(" Situația energetică pe ultima oră")
            # st.dataframe(df[["client", "ora_ro", "consumption_real","production_real","lt_real","consumption_forecast","production_forecast", "lt_forecast", "status"]])
            render_beautiful_table(df)

            st.markdown("---")

            # logica transgfer energie
            data = [
                {
                    "Client": row["client"],
                    "Cantitate Energie": row["diferenta"],  # sau altă coloană relevantă
                    "Status": row["status"]
                }
                for _, row in df.iterrows()
            ]

            response = requests.post("http://127.0.0.1:8000/api/readings/redistribute-energy/", json=data)
            if response.status_code == 200:
                result = response.json()

                # 1. Afișăm transferurile
                st.subheader("🔁 Transferuri de energie")
                transfers = pd.DataFrame(result["transfers"])
                render_transfer_table(transfers)

                # 2 Afișăm câtă energie mai rămâne de cerut din grid
                deficit_final = pd.DataFrame(result["deficit"])
                energie_din_grid = deficit_final[deficit_final["Cantitate Energie"] < 0]["Cantitate Energie"].sum()

                st.subheader("⚡ Energie in deficit -iau energia in gridul national:")
                st.metric(label="MWh", value=round(abs(energie_din_grid), 3))

                # 3 Afișăm câtă energie a rămas nefolosită în rețea (excedent final)
                excedent_final = pd.DataFrame(result["excedent"])
                energie_excedent = excedent_final[excedent_final["Cantitate Energie"] > 0]["Cantitate Energie"].sum()

                st.subheader("🌞 Energie in excedent -dau energia in gridul national:")
                st.metric(label="MWh", value=round(energie_excedent, 3))

                st.markdown("---")
                fig = render_energy_sankey(result["transfers"], pd.DataFrame(result["deficit"]))
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error(f"API Error: {response.status_code}")

    except Exception as e:
        st.error(f"Eroare: {e}")



def render_energy_sankey(transfers, deficit_final):
    all_clients = list(set([t['from'] for t in transfers] + [t['to'] for t in transfers]))

    label_map = {client: idx for idx, client in enumerate(all_clients)}
    sources = [label_map[t["from"]] for t in transfers]
    targets = [label_map[t["to"]] for t in transfers]
    values = [round(t["energie_transferata"], 3) for t in transfers]

    # Adăugăm "GRID" ca sursă de ultimă instanță
    grid_idx = len(all_clients)
    for _, row in deficit_final.iterrows():
        if row["Cantitate Energie"] > 0:
            sources.append(grid_idx)
            targets.append(label_map[row["Client"]])
            values.append(round(abs(row["Cantitate Energie"]), 3))

    labels = all_clients + ["GRID"]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=5,
            line=dict(color="black", width=0.3),
            label=labels,
            color="lightblue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=["#00cc96"] * len(transfers) + ["#EF553B"] * (len(sources) - len(transfers))
        )
    )])

    fig.update_layout(title_text="Fluxul de energie între clienți și rețea", font_size=13)
    return fig


def render_transfer_table(transfers_df):
    transfers_df["energie_transferata"] = transfers_df["energie_transferata"].round(3)

    rows_html = ""
    for _, row in transfers_df.iterrows():
        rows_html += f"""
            <tr>
                <td>{row['from']}</td>
                <td><span style="font-size: 18px;">➡️</span></td>
                <td>{row['to']}</td>
                <td style="font-weight: bold; color: #007BFF;">{row['energie_transferata']} MWh</td>
            </tr>
        """

    table_html = f"""
    <style>
        .transfer-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }}
        .transfer-table th, .transfer-table td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        .transfer-table th {{
            background-color: #f0f8ff;
            color: #333;
        }}
        .transfer-table tbody tr:hover {{
            background-color: #e6f2ff;
        }}
    </style>

    <div style="overflow-x:auto; border: 1px solid #ccc; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); margin-top: 16px;">
        <table class="transfer-table">
            <thead>
                <tr>
                    <th>De la</th>
                    <th></th>
                    <th>Către</th>
                    <th>Energie Transferată</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

    st.components.v1.html(table_html, height=350, scrolling=True)


def render_beautiful_table(df):
    # Rotunjim valorile numerice
    df[["consumption_real", "production_real", "lt_real",
        "consumption_forecast", "production_forecast","diferenta", "lt_forecast"]] = \
        df[["consumption_real", "production_real", "lt_real",
            "consumption_forecast", "production_forecast",'diferenta', "lt_forecast"]].round(3)

    # Construim rândurile tabelului
    rows_html = ""
    for _, row in df.iterrows():
        if row["status"] == "Excedent":
            status_bg = "#d4edda"
            status_text = "#155724"
        else:
            status_bg = "#f8d7da"
            status_text = "#721c24"

        rows_html += f"""
            <tr>
                <td>{row['client']}</td>
                <td>{row['ora_ro']}</td>
                <td>{row['consumption_real']}</td>
                <td>{row['production_real']}</td>
                <td>{row['lt_real']}</td>
                <td>{row['consumption_forecast']}</td>
                <td>{row['production_forecast']}</td>
                <td>{row['lt_forecast']}</td>
                <td>{row['diferenta']}</td>
                <td>
                    <span style="background-color: {status_bg}; color: {status_text}; padding: 4px 12px; border-radius: 16px; font-weight: bold;">
                        {row['status']}
                    </span>
                </td>
            </tr>
        """

    # HTML complet cu stiluri moderne
    table_html = f"""
    <style>
        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', sans-serif;
            font-size: 15px;
        }}
        .custom-table thead {{
            background-color: #e9f3ff;
            color: #333;
        }}
        .custom-table th, .custom-table td {{
            padding: 14px 12px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        .custom-table tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .custom-table tbody tr:hover {{
            background-color: #e0f0ff;
        }}
    </style>

    <div style="overflow-x:auto; border: 1px solid #ccc; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); margin-top: 18px;">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Client</th>
                    <th>Ora (RO)</th>
                    <th>Consum Real</th>
                    <th>Producție Reală</th>
                    <th>LT Real</th>
                    <th>Consum Forecast</th>
                    <th>Producție Forecast</th>
                    <th>LT Forecast</th>
                    <th>Cantitate Energie</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

    # Afișăm în Streamlit
    st.components.v1.html(table_html, height=390, scrolling=True)


