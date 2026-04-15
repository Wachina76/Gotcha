import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os
import re
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Turnos Villalba", page_icon="📅", layout="centered")

# --- LÓGICA DEL CONTADOR ---
CONTADOR_FILE = "contador.txt"
def actualizar_contador():
    try:
        if not os.path.exists(CONTADOR_FILE):
            with open(CONTADOR_FILE, "w") as f: f.write("0")
        with open(CONTADOR_FILE, "r") as f:
            vistas = int(f.read().strip() or 0)
        vistas += 1
        with open(CONTADOR_FILE, "w") as f: f.write(str(vistas))
        return vistas
    except: return 0

total_vistas = actualizar_contador()

# --- ESTILO CSS ---
st.markdown(f"""
    <style>
    .vistas-box {{
        background-color: #f1f8e9;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        color: #2e7d32;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    div.stButton > button {{
        background-color: #d32f2f !important;
        color: white !important;
        height: 3em;
        width: 100%;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA ---
def buscar_en_pdf(pdf_path, query):
    if not os.path.exists(pdf_path): return None
    doc = fitz.open(pdf_path)
    resultados = []
    query_clean = " ".join(query.lower().split())
    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina = " ".join(pagina.get_text().lower().split())
        if query_clean in texto_pagina:
            instancias = pagina.search_for(query)
            for inst in instancias:
                annot = pagina.add_highlight_annot(inst)
                annot.set_colors(stroke=(1, 0, 0)) 
                annot.update()
            pix = pagina.get_pixmap(matrix=fitz.Matrix(3.5, 3.5)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            resultados.append({"pagina": num_pagina + 1, "imagen": img, "bytes": img_byte_arr.getvalue()})
    doc.close()
    return resultados

# --- INTERFAZ ---
st.markdown(f'<div class="vistas-box">📊 Visualizaciones totales: {total_vistas}</div>', unsafe_allow_html=True)
st.title("📅 Sistema Villalba")

# CREACIÓN DE PESTAÑAS
tab1, tab2 = st.tabs(["📋 Turnos Ordinarios", "☀️ Turnos de Verano"])

# PESTAÑA 1: TURNOS NORMALES
with tab1:
    st.subheader("Buscador de Turnos Diarios")
    q1 = st.text_input("Ingresa siglas (Ej: MJP5):", key="q1")
    if st.button("BUSCAR TURNO ORDINARIO"):
        if q1:
            res = buscar_en_pdf("base_datos.pdf", q1)
            if res:
                for item in res:
                    st.image(item['imagen'], use_container_width=True)
            else: st.warning("No encontrado en listado ordinario.")

# PESTAÑA 2: TURNOS DE VERANO
with tab2:
    st.subheader("Buscador Especial Verano")
    st.info("Utiliza este buscador para consultar el cuadrante de la temporada de verano.")
    q2 = st.text_input("Ingresa siglas o refuerzo verano:", key="q2")
    if st.button("BUSCAR EN VERANO"):
        if q2:
            # Asegúrate de subir un archivo llamado 'base_datos_verano.pdf' a GitHub
            res = buscar_en_pdf("base_datos_verano.pdf", q2)
            if res:
                for item in res:
                    st.image(item['imagen'], use_container_width=True)
            else: st.warning("No encontrado en listado de verano.")

st.divider()
st.caption("Villalba App - Consulta Multibase")
