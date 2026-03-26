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
    # --- DISEÑO Y ESTILOS ---
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # --- FUNCIÓN PDF CORREGIDA ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # Cabecera azul
        pdf.set_fill_color(0, 71, 171)
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_xy(10, 15)
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "OPTIMARKET PRO | INFORME", 0, 1, 'L')
        
        pdf.set_xy(160, 15)
        pdf.set_font("Arial", '', 10)
        pdf.cell(40, 10, f"FECHA: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 0, 'R')

        # 1. Resumen
        pdf.set_xy(10, 50)
        pdf.set_text_color(0, 71, 171)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_draw_color(0, 71, 171)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0, 0, 0)
        resumen = (f"El negocio ha generado un beneficio neto total de {total:,.2f} EUR, "
                   f"con un ROI promedio del {roi_medio:.1f}% sobre el inventario.")
        pdf.multi_cell(0, 8, resumen)

        # 2. Insights
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, "2. ANALISIS ESTRATEGICO", ln=True)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"> LIDER: {estrella['Producto']} ({estrella['Rentabilidad_Total']:,.2f} EUR)", ln=True)
        pdf.cell(0, 10, f"> EFICIENCIA: {eficiente['Producto']} ({eficiente['ROI_Porcentaje']:.1f}% ROI)", ln=True)

        # 3. Tabla
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 10, " Producto", 1, 0, 'L', True)
        pdf.cell(45, 10, " Beneficio", 1, 0, 'C', True)
        pdf.cell(45, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 9)
        # Limitar a los top 25 para que no se bloquee el PDF si el excel es gigante
        for i, row in df.head(25).iterrows():
            pdf.cell(100, 9, f" {str(row['Producto'])[:45]}", 1)
            pdf.cell(45, 9, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'R')
            pdf.cell(45, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'R')
            
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # --- INTERFAZ ---
    st.title("🚀 OptiMarket Pro")
    archivo = st.sidebar.file_uploader("📂 Cargar Excel de Ventas", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        
        # --- DETECCIÓN DE TUS COLUMNAS REALES ---
        mapeo = {}
        for col in df.columns:
            c_upper = str(col).upper().strip()
            if 'FABRICANTE' in c_upper: mapeo[col] = 'Producto'
            elif 'IMPORTE' in c_upper: mapeo[col] = 'Precio_Venta'
            elif 'COSTE' in c_upper: mapeo[col] = 'Coste_Unidad'
            elif 'CANTIDAD' in c_upper: mapeo[col] = 'Ventas_Mes_Unidades'
        
        df.rename(columns=mapeo, inplace=True)

        cols_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Ventas_Mes_Unidades']
        
        if all(c in df.columns for c in cols_necesarias):
            # Limpiar datos no numéricos y asegurar que no haya costes cero
            df['Precio_Venta'] = pd.to_numeric(df['Precio_Venta'], errors='coerce')
            df['Coste_Unidad'] = pd.to_numeric(df['Coste_Unidad'], errors='coerce')
            df['Ventas_Mes_Unidades'] = pd.to_numeric(df['Ventas_Mes_Unidades'], errors='coerce')
            df = df.dropna(subset=cols_necesarias)
