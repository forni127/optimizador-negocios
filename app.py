import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
    h4 { color: #0047AB; margin-top: 0; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE GENERACIÓN DE PDF PROFESIONAL
def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 71, 171) 
    pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, " 1. RESUMEN EJECUTIVO", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, f"Beneficio Neto Total: {total:,.2f} EUR | ROI promedio: {roi_medio:.1f}%")
    pdf.ln(5)
    
    # Tabla simple para evitar errores de caracteres
    for i, row in df.iterrows():
        pdf.cell(80, 10, f"{str(row['Producto'])[:30]}", 1)
        pdf.cell(50, 10, f"{row['Rentabilidad_Total']:,.2f}", 1)
        pdf.cell(40, 10, f"{row['ROI_Porcentaje']:.1f}%", 1, 1)
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

    # 2. GRÁFICA
    st.subheader("📈 Mapa de Rentabilidad Estratégica")
    fig =
