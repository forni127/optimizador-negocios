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

    # --- FUNCIÓN PDF DE ALTA CONSULTORÍA ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # 1. ENCABEZADO CON LOGO CORPORATIVO (DISEÑADO CON CÓDIGO)
        pdf.set_fill_color(0, 71, 171)  # Azul Profundo
        pdf.rect(0, 0, 210, 45, 'F')
        
        # Dibujo de un logo simple (Un cohete/triángulo estilizado)
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
        pdf.cell(50, 10, f"EMISIÓN: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 0, 'R')
        pdf.ln(35)

        # 2. RESUMEN EJECUTIVO ESTRATÉGICO
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "1. RESUMEN EJECUTIVO DE RENDIMIENTO", ln=True)
        pdf.set_draw_color(0, 71, 171)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(40, 40, 40)
        resumen = (f"Tras la auditoría de datos, se confirma un Beneficio Neto Total de {total:,.2f} EUR. "
                   f"La eficiencia operativa global registra un ROI del {roi_medio:.1f}%, situando la rentabilidad "
                   f"por encima de los objetivos proyectados para este periodo.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(8)

        # 3. ANÁLISIS DE ACTIVOS CLAVE
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "2. INDICADORES CLAVE DE ÉXITO (KPIs)", ln=True)
        pdf.ln(2)

        # Caja de Activo Estrella
        pdf.set_fill_color(245, 248, 255)
        pdf.set_draw_color(0, 71, 171)
        pdf.rect(10, pdf.get_y(), 190, 22, 'FD')
        pdf.set_xy(15, pdf.get_y() + 2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, f"LÍDER DE INGRESOS: {estrella['Producto'].upper()}", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.set_x(15)
        pdf.cell(0, 5, f"Contribución directa de {estrella['Rentabilidad_Total']:,.2f} EUR al flujo de caja neto.", ln=True)
        pdf.ln(12)

        # 4. TABLA TÉCNICA PROFESIONAL
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 10, "3. DESGLOSE DE RENTABILIDAD POR ITEM", ln=True)
        pdf.ln(2)

        # Cabecera de Tabla Premium
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(0, 50, 120)  # Azul Marino
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(255, 255, 255)
        pdf.cell(100, 12, " PRODUCTO / REFERENCIA", 1, 0, 'L', True)
        pdf.cell(45, 12, " BENEFICIO (EUR)", 1, 0, 'C', True)
        pdf.cell(45, 12, " ROI %", 1, 1, 'C', True)

        # Filas Estilizadas (Cebra)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(30, 30, 30)
        for i, row in df.iterrows():
            fill = (i % 2 == 0)
            if fill: pdf.set_fill_color(240, 240, 240)
            else: pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(100, 10, f" {str(row['Producto'])[:45]}", 1, 0, 'L', fill)
            pdf.cell(45, 10, f"{row['Rentabilidad_Total']:,.2f} ", 1, 0, 'R', fill)
            pdf.cell(45, 10, f"{row['ROI_Porcentaje']:.1f}% ", 1, 1, 'R', fill)

        return pdf.output(dest='S').encode('latin-1', 'replace')

    # --- INTERFAZ STREAMLIT ---
    st.title("🚀 OptiMarket Pro")
    archivo = st.sidebar.file_uploader("📂 Cargar Datos de Ventas (Excel)", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        
        # Mapeo de columnas corregido
        for col in df.columns:
            c_upper = str(col).upper()
            if 'PRODUCTO' in c_upper or 'MODELO' in c_upper or 'ITEM' in c_upper: df.rename(columns={col: 'Producto'}, inplace=True)
            elif 'PRECIO' in c_upper and 'VENTA' in c_upper: df.rename(columns={col: 'Precio_Venta'}, inplace=True)
            elif 'COSTE' in c_upper or 'COSTO' in c_upper: df.rename(columns={col: 'Coste_Unidad'}, inplace=True)
            elif 'VENTAS' in c_upper or 'UNIDADES' in c_upper: df.rename(columns={col: 'Ventas_Mes_Unidades'}, inplace=True)

        cols_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Ventas_Mes_Unidades']
        if all(c in df.columns for c
