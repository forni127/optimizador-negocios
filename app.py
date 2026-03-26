import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# =========================================================
# 🛠️ CONFIGURACIÓN RÁPIDA DE COLUMNAS (Cambia esto según el cliente)
# =========================================================
# Para el archivo "RESUMEN-TEMPORADA-ART.xlsx":
COL_PRODUCTO = "REFERENC."    
COL_PRECIO   = "PRECIO_VENTA" # Si no existe, el código creará una estimación
COL_COSTE    = "COSTE_UNIDAD" # Si no existe, el código creará una estimación
COL_VENTAS   = "VENDIDO"      
# =========================================================

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

    # --- FUNCIÓN PDF POTENCIADA (Corregida para fpdf2) ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 22)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(190, 15, "OPTIMARKET PRO", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_font("helvetica", '', 12)
        resumen = (f"Durante el periodo analizado, el negocio ha generado un beneficio neto total de {total:,.2f} EUR, "
                   f"con un retorno de inversion (ROI) promedio del {roi_medio:.1f}% sobre el inventario movilizado.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 12, "2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True)
        pdf.ln(5)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("helvetica", '', 11)
        pdf.multi_cell(0, 8, f"Este activo representa el mayor flujo de caja ({estrella['Rentabilidad_Total']:,.2f} EUR).")
        pdf.ln(5)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, f"> MAXIMA EFICIENCIA: {eficiente['Producto']}", ln=True)
        pdf.set_font("helvetica", '', 11)
        pdf.multi_cell(0, 8, f"Con un ROI del {eficiente['ROI_Porcentaje']:.1f}%, es el mejor multiplicador de capital.")
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(90, 10, " Item", 1)
        pdf.cell(50, 10, " Beneficio (EUR)", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        pdf.set_font("helvetica", '', 10)
        for i, row in df.head(30).iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
        return pdf.output()

    # --- INTERFAZ ---
    st.title("🚀 OptiMarket Pro")
    archivo = st.sidebar.file_uploader("📂 Cargar Datos de Ventas (Excel)", type=["xlsx"])

    if archivo:
        try:
            # NOTA: Usamos skiprows=1 para saltar la fila vacía de tu Excel
            df = pd.read_excel(archivo, skiprows=1)
            
            # Limpiamos nombres de columnas (quitar espacios)
            df.columns = [str(c).strip() for c in df.columns]

            # MAREO DINÁMICO DE TUS COLUMNAS
            mapeo = {
                COL_PRODUCTO: 'Producto',
                COL_VENTAS: 'Ventas_Mes_Unidades'
            }
            
            # Si el Excel tiene precio y coste los usamos, si no, creamos columnas a 0
            if COL_PRECIO in df.columns: mapeo[COL_PRECIO] = 'Precio_Venta'
            else: df['Precio_Venta'] = 0
            
            if COL_COSTE in df.columns: mapeo[COL_COSTE] = 'Coste_Unidad'
            else: df['Coste_Unidad'] = 0

            df.rename(columns=mapeo, inplace=True)

            cols_necesarias = ['Producto', 'Ventas_Mes_Unidades']
            
            if all(c in df.columns for c in cols_necesarias):
                # Limpiar números
                for c in ['Precio_Venta', 'Coste_Unidad', 'Ventas_Mes_Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

                # CÁLCULOS DE RENTABILIDAD
                df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
                df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
                # Evitar división por cero
                df['ROI_Porcentaje'] = df.apply(lambda x: (x['Margen'] / x['Coste_Unidad'] * 100) if x['Coste_Un
