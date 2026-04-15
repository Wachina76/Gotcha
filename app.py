import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os
import re
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Turnos Villalba", page_icon="📅", layout="centered")

# --- LÓGICA DEL CONTADOR DE VISUALIZACIONES ---
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

# --- ESTILO VISUAL PERSONALIZADO (CSS) ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Caja del contador */
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
    
    /* Botones de búsqueda en rojo */
    div.stButton > button {{
        background-color: #d32f2f !important;
        color: white !important;
        height: 3.5em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        border: none;
    }}
    
    /* Etiquetas de ubicación (Sin disco/Con disco) */
    .etiqueta-info {{
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        margin-top: 10px;
        border-left: 5px solid #2196f3;
    }}
    
    /* Inputs de texto */
    .stTextInput>div>div>input {{
        border-radius: 10px;
        border: 2px solid #d32f2f;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA MEJORADA (ZOOM 4X + RESALTADO ROJO) ---
def buscar_en_pdf(pdf_path, query):
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    # Limpiamos espacios extra en la búsqueda
    query_clean = " ".join(query.lower().split())

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina_raw = pagina.get_text().lower()
        texto_pagina_clean = " ".join(texto_pagina_raw.split())
        
        if query_clean in texto_pagina_clean:
            # Detectar si es Sin Disco o Con Disco
            ubicacion = "Ubicación General"
            if "sin disco" in texto_pagina_clean:
                ubicacion = "📍 Ubicado en: SIN DISCO"
            elif "con disco" in texto_pagina_clean:
                ubicacion = "📍 Ubicado en: CON DISCO"
            elif "ref" in query_clean:
                ubicacion = "📍 Tipo: TURNO DE REFUERZO"

            # Resaltado en ROJO
            instancias = pagina.search_for(query)
            if not instancias: # Búsqueda de respaldo
                instancias = pagina.search_for(query.split()[0])
                
            for inst in instancias:
                annot = pagina.add_highlight_annot(inst)
                annot.set_colors(stroke=(1, 0, 0)) # Rojo puro
                annot.set_opacity(0.7)
                annot.update()
            
            # RENDERIZADO ALTA CALIDAD (ZOOM 4X)
            # Matrix(4,4) asegura que al ampliar no se vea borroso
            pix = pagina.get_pixmap(matrix=fitz.Matrix(4, 4)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Preparar bytes para el botón de Zoom
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "bytes": img_bytes,
                "info": ubicacion
            })
    doc.close()
    return resultados

# --- INTERFAZ PRINCIPAL ---
st.markdown(f'<div class="vistas-box">📊 Visualizaciones totales: {total_vistas}</div>', unsafe_allow_html=True)
st.title("📅 Sistema de Turnos Villalba")

# Nota informativa para los usuarios
st.warning('**Recordatorio:** Los refuerzos se buscan como en el tráfico (ej: `Ref mañana 2`). El turno aparecerá marcado en **ROJO**.')

# CONFIGURACIÓN DE PESTAÑAS
tab1, tab2 = st.tabs(["📋 LISTADO ORDINARIO", "☀️ LISTADO VERANO"])

# --- PESTAÑA 1: ORDINARIO ---
with tab1:
    st.subheader("Buscador Diario")
    query_ord = st.text_input("Ingresa turno o siglas:", placeholder="Ej: MJP5 o Ref tarde 1", key="input_ord")
    btn_ord = st.button("BUSCAR EN ORDINARIO", key="btn_ord")
    
    if btn_ord and query_ord:
        with st.spinner('Buscando...'):
            res = buscar_en_pdf("base_datos.pdf", query_ord)
            if res:
                st.success(f"Encontrado en Listado Ordinario")
                for i, item in enumerate(res):
                    st.markdown(f'<div class="etiqueta-info">{item["info"]}</div>', unsafe_allow_html=True)
                    st.download_button(
                        label=f"🔍 VER PÁGINA {item['pagina']} EN GRANDE (ZOOM)",
                        data=item['bytes'],
                        file_name=f"ordinario_pag_{item['pagina']}.png",
                        mime="image/png",
                        key=f"zoom_ord_{i}"
                    )
                    st.image(item['imagen'], use_container_width=True)
                    st.divider()
            else:
                st.error("No se encontró coincidencia en el listado ordinario.")

# --- PESTAÑA 2: VERANO ---
with tab2:
    st.subheader("Buscador de Verano")
    query_ver = st.text_input("Ingresa turno de verano:", placeholder="Ej: Ref verano 1", key="input_ver")
    btn_ver = st.button("BUSCAR EN VERANO", key="btn_ver")
    
    if btn_ver and query_ver:
        with st.spinner('Buscando en verano...'):
            res = buscar_en_pdf("base_datos_verano.pdf", query_ver)
            if res:
                st.success(f"Encontrado en Listado de Verano")
                for i, item in enumerate(res):
                    st.markdown(f'<div class="etiqueta-info">{item["info"]}</div>', unsafe_allow_html=True)
                    st.download_button(
                        label=f"🔍 VER PÁGINA {item['pagina']} EN GRANDE (ZOOM)",
                        data=item['bytes'],
                        file_name=f"verano_pag_{item['pagina']}.png",
                        mime="image/png",
                        key=f"zoom_ver_{i}"
                    )
                    st.image(item['imagen'], use_container_width=True)
                    st.divider()
            else:
                st.error("No se encontró coincidencia en el listado de verano.")

st.divider()
st.caption("Villalba App v3.0 - Consulta de cuadrantes")

