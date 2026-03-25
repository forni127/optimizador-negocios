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
        
        # Encabezado con Estilo Corporativo
        pdf.set_fill_color(0, 71, 171) # Azul Oscuro
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", 'B', 26)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 25, "OPTIMARKET PRO", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(190, 0, f"Informe Estrategico de Inteligencia de Negocio - {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(25)

        # 1. RESUMEN EJECUTIVO (Caja Destacada)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_draw_color(0, 71, 171)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(30, 30, 30)
        resumen = (f"El analisis de rendimiento concluye que el negocio ha generado un Beneficio Neto Total de {total:,.2f} EUR. "
                   f"La cartera de productos analizada opera con una eficiencia media (ROI) del {roi_medio:.1f}%.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(10)

        # 2. INSIGHTS ESTRATÉGICOS
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # Card: Liderazgo
        pdf.set_fill_color(240, 245, 255)
        pdf.rect(10, pdf.get_y(), 190, 25, 'F')
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, f"  > LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 5, f"    Genera el mayor flujo de caja con {estrella['Rentabilidad_Total']:,.2f} EUR netos.", ln=True)
        pdf.ln(10)

        # Card: Eficiencia
        pdf.set_fill_color(240, 255, 240)
        pdf.rect(10, pdf.get_y(), 190, 25, 'F')
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(40, 167, 69)
        pdf.cell(0, 10, f"  > MAXIMA EFICIENCIA: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 5, f"    Multiplicador de capital critico con un ROI del {eficiente['ROI_Porcentaje']:.1f}%.", ln=True)
        pdf.ln(15)
