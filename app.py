import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Panel de Control", layout="wide")

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
            
            # --- SELECTORES (Sin automatismos que den error) ---
            # Simplemente te dejamos elegir entre las columnas que existen
            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            # --- DETECCIÓN DE TIENDA ---
            col_tienda_found = next((c for c in df.columns if 'TIENDA' in c), None)
            tienda_seleccionada = "TODAS"
            
            if col_tienda_found:
                lista_tiendas = ["TODAS"] + sorted(df[col_tienda_found].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("📍 Seleccionar Tienda:", lista_tiendas)

            # --- PROCESAMIENTO ---
            df_temp = df.copy()
            
            # Filtro de tienda
            if col_tienda_found and tienda_seleccionada != "TODAS":
                df_temp = df_temp[df_temp[col_tienda_found] == tienda_seleccionada]

            df_temp['Producto'] = df_temp[col_prod]
            df_temp['Ventas'] = pd.to_numeric(df_temp[col_vent], errors='coerce').fillna(0)

            # Buscar dinero (Importe, Precio, etc.)
            col_dinero = next((c for c in df.columns if any(x in c for x in ['IMP', 'TOTAL', 'PREC'])), None)
            if col_dinero:
                df_temp['Dinero'] = pd.to_numeric(df_temp[col_dinero], errors='coerce').fillna(0)
            else:
                df_temp['Dinero'] = df_temp['Ventas']

            # Agrupar datos
            res = df_temp.groupby('Producto').agg({'Ventas':'sum', 'Dinero':'sum'}).reset_index()
            res = res.sort_values('Dinero', ascending=False).head(20)

            # --- MOSTRAR RESULTADOS ---
            if not res.empty:
                st.subheader(f"📍 Resultados de: {tienda_seleccionada}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📦 VOLUMEN", f"{res['Ventas'].sum():,.0f} uds")
                c2.metric("💰 INGRESOS", f"{res['Dinero'].sum():,.2f} €" if col_dinero else f"{res['Ventas'].sum():,.0f}")
