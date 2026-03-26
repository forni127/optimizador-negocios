import streamlit as st
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
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, "INFORME DE RENTABILIDAD", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("helvetica", '', 12)
        pdf.cell(0, 10, f"Beneficio Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"ROI Medio: {roi_m:.1f}%", ln=True)
        pdf.ln(5)
        
        # Tabla simple
        pdf.set_font("helvetica", 'B', 10)
        pdf.cell(90, 10, " Fabricante", 1)
        pdf.cell(50, 10, " Beneficio", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        
        pdf.set_font("helvetica", '', 9)
        for i, row in df.head(25).iterrows():
            pdf.cell(90, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(50, 9, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
            
        return pdf.output()

    st.title("📊 Análisis de Tienda Real")
    archivo = st.sidebar.file_uploader("Sube el Excel aquí", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            # Limpiar nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Mapeo para tu Excel
            mapeo = {
                'FABRICANTE': 'Producto',
                'IMPORTE': 'Precio_Venta',
                'COSTE': 'Coste_Unidad',
                'CANTIDAD': 'Unidades'
            }
            df.rename(columns=mapeo, inplace=True)
            
            # Verificación de columnas
            columnas_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']
            if all(col in df.columns for col in columnas_necesarias):
                
                # Convertir datos a números
                for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                df = df[df['Coste_Unidad'] > 0].copy()
                
                # Cálculos
                df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
                df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100
                
                # Agrupar
                resumen = df.groupby('Producto').agg({
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
                resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

                # Dashboard
                t_b = resumen['Rentabilidad_Total'].sum()
                r_m = resumen['ROI_Porcentaje'].mean()
                
                col1, col2 = st.columns(2)
                col1.metric("💰 BENEFICIO NETO", f"{t_b:,.2f} €")
                col2.metric("📈 ROI MEDIO", f"{r_m:.1f} %")

                st.subheader("Top Fabricantes")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', color='Rentabilidad_Total')
                st.plotly_chart(fig, use_container_width=True)

                # PDF
                pdf_bytes = generar_pdf_pro(resumen, t_b, r_m)
                st.sidebar.download_button("📩 Descargar PDF", data=pdf_bytes, file_name="informe.pdf", mime="application/pdf")
            else:
                st.error("No se encuentran las columnas. Revisa que el Excel tenga: Fabricante, Importe, Coste y Cantidad.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Sube el Excel en el panel lateral.")
