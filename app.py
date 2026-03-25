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

    # --- FUNCIÓN PDF ULTRA PROFESIONAL (POTENCIADA) ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado de Marca
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(0, 71, 171) # Azul Corporativo
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
                   f"presenta un ROI promedio del {roi_medio:.1f}%, lo que indica una saludable "
                   f"capacidad de retorno sobre el capital invertido.")
        pdf.multi_cell(0, 7, resumen)
        pdf.ln(10)
        
        # 2. ANÁLISIS ESTRATÉGICO (INSIGHTS)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, " 2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True, fill=True)
        pdf.ln(5)
        
        # Líder de Ingresos
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 8, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Este producto es el motor financiero de la operacion, aportando {estrella['Rentabilidad_Total']:,.2f} EUR. Su mantenimiento es critico para la estabilidad del flujo de caja.")
        pdf.ln(4)
        
        # Máxima Eficiencia
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(40, 167, 69) # Verde
        pdf.cell(0, 8, f"> MAXIMA EFICIENCIA DE CAPITAL: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Con un ROI extraordinario del {eficiente['ROI_Porcentaje']:.1f}%, este item es el mas eficiente. Se recomienda aumentar su exposicion para maximizar el margen neto.")
        pdf.ln(10)

        # 3. DESGLOSE TÉCNICO
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, " 3. DESGLOSE TECNICO POR PRODUCTO", ln=True, fill=True)
        pdf.ln(5)
        
        # Cabecera de Tabla
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(0, 71, 171)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(90, 10, " Producto / Item", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        
        # Filas de la Tabla
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(0, 0, 0)
        for i, row in df.iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'C')
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'C')
            
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # --- INTERFAZ ---
    st.title("🚀 OptiMarket Pro")
    archivo = st.sidebar.file_uploader("📂 Cargar Datos de Ventas (Excel)", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        
        # DETECCIÓN INTELIGENTE DE COLUMNAS
        for col in df.columns:
            c_upper = col.upper()
            if 'PRODUCTO' in c_upper or 'MODELO' in c_upper or 'ITEM' in c_upper:
                df.rename(columns={col: 'Producto'}, inplace=True)
            elif 'PRECIO' in c_upper and 'VENTA' in c_upper:
                df.rename(columns={col: 'Precio_Venta'}, inplace=True)
            elif 'COSTE' in c_upper or 'COSTO' in c_upper:
                df.rename(columns={col: 'Coste_Unidad'}, inplace=True)
            elif 'VENTAS' in c_upper or 'UNIDADES' in c_upper:
                df.rename(columns={col: 'Ventas_Mes_Unidades'}, inplace=True)

        cols_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Ventas_Mes_Unidades']
        if all(c in df.columns for c in cols_necesarias):
            df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
            df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
            df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
            
            total_neto = df['Rentabilidad_Total'].sum()
            roi_medio = df['ROI_Porcentaje'].mean()
            estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
            eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
            bajo = df.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("BENEFICIO NETO TOTAL", f"{total_neto:,.2f} €")
            c2.metric("ACTIVO ESTRELLA", estrella['Producto'])
            c3.metric("ROI PROMEDIO", f"{roi_medio:.1f} %")

            # --- GRÁFICA CON ROI EN TOOLTIP ---
            st.subheader("📈 Mapa de Rentabilidad Estratégica")
            fig = px.bar(
                df, 
                x='Producto', 
                y='Rentabilidad_Total', 
                color='Rentabilidad_Total',
                color_continuous_scale=[(0
