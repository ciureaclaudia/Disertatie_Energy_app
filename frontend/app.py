import streamlit as st
from streamlit_option_menu import option_menu

from frontend_pages import home, production, consumption, clients, statistics, map_page

# === Configura pagina ===
st.set_page_config(
    page_title="⚡ VPP Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
    <style>
    /* Ascunde bara Streamlit de sus și jos */
    #MainMenu, header, footer {
        visibility: hidden;
    }

    /* Container principal mai compact */
    .block-container {
        padding-top: 1rem !important;
    }

    /* Sidebar pe toată înălțimea fără scroll */
    section[data-testid="stSidebar"] {
        height: 100vh !important;
        overflow-y: hidden !important;
        background-color: #f5f5f5 !important;
        padding: 1rem !important;
    }

    /* Elimină containerul alb și shadow */
    div[data-testid="stSidebarNav"] {
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* Elimină padding-ul implicit din option_menu */
    .css-1n76uvr, .css-13hxz1l {
        padding: 0 !important;
        margin: 0 !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Option_menu styling */
    .nav-link {
        font-size: 16px;
        color: #333 !important;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 6px;
    }

    .nav-link:hover {
        background-color: #e0e0e0 !important;
    }

    .nav-link.active {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)




# afisare lista clienti
API_CLIENTS = "http://127.0.0.1:8000/api/clients/"

API_TODAY_CONSUMPTION = "http://127.0.0.1:8000/api/readings/today-consumption/"

API_TODAY_PRODUCTION = "http://127.0.0.1:8000/api/readings/today-production/"

# === Tema / Mod vizual ===
with st.sidebar:

    selected = option_menu(
        menu_title="Meniu VPP",
        options=["Acasă", "Producție", "Consum", "Clienți", "Statistici","Hartă"],
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

        .pulsing-emoji {{
            display: inline-block;
            animation: pulse 1.5s ease-in-out infinite;
        }}

        @keyframes pulse {{
            0%   {{ transform: scale(1); }}
            50%  {{ transform: scale(1.4); }}
            100% {{ transform: scale(1); }}
        }}
    </style>

    <div style='text-align:center; padding:20px; background:linear-gradient(to right, {primary}, #81c784); border-radius:10px;'>
        <h1 style='color:white;'>
            <span class='pulsing-emoji'>⚡</span> Virtual Power Plant Dashboard
        </h1>
        <p style='color:white;'>Monitorizează producția, consumul și performanța energetică</p>
    </div>
""", unsafe_allow_html=True)


# st.markdown(f"""
#     <style>
#         .main {{
#             background-color: {bg};
#         }}
#     </style>
#     <div style='text-align:center; padding:20px; background:linear-gradient(to right, {primary}, #81c784); border-radius:10px;'>
#         <h1 style='color:white;'>⚡ Virtual Power Plant Dashboard</h1>
#         <p style='color:white;'>Monitorizează producția, consumul și performanța energetică</p>
#     </div>
# """, unsafe_allow_html=True)

# === PAGINI ===

if selected == "Acasă":
    home.show(primary, text, card_bg)
elif selected == "Producție":
    production.show(API_TODAY_PRODUCTION)
elif selected == "Consum":
    consumption.show(API_TODAY_CONSUMPTION)
elif selected == "Clienți":
    clients.show(API_CLIENTS, primary)
elif selected == "Statistici":
    statistics.show(primary)
elif selected == "Hartă":
    map_page.show(API_CLIENTS)


