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
    # --- ESTILOS ---
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h4 { color: #0047AB; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 71, 171)
        pdf.rect(0, 0, 210, 35, 'F')
        pdf.set_xy(10, 10)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "INFORME DE RENTABILIDAD REAL", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(10, 45)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Beneficio Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"ROI Promedio: {roi_medio:.1f}%", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 10, " Fabricante", 1, 0, 'L', True)
        pdf.cell(45, 10, " Beneficio", 1, 0, 'C', True)
        pdf.cell(45, 10, " ROI %", 1, 1, 'C', True)
        pdf.set_font("Arial", '', 10)
        for i, row in df.head(30).iterrows():
            pdf.cell(100, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(45, 9, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'R')
            pdf.cell(45, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'R')
        return pdf.output(dest='S').encode('latin-1', 'replace')

    st.title("🚀 OptiMarket Pro: Análisis Real")
    archivo = st.sidebar.file_uploader("Subir Excel de la Tienda", type=["xlsx", "csv"])

    if archivo:
        try:
            # Leer archivo (soporta Excel y CSV por si acaso)
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            # Limpiar nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # MAPEO DINÁMICO (Busca por palabras clave)
            mapeo = {}
            for col in df.columns:
                if 'FABRICANTE' in col or 'PRODUCTO' in col: mapeo[col] = 'Producto'
                elif 'IMPORTE' in col or 'VENTA' in col: mapeo[col] = 'Precio_Venta'
                elif 'COSTE' in col or 'COSTO' in col: mapeo[col] = 'Coste_Unidad'
                elif 'CANTIDAD' in col: mapeo[col] = 'Unidades'

            df.rename(columns=mapeo, inplace=True)
            cols_ok = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']

            if all(c in df.columns for c in cols_ok):
                # Limpiar números
                for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

                # Cálculos
                df = df[df['Coste_Unidad'] > 0].copy()
                df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
                df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100

                # AGRUPAR POR FABRICANTE (Para que sea útil)
                resumen = df.groupby('Producto').agg({
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
                resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

                # KPIs
                t1, t2, t3 = st.columns(3)
                total_n = resumen['Rentabilidad_Total'].sum()
                roi_m = resumen['ROI_Porcentaje'].mean()
                top_f = resumen.iloc[0]

                t1.metric("BENEFICIO TOTAL", f"{total_n:,.2f} €")
                t2.metric("TOP FABRICANTE", top_f['Producto'][:15])
                t3.metric("ROI MEDIO", f"{roi_m:.1f} %")

                # Gráfica
                st.subheader("Rentabilidad por Fabricante (Top 15)")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', color='Rentabilidad_Total', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)

                # Descarga
                pdf_b = generar_pdf_pro(resumen, top_f, top_f, top_f, total_n, roi_m)
                st.sidebar.download_button("📩 Descargar Informe PDF", data=pdf_b, file_name="Analisis_Ventas.pdf")
            else:
                st.error("⚠️ El archivo no tiene las columnas: Fabricante, Importe, Coste y Cantidad.")
                st.write("Columnas encontradas:", list(df.columns))
        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")
    else:
        st.info("Esperando archivo... Sube el Excel de ventas en el lateral.")
