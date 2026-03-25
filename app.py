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

    # --- FUNCIÓN PDF POTENCIADA AL MÁXIMO ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado Corporativo
        pdf.set_fill_color(0, 71, 171) 
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", 'B', 26)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 25, "OPTIMARKET PRO", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(190, 0, f"Informe Estrategico - {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(25)

        # 1. RESUMEN EJECUTIVO
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(30, 30, 30)
        resumen = (f"Beneficio Neto Total: {total:,.2f} EUR. ROI promedio: {roi_medio:.1f}%.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(10)

        # 2. INSIGHTS
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0
