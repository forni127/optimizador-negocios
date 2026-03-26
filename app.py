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
    # --- FUNCIÓN PDF (Versión compatible con fpdf2) ---
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
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, " Fabricante", 1)
        pdf.cell(50, 10, " Beneficio", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        
        pdf.set_font("Arial", '', 9)
        # Solo ponemos los 30 primeros para que el PDF no pese mil kilos
        for i, row in df.head(30).iterrows():
            pdf.cell(90, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(50, 9, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
            
        return pdf.output() # fpdf2 devuelve bytes directamente o usa dest='S'

    st.title("📊 Análisis de Tienda Real")
    archivo = st.sidebar.file_uploader("Sube el Excel aquí", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            
            # Limpieza total de columnas: quitamos espacios, acentos y pasamos a mayúsculas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # MAPEO AGRESIVO: Buscamos cualquier cosa que se parezca a lo que necesitamos
            mapeo = {}
            for col in df.columns:
                if 'FABRICANTE' in col or 'PRODUCTO' in col: mapeo[col] = 'Producto'
                if 'IMPORTE' in col or 'VENTA' in col or 'PRECIO' in col: mapeo[col] = 'Precio_Venta'
                if 'COSTE' in col or 'COSTO' in col or 'COMPRA' in col: mapeo[col] = 'Coste_Unidad'
                if 'CANTIDAD' in col or 'CANT' in col: mapeo[col] = 'Unidades'
            
            df.rename(columns=mapeo, inplace=True)
            
            columnas_finales = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']
            
            if all(col in df.columns for col in columnas_finales):
                # Limpiar datos numéricos (quitamos errores si hay texto en celdas de dinero)
                for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                # Solo filas con sentido económico
                df = df[df['Coste_Unidad'] > 0].copy()
                
                # Cálculos
                df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
                df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100
                
                # Agrupamos por Fabricante para que la gráfica se vea bien
                resumen = df.groupby('Producto').agg({
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
                
                resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

                # Pantalla principal
                total_b = resumen['Rentabilidad_Total'].sum()
                roi_m = resumen['ROI_Porcentaje'].mean()
                
                c1, c2 = st.columns(2)
                c1.metric("💰 BENEFICIO NETO", f"{total_b:,.2f} €")
                c2.metric("📈 ROI MEDIO", f"{roi_m:.1f} %")

                st.subheader("Top Fabricantes (Los que más dinero te dejan)")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', 
                             color='Rentabilidad_Total', color_continuous_scale='Turbo')
                st.plotly_chart(fig, use_container_width=True)

                # PDF en el lateral
                pdf_output = generar_pdf_pro(resumen, total_b, roi_m)
                st.sidebar.download_button("📩 Descargar Informe PDF", data=pdf_output, file_name="informe.pdf")
            else:
                st.error("No encuentro las columnas correctas en tu Excel.")
                st.write("Columnas que veo en tu archivo:", list(df.columns))
                st.info("Asegúrate de que el Excel tenga: Fabricante, Importe, Coste y Cantidad.")
        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.info("Sube el archivo en el panel izquierdo para empezar.")
