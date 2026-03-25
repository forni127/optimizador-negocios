import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title(" Acceso Privado")
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

    # --- FUNCIÓN PDF POTENCIADA (DISEÑO PREMIUM) ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # 1. ENCABEZADO DE ALTA CONSULTORÍA
        pdf.set_fill_color(0, 71, 171) # Azul Corporativo
        pdf.rect(0, 0, 210, 45, 'F')
        
        pdf.set_xy(15, 15)
        pdf.set_font("Arial", 'B', 28)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "OPTIMARKET PRO", 0, 1, 'L')
        
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, "BUSINESS INTELLIGENCE & PROFIT REPORT", 0, 1, 'L')
        
        pdf.set_xy(145, 18)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 5, f"FECHA: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
        pdf.set_x(145)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 5, "REF: OM-2026-CONFIDENTIAL", 0, 0, 'R')

        # 2. RESUMEN EJECUTIVO
        pdf.set_xy(15, 55)
        pdf.set_text_color(0, 71, 171)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "1. RESUMEN DE RENDIMIENTO", ln=True)
        pdf.set_draw_color(0, 71, 171)
        pdf.set_line_width(0.8)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(50, 50, 50)
        resumen = (f"El analisis actual revela un Beneficio Neto Acumulado de {total:,.2f} EUR. "
                   f"La cartera de productos presenta un ROI promedio del {roi_medio:.1f}%, "
                   f"indicando una rotacion de capital saludable con margenes optimizables.")
        pdf.multi_cell(0, 7, resumen)

        # 3. CARDS DE INSIGHTS (Visuales)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "2. INSIGHTS ESTRATEGICOS CLAVE", ln=True)
        pdf.ln(2)

        # Card Líder (Azul)
        pdf.set_fill_color(240, 246, 255)
        pdf.rect(15, pdf.get_y(), 180, 20, 'F')
        pdf.set_x(20)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"LIDER DE MERCADO: {estrella['Producto'].upper()}", ln=True)
        pdf.set_x(20)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, f"Principal motor de flujo de caja con {estrella['Rentabilidad_Total']:,.2f} EUR generados.", ln=True)
        pdf.ln(8)

        # Card Eficiencia (Verde)
        pdf.set_fill_color(240, 255, 240)
        pdf.
