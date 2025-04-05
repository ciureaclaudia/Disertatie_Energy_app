# Disertație Energy App

Aceasta este o aplicație web pentru monitorizarea și vizualizarea producției și consumului de energie regenerabilă, dezvoltată ca parte a lucrării de disertație.

# Autor
Claudia Maria Ciurea – Disertație 2025 – Aplicație pentru managementul energiei verzi

## Structură

- `backend/` – Django + PostgreSQL
- `frontend/` – Streamlit (UI)

## Setup

### 1. Clonează repository-ul

```bash
git clone https://github.com/ciureaclaudia/Disertatie_Energy_app.git
cd Disertatie_Energy_app

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Rulează serverul
python manage.py runserver

### 3. Frontend
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Rulează aplicația
streamlit run app.py


## Tehnologii folosite

Backend: Django, Django Rest Framework, PostgreSQL

Frontend: Streamlit, Pandas, Altair

Altele: Git, GitHub, REST API, Python virtual environments

