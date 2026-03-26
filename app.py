import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Multi-Tienda", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Introduce tu clave:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave incorrecta")
else:
    st.title("📊 Panel de Control: Ventas y Tiendas")
    
    archivo = st.sidebar.file_uploader("📂 1. Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # LEER ARCHIVO
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            # Limpiar nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 2. Ajustes")

            # --- DETECCIÓN DE COLUMNAS ---
            # Buscamos la tienda, el producto y las ventas por palabras clave
            c_tienda = next((c for c in df.columns if 'TIENDA' in c), None)
            c_prod_sug = next((c for c in df.columns if any(x in c for x in ['FABRI', 'PROD', 'REF', 'MOD'])), df.columns[0])
            c_vent_sug = next((c for c in df.columns if any(x in c for x in ['CANT', 'VEND', 'UNID'])), df.columns[1])

            # Selectores en el lateral
            col_prod = st.sidebar.selectbox("Columna Producto/Fabricante:", df.columns, index=list(df.columns).index(c_prod_sug))
            col_vent = st.sidebar.selectbox("Columna Cantidad Vendida:", df.columns, index=list(df.columns).index(c_vent_sug))

            # --- LÓGICA DE TIENDAS ---
            filtro_tienda = "TODAS"
            if c_tienda:
                lista_tiendas = ["TODAS"] + sorted(df[c_tienda].dropna().unique().tolist())
                filtro_tienda = st.sidebar.selectbox("📍 Filtrar por Tienda:", lista_tiendas)

            # --- PROCESAMIENTO DE DATOS ---
            df_final = df.copy()
            
            # Aplicar filtro de tienda
            if c_tienda and filtro_tienda != "TODAS":
                df_final = df_final[df_final[c_tienda] == filtro_tienda]
