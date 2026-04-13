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
    except: return 0

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
    .etiqueta-info {{
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 10px;
        border-left: 5px solid #2196f3;
    }}
    div.stButton > button {{
        background-color: #2e7d32 !important;
        color: white !important;
        height: 3.5em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA CON DETECCIÓN DE TIPO ---
def buscar_y_clasificar(pdf_path, query):
    if not os.path.exists(pdf_path): return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    query_clean = " ".join(query.lower().split())

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina = pagina.get_text().lower()
        
        if query_clean in " ".join(texto_pagina.split()):
            # LÓGICA DE DETECCIÓN DE "DISCO"
            tipo_ubicacion = "Ubicación general"
            if "sin disco" in texto_pagina:
                tipo_ubicacion = "📍 Ubicado en: SIN DISCO"
            elif "con disco" in texto_pagina:
                tipo_ubicacion = "📍 Ubicado en: CON DISCO"
            elif "refuerzo" in texto_pagina:
                tipo_ubicacion = "📍 Tipo: TURNO DE REFUERZO"

            # Resaltado
            instancias = pagina.search_for(query)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Imagen alta calidad
            pix = pagina.get_pixmap(matrix=fitz.Matrix(3.5, 3.5)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "bytes": img_byte_arr.getvalue(),
                "clasificacion": tipo_ubicacion
            })
    doc.close()
    return resultados

# --- INTERFAZ ---
st.markdown(f'<div class="vistas-box">📊 Visualizaciones totales: {total_vistas}</div>', unsafe_allow_html=True)
st.title("📅 Consultar turno Villalba")

st.info('**Nota:** Los refuerzos se buscan tal cual el tráfico. Ejemplo: `Ref mañana 2`')

query = st.text_input("Ingresa siglas o nombre del turno:", placeholder="Ejemplo: MJP5")
btn_buscar = st.button("BUSCAR TURNO")

if btn_buscar and query:
    archivo_pdf = "base_datos.pdf" 
    if os.path.exists(archivo_pdf):
        with st.spinner('Analizando archivos...'):
            resultados = buscar_y_clasificar(archivo_pdf, query)
            if resultados:
                st.success(f"Encontrado para '{query}':")
                for i, item in enumerate(resultados):
                    # MOSTRAR LA CLASIFICACIÓN (Sin disco / Con disco)
                    st.markdown(f'<div class="etiqueta-info">{item["clasificacion"]}</div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label=f"🔍 Abrir Página {item['pagina']} en HD",
                        data=item['bytes'],
                        file_name=f"turno_pag_{item['pagina']}.png",
                        mime="image/png",
                        key=f"dl_{i}"
                    )
                    st.image(item['imagen'], use_container_width=True)
                    st.divider()
            else:
                st.warning("No se encontró el turno. Revisa las siglas.")
    else:
        st.error("Sube 'base_datos.pdf' a GitHub.")

st.caption("Sistema de consulta inteligente - Villalba")

