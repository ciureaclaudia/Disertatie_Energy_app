import streamlit as st
from streamlit_option_menu import option_menu

# Setări pagină
st.set_page_config(page_title="Disertație Energy App", layout="wide")

# Meniu lateral
with st.sidebar:
    selected = option_menu(
        menu_title="Meniu",
        options=["Acasă", "Clienți", "Grafic energie", "Despre"],
        icons=["house", "people", "bar-chart", "info-circle"],
        default_index=0,
    )

# Conținut pagină în funcție de selecție
if selected == "Acasă":
    st.title("🏠 Bine ai venit în aplicația Disertație")
    st.write("Aceasta este o aplicație pentru vizualizarea producției și consumului de energie.")

elif selected == "Clienți":
    st.title("📋 Lista clienților")
    st.write("Aici vei vedea lista clienților preluați din API.")

elif selected == "Grafic energie":
    st.title("📊 Vizualizare consum și producție")
    st.write("Aici poți vizualiza graficele pentru energie.")

elif selected == "Despre":
    st.title("ℹ️ Despre proiect")
    st.markdown("""
    - Autor: Claudia Maria Ciurea  
    - Aplicație disertație 2025  
    - Tehnologii: Django, PostgreSQL, Streamlit  
    """)

