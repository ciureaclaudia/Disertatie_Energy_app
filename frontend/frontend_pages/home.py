# pages/home.py

import streamlit as st
import pandas as pd
import requests
import pytz
import plotly.graph_objects as go

def calculate_diferenta(row):
    if row["lt_real"] < 0 and row["lt_forecast"] < 0:
        return -(row["lt_real"] - row["lt_forecast"])  # schimbăm semnul
    else:
        return row["lt_real"] - row["lt_forecast"]


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
            # df["diferenta"] = df["lt_real"] -df["lt_forecast"]

            df["diferenta"] = df.apply(calculate_diferenta, axis=1)

            df["status"] = df["diferenta"].apply(lambda x: "Excedent" if x >= 0 else "Deficit")

            # df["diferenta"] = df["diferenta"].abs()
            
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
                # fig = render_energy_sankey(result["transfers"], pd.DataFrame(result["deficit"]))
                fig = render_energy_sankey(
    transfers=result["transfers"],
    deficit_final=pd.DataFrame(result["deficit"]),
    excedent_final=pd.DataFrame(result["excedent"])
)

                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error(f"API Error: {response.status_code}")

    except Exception as e:
        st.error(f"Eroare: {e}")



# def render_energy_sankey(transfers, deficit_final):
#     all_clients = list(set([t['from'] for t in transfers] + [t['to'] for t in transfers]))

#     label_map = {client: idx for idx, client in enumerate(all_clients)}
#     sources = [label_map[t["from"]] for t in transfers]
#     targets = [label_map[t["to"]] for t in transfers]
#     values = [round(t["energie_transferata"], 3) for t in transfers]

#     # print(deficit_final[["Client", "Cantitate Energie"]])
#     # st.write(deficit_final[["Client", "Cantitate Energie"]])

#     # # Adăugăm "GRID" ca sursă de ultimă instanță
#     # grid_idx = len(all_clients)
#     # for _, row in deficit_final.iterrows():
#     #     if row["Cantitate Energie"] *(-1) > 0:
#     #         sources.append(grid_idx)
#     #         targets.append(label_map[row["Client"]])
#     #         values.append(round(abs(row["Cantitate Energie"]), 3))

#     # Adăugăm "GRID" ca sursă de ultimă instanță
#     grid_idx = len(label_map)  # actual, nu al vechiului all_clients
#     for _, row in deficit_final.iterrows():
#         client = row["Client"]
#         if row["Cantitate Energie"] < 0:
#             if client not in label_map:
#                 label_map[client] = len(label_map)  # adaugă client nou
#             sources.append(grid_idx)
#             targets.append(label_map[client])
#             values.append(round(abs(row["Cantitate Energie"]), 3))


#     # labels = all_clients + ["GRID"]
    
#     labels = list(label_map.keys()) + ["GRID"]
#     st.write(len(labels), max(sources), max(targets))
#     link_labels = [
#     f"De la {labels[src]} către {labels[tgt]}<br>Transfer: {val} MWh"
#     for src, tgt, val in zip(sources, targets, values)
#     ]   


#     fig = go.Figure(data=[go.Sankey(
#         node=dict(
#             pad=25,
#             thickness=25,
#             line=dict(color="black", width=1.3),
#             label=labels,
#             color="lightblue",
#             # color="rgba(51, 102, 153, 1)",
#             hovertemplate='%{label}<extra></extra>',
#         ),
#         link=dict(
#             source=sources,
#             target=targets,
#             value=values,
#             color=["#00cc96"] * len(transfers) + ["#EF553B"] * (len(sources) - len(transfers)),
#             customdata=link_labels,
#             hovertemplate='De la %{source.label} către %{target.label}<br>Transfer: %{value} MWh<extra></extra>'
#         )
#     )])

#     # fig.update_layout(title_text="Fluxul de energie între clienți și rețea", font_size=13)
#     fig.update_layout(
#         title_text="🔋 Fluxul de energie între clienți și rețea",
#         font=dict(size=18, color="black", family="Arial"),
#         height=500,
#         autosize=True,
#         paper_bgcolor='white',
#         plot_bgcolor='white',
#         margin=dict(l=30, r=30, t=70, b=30)
#     )

#     return fig


def render_energy_sankey(transfers, deficit_final, excedent_final):
    # 1. Construim label_map din toți clienții din transferuri
    label_map = {}
    current_index = 0

    for t in transfers:
        for client in [t["from"], t["to"]]:
            if client not in label_map:
                label_map[client] = current_index
                current_index += 1

    # 2. Adaugăm GRID ca ultim nod
    grid_idx = current_index
    label_map["GRID"] = grid_idx
    current_index += 1

    # 3. Construim surse/ținte/valori pentru transferurile între clienți
    sources = [label_map[t["from"]] for t in transfers]
    targets = [label_map[t["to"]] for t in transfers]
    values  = [round(t["energie_transferata"], 3) for t in transfers]

    # 4. Adăugăm transferuri GRID -> clienți în deficit
    for _, row in deficit_final.iterrows():
        client = row["Client"]
        energie = row["Cantitate Energie"]
        if energie < 0:
            if client not in label_map:
                label_map[client] = current_index
                current_index += 1
            sources.append(label_map["GRID"])
            targets.append(label_map[client])
            values.append(round(abs(energie), 3))

    # 5. Adăugăm transferuri clienți -> GRID pentru excedent nefolosit
    for _, row in excedent_final.iterrows():
        client = row["Client"]
        energie = row["Cantitate Energie"]
        if energie > 0:
            if client not in label_map:
                label_map[client] = current_index
                current_index += 1
            sources.append(label_map[client])
            targets.append(label_map["GRID"])
            values.append(round(energie, 3))

    # 6. Refacem labels după label_map
    labels = [client for client, _ in sorted(label_map.items(), key=lambda x: x[1])]

    # 7. Hover text personalizat
    link_labels = [
        f"De la {labels[src]} către {labels[tgt]}<br>Transfer: {val} MWh"
        for src, tgt, val in zip(sources, targets, values)
    ]

    # 8. Plot Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=25,
            line=dict(color="light blue", width=1),
            label=labels,
            color="lightblue",
            hovertemplate='%{label}<extra></extra>',
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=["#aaeda8"] * len(transfers) +
                  ["#edd5a8"] * (len(sources) - len(transfers)),
            customdata=link_labels,
            hovertemplate='%{customdata}<extra></extra>'
        )
    )])

    fig.update_layout(
        title_text="🔋 Fluxul de energie între clienți și rețea",
        font=dict(size=20, color="white", family="Arial Black"),
        height=500,
        autosize=True,
        paper_bgcolor="#e6f2f2",
        plot_bgcolor='white',
        margin=dict(l=30, r=30, t=70, b=30),
        hoverlabel=dict(
        bgcolor="rgba(0,0,0,0.85)",
        font_size=16,
        font_family="Arial",
        font_color="white"
    )
    )

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
                <td style="font-weight: bold;">{row['lt_real']}</td>
                <td>{row['consumption_forecast']}</td>
                <td>{row['production_forecast']}</td>
                <td style="font-weight: bold;">{row['lt_forecast']}</td>
                <td style="font-weight: bold;">{row['diferenta']}</td>
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


