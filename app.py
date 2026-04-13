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
    
    /* Botón de búsqueda principal en verde */
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }
    
    .stTextInput>div>div>input { 
        border-radius: 10px; 
        border: 2px solid #2e7d32;
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. RUTA DEL ARCHIVO
NOMBRE_PDF = "base_datos.pdf" 

def buscar_perfeccionado(pdf_path, query):
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    query_clean = query.lower().strip()

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina = pagina.get_text().lower()
        
        if query_clean in texto_pagina:
            instancias = pagina.search_for(query_clean)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Alta resolución 4x para compensar la falta de zoom táctil
            pix = pagina.get_pixmap(matrix=fitz.Matrix(4, 4)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            prioridad = 1 if re.search(rf'\b{re.escape(query_clean)}\b', texto_pagina) else 2
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "bytes": img_byte_arr,
                "prioridad": prioridad
            })
    
    return sorted(resultados, key=lambda x: x['prioridad'])

# 3. INTERFAZ DE USUARIO
st.title("📅 Consultar turno Villalba")
st.write("Ingresa siglas del turno para localizarlo")

# Creamos el campo de texto
query = st.text_input("", placeholder="Ejemplo: MJP5")

# AÑADIMOS EL BOTÓN DE BUSCAR
btn_buscar = st.button("BUSCAR TURNO")

# Solo si se pulsa el botón o se da a Enter en el teclado
if btn_buscar and query:
    with st.spinner('Buscando en el sistema...'):
        res = buscar_perfeccionado(NOMBRE_PDF, query)
        
        if res:
            st.success(f"Resultados para: {query}")
            for i, item in enumerate(res):
                with st.container():
                    st.subheader(f"Página {item['pagina']}")
                    
                    # Opción para ver en grande si el zoom falla
                    st.download_button(
                        label="🔍 Ver imagen en tamaño completo",
                        data=item['bytes'],
                        file_name=f"turno_{query}_pag_{item['pagina']}.png",
                        mime="image/png",
                        key=f"btn_{i}"
                    )
                    
                    st.image(item['imagen'], use_container_width=True)
                    st.divider()
        else:
            st.warning(f"No se encontró ninguna coincidencia para '{query}'.")
elif btn_buscar and not query:
    st.error("Por favor, escribe las siglas antes de buscar.")

if not os.path.exists(NOMBRE_PDF):
    st.error("Archivo 'base_datos.pdf' no detectado en GitHub.")

st.divider()
st.caption("Sistema de búsqueda - Villalba")
