import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# 1. CONFIGURACIÓN Y MARCA
st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

# Función para generar el PDF
def generar_pdf(df, estrella, eficiente, beneficio_total):
    pdf = FPDF()
    pdf.add_page()
    
    # Título del Informe
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 10, "Informe de Optimizacion OptiMarket Pro", ln=True, align='C')
    pdf.ln(10)
    
    # Resumen Ejecutivo
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Resumen Ejecutivo", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Beneficio Neto Total del Periodo: {beneficio_total:,.2f} EUR")
    pdf.ln(5)
    
    # Análisis de IA
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Analisis de la IA", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"- Producto Estrella: {estrella['Producto']} (Aporta {estrella['Rentabilidad_Total']:.2f} EUR)")
    pdf.multi_cell(0, 10, f"- Mayor Eficiencia (ROI): {eficiente['Producto']} ({eficiente['ROI_Porcentaje']:.0f}% de retorno)")
    pdf.ln(10)
    
    # Tabla de Datos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Producto", 1)
    pdf.cell(50, 10, "Rentabilidad", 1)
    pdf.cell(40, 10, "ROI %", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    for index, row in df.iterrows():
        pdf.cell(80, 10, str(row['Producto']), 1)
        pdf.cell(50, 10, f"{row['Rentabilidad_Total']:.2f}", 1)
        pdf.cell(40, 10, f"{row['ROI_Porcentaje']:.1f}%", 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🚀 OptiMarket Pro")
st.subheader("Análisis Inteligente y Generación de Informes Ejecutivos")

archivo = st.sidebar.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    
    # Cálculos
    df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
    df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
    beneficio_total = df['Rentabilidad_Total'].sum()
    
    # Análisis IA
    estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
    eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
    
    # Métricas y Gráfica (Igual que antes)
    st.metric("Beneficio Total Mes", f"{beneficio_total:,.2f} €")
    fig = px.bar(df, x='Producto', y='Rentabilidad_Total', color='ROI_Porcentaje', title="Rendimiento del Inventario")
    st.plotly_chart(fig, use_container_width=True)
    
    # BOTONES DE DESCARGA
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Exportar Resultados")
    
    # Botón Excel
    st.sidebar.download_button(label="Descargar Excel", data=df.to_csv(index=False), file_name='datos.csv')
    
    # Botón PDF
    pdf_bytes = generar_pdf(df, estrella, eficiente, beneficio_total)
    st.sidebar.download_button(
        label="📄 Descargar Informe PDF",
        data=pdf_bytes,
        file_name="Informe_OptiMarket.pdf",
        mime="application/pdf"
    )

    st.success("✅ Informe PDF generado. Puedes descargarlo en la barra lateral.")
