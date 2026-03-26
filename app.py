import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="OptiMarket Pro | Multi-Cliente", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Clientes")
    clave = st.text_input("Contraseña de Acceso:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave incorrecta")
else:
    st.title("📊 Inteligencia de Negocio Multi-Cliente")
    archivo = st.sidebar.file_uploader("📂 Sube cualquier Excel de ventas", type=["xlsx"])

    if archivo:
        try:
            # 1. LEER EXCEL (Detectar si hay basura arriba)
            raw_df = pd.read_excel(archivo)
            
            # Si hay muchos nombres raros (Unnamed), saltamos una fila como en tu excel de zapatos
            if raw_df.columns.str.contains('Unnamed').sum() > (len(raw_df.columns) / 2):
                df = pd.read_excel(archivo, skiprows=1)
            else:
                df = raw_df

            # 2. LIMPIEZA TOTAL DE COLUMNAS (MAYÚSCULAS Y SIN ESPACIOS)
            df.columns = [str(c).strip().upper() for c in df.columns]

            # 3. BUSCADOR INTELIGENTE (Da igual mayúsculas o minúsculas)
            mapeo = {}
            for col in df.columns:
                # Buscamos coincidencias sin importar cómo esté escrito
                if any(x in col for x in ['REF', 'PROD', 'MOD', 'ART', 'FABRI']): mapeo[col] = 'Producto'
                elif any(x in col for x in ['VEND', 'CANT', 'UNID']): mapeo[col] = 'Ventas'
                elif any(x in col for x in ['COST']): mapeo[col] = 'Coste'
                elif any(x in col for x in ['PREC', 'IMP', 'PVP', 'VALOR']): mapeo[col] = 'Precio'
                elif any(x in col for x in ['STOCK']): mapeo[col] = 'Stock'

            df = df.rename(columns=mapeo)

            # 4. COMPROBACIÓN Y CÁLCULOS
            if 'Producto' in df.columns and 'Ventas' in df.columns:
                for c in ['Ventas', 'Coste', 'Precio', 'Stock']:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                # Agrupar por producto/referencia
                res = df.groupby('Producto').agg({'Ventas': 'sum'}).reset_index()
                res = res.sort_values('Ventas', ascending=False)

                # Dashboard Simple
                c1, c2 = st.columns(2)
                c1.metric("VOLUMEN TOTAL", f"{res['Ventas'].sum():,.0f} uds")
                c2.metric("TOP PRODUCTO", str(res.iloc[0]['Producto']))

                # Gráfica
                fig = px.bar(res.head(15), x='Producto', y='Ventas', 
                             color='Ventas', color_continuous_scale='Turbo',
                             title="Distribución de Ventas")
                st.plotly_chart(fig, use_container_width=True)

                # Diagnóstico IA
                st.divider()
                st.success(f"✅ **Análisis Final:** Se han detectado las columnas correctamente. El artículo **{res.iloc[0]['Producto']}** lidera el volumen de ventas.")
            else:
                st.error("❌ No he podido identificar las columnas.")
                st.write("Columnas encontradas en el Excel:", list(df.columns))

        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.info("👋 Sube un archivo para empezar. No importa el formato de los títulos, yo los entiendo.")
