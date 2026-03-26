import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# =========================================================
# 🛠️ CAPA DE PERSONALIZACIÓN (Añade aquí palabras nuevas si fallan)
# =========================================================
# El código buscará estas palabras en los títulos de tu Excel
SINONIMOS_PRODUCTO = ['FABRICANTE', 'PRODUCTO', 'REFERENC.', 'MODELO', 'ARTICULO']
SINONIMOS_VENTAS   = ['CANTIDAD', 'VENDIDO', 'UNIDADES', 'VENTAS', 'CANT']
SINONIMOS_COSTE    = ['COSTE', 'COSTO', 'COMPRA', 'PRECIO_COMPRA']
SINONIMOS_PRECIO   = ['PRECIO', 'IMPORTE', 'VENTA', 'PVP', 'VALOR']
# =========================================================

st.set_page_config(page_title="OptiMarket Pro | Business Intelligence", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Inteligencia de Negocio")
    clave = st.text_input("Contraseña Maestro:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Acceso Denegado")
else:
    # Estilos Profesionales
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); color: #1e1e1e; }
        .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 10px; }
        h4 { color: #0047AB; margin: 0; }
        </style>
        """, unsafe_allow_html=True)

    st.title("📊 OptiMarket Pro: Consultoría de Ventas")
    archivo = st.sidebar.file_uploader("📂 Sube tu archivo (Excel/CSV)", type=["xlsx", "csv"])

    if archivo:
        try:
            # 1. CARGA INTELIGENTE
            # Probamos lectura normal. Si falla, es que tiene filas vacías arriba.
            df_test = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
            
            # Si hay muchos nombres raros o vacíos, saltamos la primera fila
            if df_test.columns.str.contains('Unnamed').sum() > (len(df_test.columns) / 2):
                df = pd.read_excel(archivo, skiprows=1)
            else:
                df = df_test

            # 2. UNIFICACIÓN DE NOMBRES (Mayúsculas y Limpios)
            df.columns = [str(c).strip().upper() for c in df.columns]

            # 3. BUSCADOR SEMÁNTICO (Mapeo automático)
            mapeo = {}
            for col in df.columns:
                if any(x in col for x in SINONIMOS_PRODUCTO): mapeo[col] = 'Producto_Final'
                elif any(x in col for x in SINONIMOS_VENTAS): mapeo[col] = 'Ventas_Final'
                elif any(x in col for x in SINONIMOS_COSTE): mapeo[col] = 'Coste_Final'
                elif any(x in col for x in SINONIMOS_PRECIO): mapeo[col] = 'Precio_Final'

            df = df.rename(columns=mapeo)

            # 4. PROCESAMIENTO DE DATOS
            cols_vitales = ['Producto_Final', 'Ventas_Final']
            if all(c in df.columns for c in cols_vitales):
                
                # Convertir a números y limpiar basura
                for c in ['Ventas_Final', 'Coste_Final', 'Precio_Final']:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                # Cálculos de Rentabilidad (Si el Excel tiene dinero)
                if 'Precio_Final' in df.columns and 'Coste_Final' in df.columns:
                    # Usamos Precio_Final si es el unitario, o Importe si es el total. 
                    # Aquí calculamos margen unitario si podemos
                    df['Margen_Unitario'] = df['Precio_Final'] - df['Coste_Final']
                    df['Beneficio_Total'] = df['Margen_Unitario'] * df['Ventas_Final']
                    df['ROI'] = df.apply(lambda x: (x['Margen_Unitario']/x['Coste_Final']*100) if x['Coste_Final'] > 0 else 0, axis=1)
                else:
                    df['Beneficio_Total'] = df['Ventas_Final'] # Fallback a unidades
                    df['ROI'] = 0

                # AGRUPAR POR FABRICANTE/PRODUCTO
                res = df.groupby('Producto_Final').agg({
                    'Ventas_Final': 'sum',
                    'Beneficio_Total': 'sum',
                    'ROI': 'mean'
                }).reset_index().sort_values('Beneficio_Total', ascending=False)

                # --- DASHBOARD DE CONTROL ---
                st.subheader("📍 Indicadores Clave de Desempeño (KPIs)")
                k1, k2, k3, k4 = st.columns(4)
                
                total_v = res['Ventas_Final'].sum()
                total_b = res['Beneficio_Total'].sum()
                top_p = res.iloc[0]
                roi_m = res['ROI'].mean()

                k1.metric("VENTAS TOTALES", f"{total_v:,.0f} uds")
                k2.metric("BENEFICIO NETO", f"{total_b:,.2f} €")
                k3.metric("LÍDER", str(top_p['Producto_Final'])[:15])
                k4.metric("ROI MEDIO", f"{roi_m:.1f} %")

                # --- GRÁFICA PROFESIONAL ---
                st.divider()
                st.subheader("📊 Análisis Comparativo de Fabricantes")
                # Gráfica de burbujas o barras
                fig = px.bar(res.head(15), x='Producto_Final', y='Beneficio_Total',
                             color='ROI', color_continuous_scale='RdYlGn',
                             hover_data=['Ventas_Final'],
                             labels={'Producto_Final': 'Fabricante', 'Beneficio_Total': 'Ganancia (€)'})
                st.plotly_chart(fig, use_container_width=True)

                # --- DIAGNÓSTICO ESTRATÉGICO IA ---
                st.header("🧠 Consultoría Estratégica IA")
                l, r = st.columns(2)
                
                with l:
                    st.markdown(f"""<div class="report-card"><h4>💎 Activo VIP: {top_p['Producto_Final']}</h4>
                    <p>Este fabricante genera <b>{top_p['Beneficio_Total']:,.2f}€</b>. Es el pilar de tu rentabilidad actual.</p>
                    </div>""", unsafe_allow_html=True)
                
                with r:
                    eficiente = res.sort_values('ROI', ascending=False).iloc[0]
                    st.markdown(f"""<div class="report-card" style="border-left-color: #28a745;"><h4>🚀 Máxima Eficiencia: {eficiente['Producto_Final']}</h4>
                    <p>Multiplica tu inversión con un ROI del <b>{eficiente['ROI']:.1f}%</b>. Ideal para reinversión.</p>
                    </div>""", unsafe_allow_html=True)

                # --- EXPORTACIÓN ---
                st.sidebar.divider()
                st.sidebar.write("### ⬇️ Exportar Análisis")
                csv = res.to_csv(index=False).encode('utf-8')
                st.sidebar.download_button("📊 Descargar Datos CSV", data=csv, file_name="analisis_pro.csv")
                
            else:
                st.error("❌ No detecto columnas de 'Producto' o 'Ventas'.")
                st.write("Columnas leídas:", list(df.columns))

        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.info("👋 Bienvenido, Socio. Sube el Excel de Ventas-Fabricantes para empezar el análisis.")
