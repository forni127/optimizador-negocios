import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

# --- SISTEMA DE CONTRASEÑA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado OptiMarket")
        user_pass = st.text_input("Introduce la clave de consultor:", type="password")
        if st.button("Desbloquear Sistema"):
            if user_pass == "SOCIO2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta.")
        return False
    return True

if check_password():
    # 2. ESTILOS
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; }
        </style>
        """, unsafe_allow_html=True)

    # 3. INTERFAZ
    st.title("🚀 OptiMarket Pro")
    st.subheader("Business Intelligence & Profit Optimization")

    archivo = st.sidebar.file_uploader("📂 Cargar Excel de Ventas", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        
        # Cálculos rápidos
        df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
        df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
        df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
        
        total_neto = df['Rentabilidad_Total'].sum()
        roi_medio = df['ROI_Porcentaje'].mean()
        estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
        eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
        bajo = df.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("BENEFICIO NETO TOTAL", f"{total_neto:,.2f} €")
        c2.metric("ACTIVO ESTRELLA", estrella['Producto'])
        c3.metric("ROI PROMEDIO", f"{roi_medio:.1f} %")

        # Gráfica
        st.subheader("📈 Mapa de Rentabilidad Estratégica")
        fig = px.bar(df, x='Producto', y='Rentabilidad_Total', color='ROI_Porcentaje', 
                     color_continuous_scale='Geyser', text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

        # 4. DIAGNÓSTICO IA (TEXTOS RECUPERADOS)
        st.divider()
        st.header("🧠 Diagnóstico de Consultoría IA")
        
        # Calculamos el % de aportación de la estrella
        pct_estrella = (estrella['Rentabilidad_Total'] / total_neto) * 100

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"""
            <div class="report-card">
                <h4>🥇 Liderazgo de Mercado: {estrella['Producto']}</h4>
                <p>Este activo es tu <b>principal generador de liquidez</b>. Contribuye con un <b>{pct_estrella:.1f}%</b> al beneficio total de la empresa.
                <br><br><b>Estrategia:</b> No compitas por precio; compite por servicio. Cualquier rotura de stock aquí es una pérdida crítica de flujo de caja.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown(f"""
            <div class="report-card" style="border-left-color: #28a745;">
                <h4>📈 Optimización de Capital: {eficiente['Producto']}</h4>
                <p>Presenta una eficiencia del <b>{eficiente['ROI_Porcentaje']:.0f}%</b>. Es un multiplicador de dinero: cada euro invertido genera {eficiente['Margen']:.2f}€ de margen limpio.
                <br><br><b>Estrategia:</b> Escalar las ventas de este ítem optimizará el margen global sin aumentar el riesgo financiero.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="report-card" style="border-left-color: #d9534f;">
            <h4>⚠️ Alerta de Rendimiento: {bajo['Producto']}</h4>
            <p>Este ítem está <b>"secuestrando" capital</b> con el ROI más bajo (<b>{bajo['ROI_Porcentaje']:.1f}%</b>). 
            <br><br><b>Estrategia:</b> Evalúa una subida de precio o un paquete de liquidación (Bundling) para liberar efectivo e invertirlo en inventario de alta rotación.</p>
        </div>
        """, unsafe_allow_html=True)

        # 5. PDF (Versión segura)
        st.sidebar.divider()
        st.sidebar.info("Usa el menú superior del navegador para imprimir a PDF o descarga el CSV abajo.")
        st.sidebar.download_button("📊 Exportar Datos CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="analisis.csv")
    else:
        st.info("👋 Por favor, cargue su archivo Excel en el panel lateral.")
