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
        background-color: #ffebee;
        color: #c62828;
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 10px;
        border-left: 5px solid #d32f2f;
    }}
    div.stButton > button {{
        background-color: #d32f2f !important;
        color: white !important;
        height: 3.5em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE BÚSQUEDA ULTRA-FLEXIBLE ---
def buscar_flexible_rojo(pdf_path, query):
    if not os.path.exists(pdf_path): return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    
    # 1. Normalizar la búsqueda del usuario (ej: "Ref  tarde" -> "ref tarde")
    query_clean = " ".join(query.lower().split())

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        # 2. Normalizar el texto de la página para evitar fallos por espacios dobles
        texto_pagina_raw = pagina.get_text().lower()
        texto_pagina_clean = " ".join(texto_pagina_raw.split())
        
        # 3. Comprobar si existe la coincidencia
        if query_clean in texto_pagina_clean:
            # Lógica de clasificación
            tipo = "Ubicación general"
            if "sin disco" in texto_pagina_clean: tipo = "📍 Ubicado en: SIN DISCO"
            elif "con disco" in texto_pagina_clean: tipo = "📍 Ubicado en: CON DISCO"
            elif "ref" in query_clean: tipo = "📍 Tipo: TURNO DE REFUERZO"

            # 4. Intentar resaltar (Probamos varios métodos si uno falla)
            instancias = pagina.search_for(query)
            if not instancias:
                # Si no lo halla exacto, busca la primera palabra para no dejar la página vacía
                instancias = pagina.search_for(query.split()[0])

            for inst in instancias:
                annot = pagina.add_highlight_annot(inst)
                annot.set_colors(stroke=(1, 0, 0)) 
                annot.set_opacity(0.8)
                annot.update()
            
            # 5. Renderizado HD
            pix = pagina.get_pixmap(matrix=fitz.Matrix(4, 4)) 
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "bytes": img_byte_arr.getvalue(),
                "clasificacion": tipo
            })
    doc.close()
    return resultados

# --- INTERFAZ ---
st.markdown(f'<div class="vistas-box">📊 Visualizaciones totales: {total_vistas}</div>', unsafe_allow_html=True)
st.title("📅 Consultar turno Villalba")

st.info('**Nota:** Para refuerzos, busca exactamente como en el tráfico. Ejemplo: `Ref tarde 3`.')

query = st.text_input("Ingresa siglas o turno:", placeholder="Ejemplo: Ref tarde 3")
btn_buscar = st.button("BUSCAR TURNO")

if btn_buscar and query:
    archivo_pdf = "base_datos.pdf" 
    if os.path.exists(archivo_pdf):
        with st.spinner('Escaneando base de datos...'):
            resultados = buscar_flexible_rojo(archivo_pdf, query)
            if resultados:
                st.success(f"Resultados encontrados para '{query}':")
                for i, item in enumerate(resultados):
                    st.markdown(f'<div class="etiqueta-info">{item["clasificacion"]}</div>', unsafe_allow_html=True)
                    st.download_button(
                        label=f"🔍 Abrir Página {item['pagina']} (Zoom HD)",
                        data=item['bytes'],
                        file_name=f"turno_pag_{item['pagina']}.png",
                        mime="image/png",
                        key=f"dl_{i}"
                    )
                    st.image(item['imagen'], use_container_width=True)
                    st.divider()
            else:
                st.warning("No se encontró. Prueba escribiendo solo una parte (ej: 'Ref tarde').")
    else:
        st.error("Archivo 'base_datos.pdf' no encontrado.")

st.caption("Sistema de consulta Villalba - v2.0")
