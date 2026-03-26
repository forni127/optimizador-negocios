import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# =========================================================
# 🛠️ SECCIÓN DE CONFIGURACIÓN PARA: RESUMEN-TEMPORADA-ART.xlsx
# =========================================================
COL_PRODUCTO = "REFERENC."    # Es la columna que identifica el artículo
COL_PRECIO   = "PRECIO"       # Tu Excel NO tiene esta columna, el código la creará a 0
COL_COSTE    = "COSTE"        # Tu Excel NO tiene esta columna, el código la creará a 0
COL_VENTAS   = "VENDIDO"      # Es la columna con las unidades vendidas
# =========================================================

st.set_page_config(page_title="OptiMarket Pro | Multi-Empresa", page_icon="🚀", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Incorrecta")
else:
    # Estilos de la IA
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        h4 { color: #0047AB; margin-top: 0; }
        </style>
        """, unsafe_allow_html=True)

    st.title("📊 Consultoría de Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("📂 Cargar Excel de cualquier empresa", type=["xlsx"])

    if archivo:
        try:
            # 1. Cargar datos (Saltamos filas vacías si las hay, común en Excels reales)
            # Busca la línea que carga el archivo y déjala así:
df = pd.read_excel(archivo, skiprows=1)
            
            # Limpieza básica: nombres de columnas sin espacios extra
            df.columns = [str(c).strip() for c in df.columns]

            # 2. MAREO DINÁMICO: Mapeamos tus nombres a los que la app usa internamente
            mapeo = {
                COL_PRODUCTO: 'Producto_Interno',
                COL_PRECIO:   'Precio_Interno',
                COL_COSTE:    'Coste_Interno',
                COL_VENTAS:   'Ventas_Interno'
            }
            
            # Si alguna columna de la configuración no existe, avisamos
            faltantes = [c for c in [COL_PRODUCTO, COL_VENTAS] if c not in df.columns]
            
            if not faltantes:
                # Si no hay columnas de precio/coste en este Excel (como en tu último archivo), 
                # las creamos vacías para que no explote
                if COL_PRECIO not in df.columns: df['Precio_Interno'] = 0
                else: df.rename(columns={COL_PRECIO: 'Precio_Interno'}, inplace=True)
                
                if COL_COSTE not in df.columns: df['Coste_Interno'] = 0
                else: df.rename(columns={COL_COSTE: 'Coste_Interno'}, inplace=True)
                
                df.rename(columns={COL_PRODUCTO: 'Producto_Interno', COL_VENTAS: 'Ventas_Interno'}, inplace=True)

                # 3. Limpieza Numérica
                for c in ['Precio_Interno', 'Coste_Interno', 'Ventas_Interno']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

                # 4. Lógica de Negocio
                df['Beneficio'] = (df['Precio_Interno'] - df['Coste_Interno']) * df['Ventas_Interno']
                # Evitar división por cero en ROI
                df['ROI'] = df.apply(lambda x: ((x['Precio_Interno'] - x['Coste_Interno']) / x['Coste_Interno'] * 100) if x['Coste_Interno'] > 0 else 0, axis=1)

                # Agrupamos por lo que hayas configurado como Producto
                resumen = df.groupby('Producto_Interno').agg({
                    'Ventas_Interno': 'sum',
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().sort_values('Beneficio', ascending=False)

                # 5. DASHBOARD ESTRATÉGICO
                total_v = resumen['Ventas_Interno'].sum()
                total_b = resumen['Beneficio'].sum()
                estrella = resumen.iloc[0]

                c1, c2, c3 = st.columns(3)
                c1.metric("UNIDADES VENDIDAS", f"{total_v:,.0f}")
                c2.metric("BENEFICIO ESTIMADO", f"{total_b:,.2f} €")
                c3.metric("TOP VENTAS", str(estrella['Producto_Interno']))

                # Gráfica
                st.subheader("Análisis de Rendimiento por Producto/Referencia")
                fig = px.bar(resumen.head(20), x='Producto_Interno', y='Ventas_Interno', 
                             color='Ventas_Interno', color_continuous_scale='Blues',
                             labels={'Producto_Interno': 'Referencia', 'Ventas_Interno': 'Unidades'})
                st.plotly_chart(fig, use_container_width=True)

                # --- DIAGNÓSTICO IA ---
                st.divider()
                st.header("🧠 Diagnóstico de Consultoría IA")
                col_l, col_r = st.columns(2)
                
                with col_l:
                    st.markdown(f"""<div class="report-card"><h4>🥇 Líder de Rotación: {estrella['Producto_Interno']}</h4><p>Este producto ha movido <b>{estrella['Ventas_Interno']:.0f} unidades</b>. Es el corazón de la operación actual.</p></div>""", unsafe_allow_html=True)
                
                with col_r:
                    # Buscamos el que más stock podría tener o el que menos rota (si tuvieras columna stock)
                    st.markdown(f"""<div class="report-card" style="border-left-color: #28a745;"><h4>💡 Insight de Volumen</h4><p>El volumen total de ventas indica una salud comercial estable. El Top 5 de productos representa el grueso de tu flujo de trabajo.</p></div>""", unsafe_allow_html=True)

            else:
                st.error(f"⚠️ Error de configuración. No encuentro estas columnas en el Excel: {faltantes}")
                st.write("Columnas detectadas en el archivo subido:", list(df.columns))

        except Exception as e:
            st.error(f"Ocurrió un error al procesar este archivo: {e}")
    else:
        st.info("👋 Sube el Excel. Recuerda que si los nombres de las columnas cambian, solo tienes que editarlos en la parte superior del código.")
