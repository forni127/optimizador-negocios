import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE COLUMNAS (Para tu Excel de Zapatería) ---
COL_PRODUCTO = "REFERENC."    
COL_VENTAS   = "VENDIDO"      
COL_STOCK    = "STOCK"        

st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave incorrecta")
else:
    # Estilos Visuales
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        h4 { color: #0047AB; margin-top: 0; }
        </style>
        """, unsafe_allow_html=True)

    st.title("📊 Análisis de Temporada")
    archivo = st.sidebar.file_uploader("Sube el archivo Excel", type=["xlsx"])

    if archivo:
        try:
            # Cargamos el Excel saltando la primera fila que está vacía
            df = pd.read_excel(archivo, skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]

            if COL_PRODUCTO in df.columns and COL_VENTAS in df.columns:
                # Limpiar números
                df[COL_VENTAS] = pd.to_numeric(df[COL_VENTAS], errors='coerce').fillna(0)
                df[COL_STOCK] = pd.to_numeric(df[COL_STOCK], errors='coerce').fillna(0)

                # Resumen por Referencia
                res = df.groupby(COL_PRODUCTO).agg({COL_VENTAS:'sum', COL_STOCK:'sum'}).reset_index()
                res = res.sort_values(COL_VENTAS, ascending=False)

                # KPIs
                c1, c2, c3 = st.columns(3)
                c1.metric("PARES VENDIDOS", f"{res[COL_VENTAS].sum():,.0f}")
                c2.metric("STOCK TOTAL", f"{res[COL_STOCK].sum():,.0f}")
                estrella = res.iloc[0]
                c3.metric("TOP REF", str(estrella[COL_PRODUCTO]))

                # Gráfica
                fig = px.bar(res.head(15), x=COL_PRODUCTO, y=COL_VENTAS, color=COL_VENTAS, 
                             color_continuous_scale='Blues', title="Ventas por Referencia")
                st.plotly_chart(fig, use_container_width=True)

                # --- DIAGNÓSTICO IA ---
                st.divider()
                st.header("🧠 Consultoría IA")
                l, r = st.columns(2)
                with l:
                    st.markdown(f'<div class="report-card"><h4>🥇 Líder: {estrella[COL_PRODUCTO]}</h4><p>Has vendido {estrella[COL_VENTAS]:.0f} unidades. Es tu mejor artículo este mes.</p></div>', unsafe_allow_html=True)
                with r:
                    sobrante = res.sort_values(COL_STOCK, ascending=False).iloc[0]
                    st.markdown(f'<div class="report-card" style="border-left-color: #d9534f;"><h4>⚠️ Exceso: {sobrante[COL_PRODUCTO]}</h4><p>Tienes {sobrante[COL_STOCK]:.0f} unidades en stock. Toca liquidar o promocionar.</p></div>', unsafe_allow_html=True)

            else:
                st.error(f"Columnas no encontradas. Veo: {list(df.columns)}")
        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.info("Sube el Excel en el panel lateral.")
