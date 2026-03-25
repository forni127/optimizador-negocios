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

    # --- FUNCIÓN PDF POTENCIADA ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(0, 71, 171) 
        pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_font("Arial", '', 12)
        resumen = (f"Durante el periodo analizado, el negocio ha generado un beneficio neto total de {total:,.2f} EUR, "
                   f"con un retorno de inversion (ROI) promedio del {roi_medio:.1f}% sobre el inventario movilizado.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, "2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Este activo representa el mayor flujo de caja ({estrella['Rentabilidad_Total']:,.2f} EUR).")
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"> MAXIMA EFICIENCIA: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Con un ROI del {eficiente['ROI_Porcentaje']:.1f}%, es el mejor multiplicador de capital.")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(90, 10, " Item", 1)
        pdf.cell(50, 10, " Beneficio (EUR)", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        pdf.set_font("Arial", '', 10)
        for i, row in df.iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
        return pdf.output(
