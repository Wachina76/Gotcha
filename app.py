import streamlit as st
import fitz  # PyMuPDF
from PIL import Image

def buscar_y_resaltar(file_bytes, query):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    resultados = []

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        # Buscar todas las instancias de la palabra
        instancias = pagina.search_for(query)
        
        if instancias:
            # Resaltar cada instancia en el PDF
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Convertir la página a imagen para mostrarla en la app
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2)) # Zoom 2x para calidad
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img,
                "texto": pagina.get_text()
            })
    return resultados

# --- Interfaz de Streamlit ---
st.title("🛠️ Localizador Visual de Servicios")

archivo = st.file_uploader("Sube tu catálogo (PDF)", type="pdf")
query = st.text_input("Servicio a localizar:")

if archivo and query:
    pdf_bytes = archivo.read()
    resultados = buscar_y_resaltar(pdf_bytes, query)
    
    if resultados:
        st.success(f"Encontrado en {len(resultados)} páginas")
        for res in resultados:
            with st.expander(f"📍 Ver resultado en Página {res['pagina']}", expanded=True):
                st.image(res['imagen'], use_container_width=True)
    else:
        st.error("No se encontró el servicio solicitado.")