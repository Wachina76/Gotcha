import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os
import re
import io

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Turnos Villalba", page_icon="📅", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #ffffff; }
    
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    
    .stTextInput>div>div>input { 
        border-radius: 10px; 
        border: 2px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTADOR (Omitido aquí por brevedad, mantén el tuyo) ---

# 2. INTERFAZ DE USUARIO
st.title("📅 Consultar turno Villalba")

# AVISO DE REFUERZOS (NUEVO)
st.info('**Nota importante:** Los turnos de refuerzo se buscan tal cual están en el tráfico. Ejemplo: `Ref mañana 2` o `Ref tarde 3`.')

st.write("Ingresa siglas del turno para localizarlo")

# 3. LÓGICA DE BÚSQUEDA
NOMBRE_PDF = "base_datos.pdf" 

query = st.text_input("", placeholder="Ejemplo: Ref mañana 2")
btn_buscar = st.button("BUSCAR TURNO")

if btn_buscar and query:
    if os.path.exists(NOMBRE_PDF):
        with st.spinner('Buscando...'):
            # Aquí va tu función buscar_perfeccionado
            # res = buscar_perfeccionado(NOMBRE_PDF, query)
            # ... (resto del código de visualización)
            pass
    else:
        st.error("Archivo no encontrado.")

st.divider()
st.caption("Sistema de búsqueda - Villalba")

