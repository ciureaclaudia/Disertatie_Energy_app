import streamlit as st
from streamlit_option_menu import option_menu

from frontend_pages import home, production, consumption, clients, statistics

# === Configura pagina ===
st.set_page_config(
    page_title="⚡ VPP Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
    <style>
        /* Ascunde complet bara de sus Deploy, Rerun, etc */
        #MainMenu, header, footer {
            visibility: hidden !important;
            height: 0px !important;
        }

        /*  Micșorează spațiul dintre header și conținut */
        .block-container {
            padding-top: 1rem !important;
        }

         <style>
    /* Extinde sidebar-ul pe toată înălțimea ferestrei */
    section[data-testid="stSidebar"] {
        height: 100vh !important;
        overflow-y: auto !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Meniu mai compact */
    .css-1lcbmhc {
        flex-grow: 1;
    }

    /* Iconul din switch */
    .stToggleSwitch [data-testid="stMarkdownContainer"] {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    </style>
""", unsafe_allow_html=True)


# afisare lista clienti
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
    home.show(primary, text, card_bg)
elif selected == "Producție":
    production.show()
elif selected == "Consum":
    consumption.show()
elif selected == "Clienți":
    clients.show(API_CLIENTS, primary)
elif selected == "Statistici":
    statistics.show(primary)


