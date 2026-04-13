import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import urllib.parse
import os

# 1. CONFIGURACIÓN VISUAL PRO
st.set_page_config(page_title="Service Finder Pro", page_icon="📲", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #f0f2f6; }
    .stTextInput>div>div>input { border-radius: 15px; }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #25D366;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. NOMBRE DEL ARCHIVO QUE SUBISTE A GITHUB
NOMBRE_PDF = "base_datos.pdf" 

def buscar_flexible(pdf_path, query):
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    resultados = []
    query = query.lower().strip()

    for num_pagina in range(len(doc)):
        pagina = doc[num_pagina]
        texto_pagina = pagina.get_text().lower()
        
        # Búsqueda flexible: verifica si la palabra está contenida
        if query in texto_pagina:
            instancias = pagina.search_for(query)
            for inst in instancias:
                pagina.add_highlight_annot(inst)
            
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2)) # Alta calidad
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            resultados.append({"pagina": num_pagina + 1, "imagen": img})
            
    return resultados

# 3. INTERFAZ MÓVIL
st.title("📲 Buscador de Servicios")
st.write("Escribe el nombre del servicio para localizar al profesional.")

if os.path.exists(NOMBRE_PDF):
    query = st.text_input("", placeholder="🔍 Ej: Limpieza, Abogado, Mudanzas...")

    if query:
        with st.spinner('Consultando catálogo...'):
            res = buscar_flexible(NOMBRE_PDF, query)
            
            if res:
                st.caption(f"Se han encontrado {len(res)} coincidencia(s).")
                for i, item in enumerate(res):
                    with st.expander(f"📍 Ver resultado - Página {item['pagina']}", expanded=True):
                        st.image(item['imagen'], use_container_width=True)
                        
                        # Espacio para el teléfono
                        tel = st.text_input(f"Introduce el WhatsApp del profesional (Pág. {item['pagina']})", 
                                          placeholder="Ej: 34612345678", 
                                          key=f"w_{i}")
                        
                        if tel:
                            msg = urllib.parse.quote(f"Hola, te he encontrado en el buscador de servicios. Me interesa información sobre {query}.")
                            link = f"https://wa.me/{tel}?text={msg}"
                            st.markdown(f'<a href="{link}" target="_blank"><button>HABLAR POR WHATSAPP 💬</button></a>', unsafe_allow_html=True)
            else:
                st.error("❌ No se encontraron resultados. Intenta con otra palabra.")
else:
    st.warning("⚠️ El archivo 'base_datos.pdf' no se encuentra. Súbelo a GitHub para activar el buscador.")

st.info("💡 Consejo: Si instalas esta web en tu pantalla de inicio, funcionará como una App nativa.")

      
  
 
