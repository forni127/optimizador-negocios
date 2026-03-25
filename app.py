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

    # --- FUNCIÓN PDF DE ALTA CONSULTORÍA CON LOGO ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # 1. ENCABEZADO CON LOGO CORPORATIVO
        pdf.set_fill_color(0, 71, 171)  
        pdf.rect(0, 0, 210, 45, 'F')
        
        # Logo minimalista
        pdf.set_fill_color(255, 255, 255)
        pdf.polygon([(15, 35), (25, 10), (35, 35)], 'F')
        
        pdf.set_xy(40, 15)
        pdf.set_font("Arial", 'B', 28)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(100, 10, "OPTIMARKET PRO", 0, 0, 'L')
        
        pdf.set_xy(40, 28)
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(100, 5, "Business Intelligence & Profit Optimization", 0, 0, 'L')
        
        pdf.set_xy(150, 20)
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 10, f"FECHA: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 0, 'R')
        pdf.ln(35)

        # 2. RESUMEN EJECUTIVO
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "1. RESUMEN DE RENDIMIENTO", ln=True)
        pdf.set_draw_color(0, 71, 171)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(40, 40, 40)
        resumen = (f"El beneficio neto total asciende a {total:,.2f
