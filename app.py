import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA Y MARCA
st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

# Estilos CSS para las tarjetas de la IA
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# Función para generar el PDF (Corregida para evitar errores de caracteres)
def generar_pdf(df, estrella, eficiente, beneficio_total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Informe Estrategico OptiMarket Pro", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Beneficio Neto Total: {beneficio_total:,.2f} EUR", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, f"Analisis: El producto estrella es {estrella['Producto']} con un beneficio de {estrella['Rentabilidad_Total']:.2f} EUR. El mas eficiente es {eficiente['Producto']} con un ROI del {eficiente['ROI_Porcentaje']:.1f}%.")
    pdf.ln(10)
    
    # Tabla simple en PDF
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 10, "Producto", 1)
    pdf.cell(50, 10, "Beneficio (EUR)", 1)
    pdf.cell(40, 10, "ROI %", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    for i, row in df.iterrows():
        pdf.cell(80, 10, str(row['Producto'])[:30], 1)
        pdf.cell(50, 10, f"{row['Rentabilidad_Total']:.2f}", 1)
        pdf.cell(40, 10, f"{row['ROI_Porcentaje']:.1f}%", 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- CUERPO DE LA APP ---
st.title("🚀 OptiMarket Pro")
st.subheader("Consultoria Estrategica de Negocios mediante Datos")
st.divider()

archivo = st.sidebar.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    
    # Cálculos
    df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
    df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
    beneficio_total = df['Rentabilidad_Total'].sum()
    
    # Métricas principales
    c1, c2, c3 = st.columns(3)
    estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
