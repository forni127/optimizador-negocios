import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# =========================================================
# 🛠️ CONFIGURACIÓN DE COLUMNAS (Cambia esto según tu Excel)
# =========================================================
# Pon aquí el nombre exacto de las columnas de tu archivo Excel:
COL_PRODUCTO = "Fabricante"    # Ej: "Fabricante", "Modelo", "Referencia"
COL_MODELO = "Modelo" 
COL_PRECIO   = "Precio"       # Ej: "Importe", "PVP", "Venta"
COL_COSTE    = "Coste"        # Ej: "Coste", "Costo", "Compra"
COL_VENTAS   = "Venta"      # Ej: "Cantidad", "Unidades", "Vendido"
# =========================================================

st.set_page_config(page_title="OptiMarket Pro | Intelligence", page_icon="🚀", layout="wide")

# --- BLOQUE DE SEGURIDAD ---
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

    # --- FUNCIÓN PDF ---
    def generar_pdf_pro(df, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 20)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 15, "OPTIMARKET PRO - INFORME", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("helvetica", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Beneficio Total: {total:,.2f} EUR", ln=True)
        pdf.cell(0, 10, f"ROI Promedio: {roi_medio:.1f}%", ln=True)
        pdf.ln(5)
        
        # Tabla
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(90, 10, " Producto", 1, 0, 'L', True)
        pdf.cell(50, 10, " Beneficio", 1, 0, 'C', True)
        pdf.cell(40, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("helvetica", '', 10)
        for i, row in df.head(20).iterrows():
            pdf.cell(90, 9, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 9, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'R')
            pdf.cell(40, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'R')
        return pdf.output()

    # --- INTERFAZ ---
    st.title("🚀 OptiMarket Pro")
    archivo = st.sidebar.file_uploader("📂 Cargar Excel", type=["xlsx"])

    if archivo:
        try:
            # Saltamos la primera fila si el excel tiene basura arriba (skiprows=1)
            # Si tu excel es limpio, puedes quitar el skiprows=1
            df = pd.read_excel(archivo, skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]

            # Mapeo de columnas según configuración
            df = df.rename(columns={
                COL_PRODUCTO: 'Producto',
                COL_PRECIO: 'Precio_Venta',
                COL_COSTE: 'Coste_Unidad',
                COL_VENTAS: 'Ventas_Unidades'
            })

            # Verificar si las columnas existen tras el renombre
            columnas_finales = ['Producto', 'Ventas_Unidades']
            if all(c in df.columns for c in columnas_finales):
                
                # Convertir a números (por si hay basura en el Excel)
                for c in ['Precio_Venta', 'Coste_Unidad', 'Ventas_Unidades']:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                    else:
                        df[c] = 0 # Si no hay precio/coste, creamos la columna a 0

                # Cálculos
                df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
                df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Unidades']
                df['ROI_Porcentaje'] = df.apply(lambda x: (x['Margen']/x['Coste_Unidad']*100) if x['Coste_Unidad']>0 else 0, axis=1)

                # Agrupación para limpiar el gráfico
                resumen = df.groupby('Producto').agg({
                    'Ventas_Unidades': 'sum',
                    'Rentabilidad_Total': 'sum',
                    'ROI_Porcentaje': 'mean'
                }).reset_index().sort_values('Rentabilidad_Total', ascending=False)

                # KPIs
                total_n = resumen['Rentabilidad_Total'].sum()
                roi_m = resumen['ROI_Porcentaje'].mean()
                estrella = resumen.iloc[0]
                eficiente = resumen.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
                bajo = resumen.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

                c1, c2, c3 = st.columns(3)
                c1.metric("BENEFICIO NETO", f"{total_n:,.2f} €")
                c2.metric("ACTIVO ESTRELLA", str(estrella['Producto'])[:15])
                c3.metric("ROI PROMEDIO", f"{roi_m:.1f} %")

                # Gráfica
                st.subheader("📊 Mapa de Rentabilidad")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', color='Rentabilidad_Total',
                             color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)

                # Diagnóstico IA
                st.divider()
                st.header("🧠 Diagnóstico de Consultoría IA")
                l, r = st.columns(2)
                with l:
                    st.markdown(f'<div class="report-card"><h4>🥇 Líder: {estrella["Producto"]}</h4><p>Aporta {estrella["Rentabilidad_Total"]:,.2f}€. Es tu mayor flujo de caja.</p></div>', unsafe_allow_html=True)
                with r:
                    st.markdown(f'<div class="report-card" style="border-left-color: #28a745;"><h4>📈 Eficiencia: {eficiente["Producto"]}</h4><p>ROI del {eficiente["ROI_Porcentaje"]:.1f}%. Máxima rentabilidad por euro.</p></div>', unsafe_allow_html=True)

                # Exportación
                pdf_bytes = generar_pdf_pro(resumen, total_n, roi_m)
                st.sidebar.download_button("📄 Descargar PDF", data=bytes(pdf_bytes), file_name="Informe.pdf")
                
            else:
                st.error(f"No encuentro las columnas configuradas. Veo: {list(df.columns)}")
        
        except Exception as e:
            st.error(f"Error al procesar: {e}")
    else:
        st.info("👋 Sube tu Excel para iniciar el diagnóstico.")
