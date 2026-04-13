import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero)
st.set_page_config(
    page_title="Service Finder Pro",
    page_icon="🔍",
    layout="centered"
)

# 2. ESTILO CSS PARA MÓVIL (Oculta menús y mejora botones)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3em;
        background-color: #25D366;
        color: white;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN DE BÚSQUEDA Y RESALTADO
def buscar_y_resaltar(file_bytes, query):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    resultados = []

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        instancias = pagina.search_for(query)
        
        if instancias:
            # Añadir resaltado amarillo
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            # Convertir página a imagen (zoom 1.5 para que no pese tanto en el móvil)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            resultados.append({
                "pagina": num_pagina + 1,
                "imagen": img
            })
    return resultados

# 4. INTERFAZ DE USUARIO
st.title("🔍 Buscador de Servicios")
st.write("Encuentra profesionales en el catálogo y contáctalos por WhatsApp.")

# Barra lateral para subir el archivo
with st.sidebar:
    st.header("Admin")
    archivo = st.file_uploader("Sube el catálogo PDF", type="pdf")

# Buscador principal
query = st.text_input("¿Qué servicio buscas?", placeholder="Ej: Electricista, Pintor...")

if archivo and query:
    # Leemos el archivo una sola vez
    pdf_bytes = archivo.read()
    res = buscar_y_resaltar(pdf_bytes, query)
    
    if res:
        st.success(f"Encontrado en {len(res)} páginas")
        for i, item in enumerate(res):
            with st.container():
                st.subheader(f"Resultado en Página {item['pagina']}")
                st.image(item['imagen'], use_container_width=True)
                
                # Sección de contacto
                tel = st.text_input(f"Introduce el teléfono de esta página (con código de país)", 
                                  placeholder="Ej: 34600112233", 
                                  key=f"input_{i}")
                
                if tel:
                    msg = urllib.parse.quote(f"Hola, te encontré en el buscador. Me interesa el servicio de {query}.")
                    url_wa = f"https://wa.me/{tel}?text={msg}"
                    st.markdown(f'<a href="{url_wa}" target="_blank"><button style="width:100%; border-radius:25px; height:3em; background-color:#25D366; color:white; font-weight:bold; border:none; cursor:pointer;">Enviar WhatsApp 💬</button></a>', unsafe_allow_html=True)
                st.divider()
    else:
        st.warning("No se encontraron coincidencias para esa palabra.")

elif not archivo:
    st.info("👋 ¡Bienvenido! Por favor, sube el catálogo PDF desde el menú lateral para empezar.")
