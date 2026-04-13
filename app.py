import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Turnos Villalba", page_icon="📅", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #ffffff; }
    .stTextInput>div>div>input { 
        border-radius: 10px; 
        border: 2px solid #e0e0e0;
    }
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. NOMBRE DEL ARCHIVO EN GITHUB
NOMBRE_PDF = "base_datos.pdf" 

def buscar_en_catalogo(pdf_path, query):
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    query = query.lower().strip()

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina = pagina.get_text().lower()
        
        if query in texto_pagina:
            instancias = pagina.search_for(query)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            resultados.append({"pagina": num_pagina + 1, "imagen": img})
            
    return resultados

# 3. INTERFAZ DE USUARIO ACTUALIZADA
st.title("📅 Consultar turno Villalba")
st.write("Ingresa tu nombre, DNI o fecha para localizar tu turno en el sistema.")

if os.path.exists(NOMBRE_PDF):
    # Campo de búsqueda
    query = st.text_input("", placeholder="🔍 Escribe aquí para buscar tu turno...")

    if query:
        with st.spinner('Buscando turno...'):
            res = buscar_en_catalogo(NOMBRE_PDF, query)
            
            if res:
                st.info(f"Se han encontrado {len(res)} coincidencia(s).")
                for item in res:
                    with st.expander(f"📄 Información del Turno - Página {item['pagina']}", expanded=True):
                        st.image(item['imagen'], use_container_width=True)
            else:
                st.warning("No se encontraron turnos con ese dato. Revisa si está bien escrito.")
else:
    st.error("Archivo 'base_datos.pdf' no encontrado. Asegúrate de subir la lista de turnos a GitHub con ese nombre.")

st.divider()
st.caption("Sistema de consulta de turnos - Villalba")
 
