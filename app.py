import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import io

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="OptiMarket Pro | VIP", page_icon="🚀", layout="wide")

# --- SISTEMA DE SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Sistema de Inteligencia de Negocio")
        st.info("Acceso restringido a consultores autorizados.")
        user_pass = st.text_input("Introduce tu clave:", type="password")
        if st.button("Desbloquear"):
            if user_pass == "SOCIO2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta.")
        return False
    return True

if check_password():
    # 2. ESTILOS CSS PROFESIONALES
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; }
        </style>
        """, unsafe_allow_html=True)

    # 3. FUNCIÓN DE GENERACIÓN DE PDF PROFESIONAL
    def exportar_pdf(df, estrella, eficiente, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 15, "INFORME ESTRATEGICO OPTIMARKET PRO", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(128, 128, 128)
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 10, f"Generado por Consultoria IA el {fecha}", ln=True, align='C')
        pdf.ln(10)
        
        # Resumen Ejecutivo
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, " 1. RESUMEN DE RENDIMIENTO", ln=True, fill=True)
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"- Beneficio Neto Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"- ROI Promedio del Inventario: {roi_medio:.1f}%", ln=True)
        pdf.ln(5)
        
        # Insights IA
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, " 2. CONCLUSIONES DEL CONSULTOR IA", ln=True, fill=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Lider de Ventas: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Este producto genera el mayor flujo de caja ({estrella['Rentabilidad_Total']:,.2f} EUR). Es el pilar de solvencia de la empresa.")
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Activo mas Eficiente: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Con un ROI del {eficiente['ROI_Porcentaje']:.0f}%, es el multiplicador de capital mas potente del catalogo.")
        pdf.ln(10)

        # Tabla Técnica
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(0, 71, 171)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(90, 10, " Producto", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(0, 0, 0)
        for _, row in df.iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'C')
            
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # 4. CUERPO DE LA APP
    st.title("🚀 OptiMarket Pro")
    st.subheader("Business Intelligence & Profit Optimization")

    archivo = st.sidebar.file_uploader("📂 Cargar Excel de Ventas", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        
        # Cálculos Estratégicos
        df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
        df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
        df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
        
        total_neto = df['Rentabilidad_Total'].sum()
        roi_medio = df['ROI_Porcentaje'].mean()
        estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
        eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
        bajo = df.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

        # KPIs Visuales
        c1, c2, c3 = st.columns(3)
        c1.metric("BENEFICIO NETO TOTAL", f"{total_neto:,.2f} €")
        c2.metric("ACTIVO ESTRELLA", estrella['Producto'])
        c3.metric("ROI PROMEDIO", f"{roi_medio:.1f} %")

        # Gráfica
        st.subheader("📈 Mapa de Rentabilidad Estratégica")
        fig = px.bar(df, x='Producto', y='Rentabilidad_Total', color='ROI_Porcentaje', 
                     color_continuous_scale='Geyser', text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

        # 5. DIAGNÓSTICO IA (TEXTOS PREMIUM)
        st.divider()
        st.header("🧠 Diagnóstico de Consultoría IA")
        
        pct_estrella = (estrella['Rentabilidad_Total'] / total_neto) * 100
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.markdown(f"""
            <div class="report-card">
                <h4>🥇 Liderazgo de Mercado: {estrella['Producto']}</h4>
                <p>Este activo es tu <b>principal generador de liquidez</b>. Contribuye con un <b>{pct_estrella:.1f}%</b> al beneficio total.
                <br><br><b>Estrategia:</b> No compitas por precio; compite por servicio. Cualquier rotura de stock aquí es una pérdida crítica de flujo de caja.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown(f"""
            <div class="report-card" style="border-left-color: #28a745;">
                <h4>📈 Optimización de Capital: {eficiente['Producto']}</h4>
                <p>Presenta una eficiencia del <b>{eficiente['ROI_Porcentaje']:.0f}%</b>. Es un multiplicador de dinero: cada euro invertido genera {eficiente['Margen']:.2f}€ de margen limpio.
                <br><br><b>Estrategia:</b> Escalar las ventas de este ítem optimizará el margen global sin aumentar el riesgo financiero.</p>
            </div>
            """, unsafe_allow_html=True)
