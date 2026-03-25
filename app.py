import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

# Estilos visuales para la Web
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
    h4 { color: #0047AB; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE GENERACIÓN DE INFORME PDF PROFESIONAL
def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
    pdf = FPDF()
    pdf.add_page()
   
    # Encabezado
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 71, 171) # Azul Corporativo
    pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    pdf.cell(200, 10, f"Informe Estrategico de Rendimiento - Generado el {fecha}", ln=True, align='C')
    pdf.ln(10)

    # Bloque 1: Resumen Ejecutivo
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, " 1. RESUMEN EJECUTIVO", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Durante el periodo analizado, el negocio ha generado un beneficio neto total de {total:,.2f} EUR, con un retorno de inversion (ROI) promedio del {roi_medio:.1f}% sobre el inventario movilizado.")
    pdf.ln(5)

    # Bloque 2: Hallazgos Clave de la IA
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, " 2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True, fill=True)
    pdf.ln(5)
   
    # Producto Estrella
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Este activo representa el mayor flujo de caja. Con un beneficio neto de {estrella['Rentabilidad_Total']:.2f} EUR, es el pilar de la solvencia operativa. Se recomienda priorizar su disponibilidad absoluta.")
    pdf.ln(3)

    # ROI
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"> MAXIMA EFICIENCIA DE CAPITAL: {eficiente['Producto']}", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Con un ROI del {eficiente['ROI_Porcentaje']:.0f}%, este producto es el mas rentable por cada euro invertido. Escalar las ventas de este item optimizara el margen global sin aumentar proporcionalmente el riesgo financiero.")
    pdf.ln(10)

    # Bloque 3: Tabla Detallada
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 12, " 3. DESGLOSE TECNICO POR PRODUCTO", ln=True, fill=True)
    pdf.ln(5)
   
    # Cabecera Tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(0, 71, 171)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 10, " Item", 1, 0, 'L', True)
    pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
    pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
   
    # Filas Tabla
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
                 title="Volumen de Beneficio vs. Eficiencia de Retorno",
                 labels={'Rentabilidad_Total':'Beneficio Neto (€)', 'ROI_Porcentaje':'Eficiencia ROI (%)'},
                 color_continuous_scale='Geyser', text_auto='.2s')
    st.plotly_chart(fig, use_container_width=True)

    # 3. CONSULTORÍA DE IA (TEXTOS TRABAJADOS)
    st.divider()
    st.header("🧠 Diagnóstico de Consultoría IA")
   
    col_left, col_right = st.columns(2)
   
    with col_left:
        st.markdown(f"""
        <div class="report-card">
            <h4>🥇 Liderazgo de Mercado: {estrella['Producto']}</h4>
            <p>Este producto no es solo el más vendido; es tu <b>principal generador de liquidez</b>. Contribuye con un <b>{(estrella['Rentabilidad_Total']/total_neto)*100:.1f}%</b> al beneficio total de la empresa.
            <br><br><b>Estrategia:</b> No compitas por precio aquí; compite por servicio. Cualquier rotura de stock en este ítem es una pérdida crítica de flujo de caja.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class="report-card" style="border-left-color: #28a745;">
            <h4>📈 Optimización de Capital: {eficiente['Producto']}</h4>
            <p>Presenta una eficiencia del <b>{eficiente['ROI_Porcentaje']:.0f}%</b>. Es un "multiplicador de dinero". Por cada euro que pones en este stock, el negocio genera {eficiente['Margen']:.2f}€ de margen limpio.
            <br><br><b>Estrategia:</b> Considera aumentar el presupuesto de marketing para este ítem. Es donde tu inversión tiene el menor riesgo y el mayor retorno relativo.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-card" style="border-left-color: #d9534f;">
        <h4>⚠️ Alerta de Rendimiento: {bajo['Producto']}</h4>
        <p>Este ítem tiene el ROI más bajo del catálogo (<b>{bajo['ROI_Porcentaje']:.1f}%</b>). Está "secuestrando" capital que podría estar rindiendo más en otros productos.
        <br><br><b>Estrategia:</b> Evalúa una subida de precio inmediata o un paquete de liquidación (Bundling) para liberar ese efectivo e invertirlo en el inventario de alta rotación.</p>
    </div>
    """, unsafe_allow_html=True)

    # 4. EXPORTACIÓN
    st.sidebar.divider()
    st.sidebar.subheader("📥 Generar Reporte Oficial")
   
    # Generar PDF
    with st.spinner('Redactando informe PDF...'):
        pdf_bytes = generar_pdf_pro(df, estrella, eficiente, bajo, total_neto, roi_medio)
       
    st.sidebar.download_button(
        label="📄 Descargar Informe Ejecutivo (PDF)",
        data=pdf_bytes,
        file_name=f"Informe_Estrategico_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
   
    st.sidebar.download_button(
        label="📊 Exportar Tabla de Datos (Excel/CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="datos_optmarket.csv",
        mime="text/csv"
    )

else:
    st.info("👋 Bienvenida/o a OptiMarket Pro. Por favor, cargue su archivo de ventas en el panel lateral para iniciar el diagnóstico de inteligencia de negocio.")
