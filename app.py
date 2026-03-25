import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

# --- SISTEMA DE CONTRASEÑA (NUEVO) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado OptiMarket")
        user_pass = st.text_input("Introduce la clave de consultor para acceder:", type="password")
        if st.button("Desbloquear Sistema"):
            if user_pass == "SOCIO2026": # <--- CAMBIA TU CLAVE AQUÍ
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta. Contacta con el administrador.")
        return False
    return True

# Solo si la contraseña es correcta se ejecuta el resto
if check_password():

    # 2. ESTILOS VISUALES (Tus estilos originales)
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # FUNCIÓN DE GENERACIÓN DE PDF (Tu función original sin cambios)
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(0, 71, 171) 
        pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        fecha = datetime.datetime.now().strftime("%d/%m/%Y")
        pdf.cell(200, 10, f"Informe Estrategico de Rendimiento - Generado el {fecha}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, " 1. RESUMEN EJECUTIVO", ln=True, fill=True)
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"Beneficio Neto Total: {total:,.2f} EUR | ROI promedio: {roi_medio:.1f}%")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(80, 10, " Item", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 9)
        for i, row in df.iterrows():
            pdf.cell(80, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'C')
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # --- INTERFAZ WEB ---
    st.title("🚀 OptiMarket Pro")
    st.subheader("Business Intelligence & Profit Optimization")

    archivo = st.sidebar.file_uploader("📂 Cargar Datos de Ventas (Excel)", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        
        # Cálculos de Negocio
        df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
        df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
        df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
        
        total_neto = df['Rentabilidad_Total'].sum()
        roi_medio = df['ROI_Porcentaje'].mean()
        estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
        eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
        bajo = df.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

        # 1. KPIs Visuales
        c1, c2, c3 = st.columns(3)
        c1.metric("BENEFICIO NETO TOTAL", f"{total_neto:,.2f} €")
        c2.metric("ACTIVO ESTRELLA", estrella['Producto'])
        c3.metric("ROI PROMEDIO", f"{roi_medio:.1f} %")

        # 2. GRÁFICA AVANZADA
        st.subheader("📈 Mapa de Rentabilidad Estratégica")
        fig = px.bar(df, x='Producto', y='Rentabilidad_Total', color='ROI_Porcentaje', 
                     color_continuous_scale='Geyser', text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

        # 3. CONSULTORÍA DE IA
        st.divider()
        st.header("🧠 Diagnóstico de Consultoría IA")
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f"""<div class="report-card"><h4>🥇 Liderazgo: {estrella['Producto']}</h4><p>Aporta el <b>{(estrella['Rentabilidad_Total']/total_neto)*100:.1f}%</b> del beneficio total.</p></div>""", unsafe_allow_html=True)
        with col_right:
            st.markdown(f"""<div class="report-card" style="border-left-color: #28a745;"><h4>📈 Eficiencia: {eficiente['Producto']}</h4><p>Retorno del <b>{eficiente['ROI_Porcentaje']:.0f}%</b> por euro invertido.</p></div>""", unsafe_allow_html=True)

        # 4. EXPORTACIÓN
        st.sidebar.divider()
        st.sidebar.subheader("📥 Generar Reporte Oficial")
        with st.spinner('Redactando PDF...'):
            pdf_bytes = generar_pdf_pro(df, estrella, eficiente, bajo, total_neto, roi_medio)
        st.sidebar.download_button("📄 Descargar Informe PDF", data=pdf_bytes, file_name="Informe.pdf", mime="application/pdf")
        st.sidebar.download_button("📊 Exportar CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="datos.csv")
    else:
        st.info("👋 Por favor, cargue su archivo Excel en el panel lateral.")
