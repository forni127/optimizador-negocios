import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# --- SEGURIDAD ---
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
    # --- FUNCIÓN PDF CORREGIDA PARA FPDF2 ---
    def generar_pdf_pro(df, total, roi_m):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(0, 10, "INFORME ESTRATEGICO DE VENTAS", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("helvetica", '', 12)
        pdf.cell(0, 10, f"Beneficio Neto Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"ROI Promedio: {roi_m:.1f}%", ln=True)
        pdf.ln(5)
        
        # Tabla de resultados
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(90, 10, " Fabricante", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio (EUR)", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("helvetica", '', 9)
        # Mostramos los top 30 para un informe ejecutivo
        for i, row in df.head(30).iterrows():
            pdf.cell(90, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(50, 9, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'R')
            pdf.cell(40, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'R')
            
        # IMPORTANTE: fpdf2 devuelve los bytes directamente con output()
        return pdf.output()

    st.title("📊 Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("Sube tu Excel de Ventas", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            # Normalizar columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Mapeo según tu archivo real
            mapeo = {
                'FABRICANTE': 'Producto',
                'IMPORTE': 'Precio_Venta',
                'COSTE': 'Coste_Unidad',
                'CANTIDAD': 'Unidades'
            }
            df.rename(columns=mapeo, inplace=True)
            
            columnas_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']
            
            if all(col in df.columns for col in columnas_necesarias):
                # Limpiar y convertir a números
                for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                # Solo productos con coste real
                df = df[df['Coste_Unidad'] > 0].copy()
                
                # Cálculos de rentabilidad
                df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
                df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100
                
                # Agrupar por fabricante (limpiando nombres)
                df['Producto'] = df['Producto'].astype(str).str.upper()
                resumen = df.groupby('Producto').agg({
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
                
                resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

                # --- DASHBOARD ---
                total_b = resumen['Rentabilidad_Total'].sum()
                roi_m = resumen['ROI_Porcentaje'].mean()
                
                c1, c2 = st.columns(2)
                c1.metric("💰 BENEFICIO TOTAL", f"{total_b:,.2f} €")
                c2.metric("📈 ROI MEDIO", f"{roi_m:.1f} %")

                st.subheader("Top 15 Fabricantes por Rentabilidad")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', 
                             color='Rentabilidad_Total', color_continuous_scale='Blues',
                             labels={'Rentabilidad_Total': 'Beneficio (€)'})
                st.plotly_chart(fig, use_container_width=True)

                # --- DESCARGA ---
                pdf_bytes = generar_pdf_pro(resumen, total_b, roi_m)
                st.sidebar.divider()
                st.sidebar.write("### Exportar Resultados")
                st.sidebar.download_button(
                    label="📄 Descargar Informe PDF",
                    data=bytes(pdf_bytes), # Aseguramos formato bytes
                    file_name=f"Informe_Ventas_{datetime.date.today()}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("No se detectan las columnas necesarias (Fabricante, Importe, Coste, Cantidad).")
        except Exception as e:
            st.error(f"Hubo un problema al procesar los datos: {e}")
    else:
        st.info("👋 Bienvenida/o. Por favor, sube tu archivo Excel para analizar los beneficios.")
