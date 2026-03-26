import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Business Intelligence", layout="wide")

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
    st.title("📊 Análisis Estratégico de Ventas")
    
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
            st.sidebar.subheader("⚙️ 2. Ajuste de Columnas")
            
            # Selectores manuales
            col_prod = st.sidebar.selectbox("Columna de Producto/Fabricante:", df.columns)
            col_vent = st.sidebar.selectbox("Columna de Cantidad Vendida:", df.columns)

            if col_prod and col_vent:
                df_final = df.copy()
                df_final['Producto'] = df_final[col_prod]
                df_final['Ventas'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

                # Buscar columna de dinero (Importe, Precio o Total)
                col_dinero = next((c for c in df.columns if any(x in c for x in ['IMP', 'TOTAL', 'PREC'])), None)
                
                if col_dinero:
                    df_final['Dinero'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
                else:
                    df_final['Dinero'] = df_final['Ventas']

                # Agrupar datos
                res = df_final.groupby('Producto').agg({'Ventas':'sum', 'Dinero':'sum'}).reset_index()
                res = res.sort_values('Dinero', ascending=False).head(20)

                # --- DASH
