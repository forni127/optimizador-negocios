import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

# --- SISTEMA DE CONTRASEÑA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado OptiMarket")
        user_pass = st.text_input("Introduce la clave de consultor:", type="password")
        if st.button("Desbloquear Sistema"):
            if user_pass == "SOCIO2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta.")
        return False
    return True

if check_password():
    # 2. ESTILOS VISUALES
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # 3. FUNCIÓN PDF PROFESIONAL
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
        # Tabla simple
        for i, row in df.iterrows():
            pdf.cell(80, 10, f"{str(row['Producto'])[:30]}", 1)
            pdf.cell(50, 10, f"{row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 10, f"{row['ROI_Porcentaje']:.1f}%", 1, 1)
        return pdf.output(dest='S').encode('latin-1
