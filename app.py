import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Catálogo Digital", page_icon="📖", layout="centered")

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
    /* Estilo para resaltar los expanders */
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
            # Resaltar la palabra encontrada
            instancias = pagina.search_for(query)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Generar imagen de alta calidad (zoom 2x para lectura clara)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            resultados.append({"pagina": num_pagina + 1, "imagen": img})
            
    return resultados

# 3. INTERFAZ DE USUARIO
st.title("📖 Consulta de Catálogo")
st.write("Escribe una palabra clave para localizar la página del servicio.")

if os.path.exists(NOMBRE_PDF):
    # Campo de búsqueda
    query = st.text_input("", placeholder="🔍 Buscar servicio, producto o profesional...")

    if query:
        with st.spinner('Localizando en el documento...'):
            res = buscar_en_catalogo(NOMBRE_PDF, query)
            
            if res:
                st.info(f"Se encontraron {len(res)} coincidencias en el catálogo.")
                for item in res:
                    # Usamos un contenedor expandible para cada página encontrada
                    with st.expander(f"📄 Página {item['pagina']}", expanded=True):
                        st.image(item['imagen'], use_container_width=True)
                        st.caption(f"Visualizando página {item['pagina']} del archivo oficial.")
            else:
                st.warning("No se encontraron resultados. Intenta con un término más general.")
else:
    st.error("Archivo 'base_datos.pdf' no detectado. Por favor, súbelo a tu repositorio de GitHub.")

st.divider()
st.caption("Uso interno - Buscador de servicios basado en PDF")
      
  
 
