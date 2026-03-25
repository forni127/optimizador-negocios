import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Introduce la contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
else:
    # --- TU DISEÑO Y ESTILOS ---
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # --- FUNCIÓN PDF ULTRA PROFESIONAL ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado de Marca
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(0, 71, 171) 
        pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        fecha = datetime.datetime.now().strftime("%d/%m/%Y")
        pdf.cell(200, 10, f"Informe Estrategico de Rendimiento - Generado el {fecha}", ln=True, align='C')
        pdf.ln(10)
        
        # 1. RESUMEN EJECUTIVO
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, " 1. RESUMEN EJECUTIVO", ln=True, fill=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", '', 12)
        resumen = (f"Tras el analisis de los datos facilitados, el volumen de negocio ha generado un "
                   f"beneficio neto total de {total:,.2f} EUR. La eficiencia global de la cartera "
                   f"presenta un ROI promedio del {roi_medio:.1f}%.")
        pdf.multi_cell(0, 7, resumen)
        pdf.ln(10)
        
        # 2. ANÁLISIS ESTRATÉGICO
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, " 2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 8, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Este producto es el motor financiero, aportando {estrella['Rentabilidad_Total']:,.2f} EUR.")
        pdf.ln(4)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(40, 167, 69) 
        pdf.cell(0, 8, f"> MAXIMA EFICIENCIA: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Con un ROI del {eficiente['ROI_Porcentaje']:.1f}%, es el item mas rentable.")
        pdf.ln(10)

        # 3. TABLA TÉCNICA
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(0, 71, 171)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(90, 10, " Producto", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(0, 0, 0)
        for _, row in df.iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'C
