import streamlit as st
import pd as pd
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- BLOQUE DE SEGURIDAD ---
st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Incorrecta")
else:
    # --- FUNCIÓN PDF ---
    def generar_pdf_pro(df, total, roi_m):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "INFORME DE VENTAS REAL", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Beneficio Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"ROI Medio: {roi_m:.1f}%", ln=True)
        pdf.ln(5)
        # Tabla
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, " Fabricante", 1)
        pdf.cell(50, 10, " Beneficio", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        pdf.set_font("Arial", '', 9)
        for i, row in df.head(30).iterrows():
            pdf.cell(90, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(50, 9, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
        return pdf.output(dest='S').encode('latin-1', 'replace')

    st.title("📊 Análisis de Tienda Real")
    archivo = st.sidebar.file_uploader("Sube el Excel aquí", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)
        
        # --- LIMPIEZA CRÍTICA DE COLUMNAS ---
        # Pasamos todo a mayúsculas y quitamos espacios para que coincida con tu Excel
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mapeo exacto basado en tu captura
        mapeo = {
            'FABRICANTE': 'Producto',
            'IMPORTE': 'Precio_Venta',
            'COSTE': 'Coste_Unidad',
            'CANTIDAD': 'Unidades'
        }
        
        df.rename(columns=mapeo, inplace=True)
        
        columnas_finales = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']
        
        if all(col in df.columns for col in columnas_finales):
            # Convertir a números por si acaso
            for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            # Filtramos filas sin coste para evitar errores
            df = df[df['Coste_Unidad'] > 0].copy()
            
            # Cálculos de negocio
            df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
            df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100
            
            # Agrupamos por marca (Fabricante)
            resumen = df.groupby('Producto').agg({
                'Beneficio': 'sum',
                'ROI': 'mean'
            }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
            
            resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

            # Visualización
            c1, c2 = st.columns(2)
            total_b = resumen['Rentabilidad_Total'].sum()
            roi_promedio = resumen['ROI_Porcentaje'].mean()
            
            c1.metric("💰 BENEFICIO NETO", f"{total_b:,.2f} €")
            c2.metric("📈 ROI MEDIO", f"{roi_promedio:.1f} %")

            st.subheader("Top 10 Fabricantes por Beneficio")
            fig = px.bar(resumen.head(10), x='Producto', y='Rentabilidad_Total', color='Rentabilidad_Total')
            st.plotly_chart(fig, use_container_width=True)

            # PDF
            pdf_bytes = generar_pdf_pro(resumen, total_b, roi_promedio)
            st.sidebar.download_button("📩 Descargar Informe", data=pdf_bytes, file_name="informe_real.pdf")
            
        else:
            st.error("Faltan columnas. Asegúrate de que el Excel tenga: Fabricante, Importe, Coste y Cantidad.")
            st.write("Columnas detectadas:", list(df.columns))
    else:
        st.info("Sube el archivo en el panel izquierdo.")
