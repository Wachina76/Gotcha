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
            contenido = f.read().strip()
            vistas = int(contenido) if contenido else 0
        vistas += 1
        with open(CONTADOR_FILE, "w") as f: f.write(str(vistas))
        return vistas
    except:
        return 0

total_vistas = actualizar_contador()

# --- ESTILO CSS ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .vistas-box {{
        background-color: #f1f8e9;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        color: #2e7d32;
        font-weight: bold;
        margin-bottom: 20px;
        border: 1px solid #c8e6c9;
    }}
    /* Estilo del Botón Buscar */
    div.stButton > button {{
        background-color: #2e7d32 !important;
        color: white !important;
        height: 3.5em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        border: none;
        cursor: pointer;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA ---
def buscar_en_pdf(pdf_path, query):
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    # Normalizamos la búsqueda: quitamos espacios extra y pasamos a minúsculas
    query_clean = " ".join(query.lower().split())

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        # Extraemos texto normalizado de la página
        texto_pagina = " ".join(pagina.get_text().lower().split())
        
        if query_clean in texto_pagina:
            # Resaltar en el PDF original
            instancias = pagina.search_for(query)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Renderizar imagen en alta calidad
            pix = pagina.get_pixmap(matrix=fitz.Matrix(3.5, 3.5)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Preparar bytes para descarga
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "bytes": img_byte_arr.getvalue()
            })
    doc.close()
    return resultados

# --- INTERFAZ PRINCIPAL ---
st.markdown(f'<div class="vistas-box">📊 Visualizaciones totales: {total_vistas}</div>', unsafe_allow_html=True)

st.title("📅 Consultar turno Villalba")

# Aviso importante
st.info('**Nota importante:** Los turnos de refuerzo se buscan tal cual están en el tráfico. Ejemplo: `Ref mañana 2` o `Ref tarde 3`.')

# Input de búsqueda
query = st.text_input("Ingresa siglas o nombre del turno:", placeholder="Ejemplo: Ref mañana 2")

# El botón ahora está vinculado a una variable
boton_pulsado = st.button("BUSCAR TURNO")

# Solo se ejecuta si se pulsa el botón
if boton_pulsado:
    if query:
        # Reemplaza 'base_datos.pdf' por el nombre exacto de tu archivo en GitHub
        archivo_pdf = "base_datos.pdf" 
        
        if os.path.exists(archivo_pdf):
            with st.spinner('Buscando en el sistema...'):
                resultados = buscar_en_pdf(archivo_pdf, query)
                
                if resultados:
                    st.success(f"Se han encontrado {len(resultados)} coincidencia(s) para '{query}'")
                    for i, item in enumerate(resultados):
                        st.subheader(f"Página {item['pagina']}")
                        # Botón para descargar/ver en grande
                        st.download_button(
                            label="🔍 Ver imagen en tamaño completo (Zoom)",
                            data=item['bytes'],
                            file_name=f"turno_pag_{item['pagina']}.png",
                            mime="image/png",
                            key=f"dl_{i}"
                        )
                        st.image(item['imagen'], use_container_width=True)
                        st.divider()
                else:
                    st.warning(f"No se encontró nada para '{query}'. Revisa si está bien escrito.")
        else:
            st.error(f"Error: No se encuentra el archivo '{archivo_pdf}' en GitHub.")
    else:
        st.error("Escribe algo en el buscador antes de pulsar el botón.")

st.divider()
st.caption("Sistema de consulta - Villalba")

