import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os
import re

# 1. CONFIGURACIÓN VISUAL Y HABILITACIÓN DE ZOOM
st.set_page_config(page_title="Turnos Villalba", page_icon="📅", layout="centered")

# Inyectamos el meta tag para permitir zoom en dispositivos móviles
st.markdown("""
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    </head>
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #ffffff; }
    
    /* Hace que la imagen sea interactiva al tacto */
    img {
        cursor: zoom-in;
    }
    
    .stTextInput>div>div>input { 
        border-radius: 10px; 
        border: 2px solid #2e7d32;
        font-size: 18px !important; /* Texto más grande para que el móvil no haga auto-zoom al escribir */
    }
    .streamlit-expanderHeader {
        background-color: #e8f5e9;
        border-radius: 10px;
        font-weight: bold;
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
            
            # Subimos el zoom del renderizado a 3.0 para que al ampliar en el móvil se vea nítido
            pix = pagina.get_pixmap(matrix=fitz.Matrix(3, 3)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            prioridad = 1 if re.search(rf'\b{re.escape(query_clean)}\b', texto_pagina) else 2
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "prioridad": prioridad
            })
    
    return sorted(resultados, key=lambda x: x['prioridad'])

# 3. INTERFAZ DE USUARIO
st.title("📅 Consultar turno Villalba")
st.write("Ingresa siglas del turno para localizarlo en el sistema")

if os.path.exists(NOMBRE_PDF):
    query = st.text_input("", placeholder="🔍 Ejemplo: MJP5")

    if query:
        with st.spinner('Localizando turno...'):
            res = buscar_perfeccionado(NOMBRE_PDF, query)
            
            if res:
                st.success(f"Resultados para: {query}")
                for item in res:
                    etiqueta = "✅ Coincidencia Principal" if item['prioridad'] == 1 else "📄 Mención en página"
                    with st.expander(f"{etiqueta} - Página {item['pagina']}", expanded=True):
                        # Mostramos la imagen ocupando todo el ancho disponible
                        st.image(item['imagen'], use_container_width=True)
                        st.caption("Puedes usar dos dedos sobre la pantalla para ampliar la imagen.")
            else:
                st.warning(f"No se encontró ninguna referencia a '{query}'.")
else:
    st.error("Error: Sube el archivo 'base_datos.pdf' a GitHub.")

st.divider()
st.caption("Sistema optimizado con Zoom - Villalba")
