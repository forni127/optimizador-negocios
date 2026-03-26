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
    # --- ESTILOS VISUALES ---
    st.markdown("""
        <style>
        .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 6px solid #0047AB; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #1e1e1e; }
        .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e6ed; }
        h4 { color: #0047AB; margin-top: 0; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # --- FUNCIÓN PDF (Compatible con fpdf2) ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 18)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(0, 15, "OPTIMARKET PRO - INFORME ESTRATÉGICO", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("helvetica", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_font("helvetica", '', 11)
        resumen = f"Beneficio Neto Total: {total:,.2f} EUR | ROI Promedio: {roi_medio:.1f}%"
        pdf.cell(0, 10, resumen, ln=True)
        
        pdf.ln(5)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "2. TOP 10 FABRICANTES POR RENTABILIDAD", ln=True)
        
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 10, " Fabricante", 1, 0, 'L', True)
        pdf.cell(45, 10, " Beneficio", 1, 0, 'C', True)
        pdf.cell(45, 10, " ROI %", 1, 1, 'C', True)
        
        pdf.set_font("helvetica", '', 9)
        for i, row in df.head(10).iterrows():
            pdf.cell(100, 9, f" {str(row['Producto'])[:40]}", 1)
            pdf.cell(45, 9, f" {row['Rentabilidad_Total']:,.2f}", 1, 0, 'R')
            pdf.cell(45, 9, f" {row['ROI_Porcentaje']:.1f}%", 1, 1, 'R')
            
        return pdf.output()

    st.title("🚀 OptiMarket Pro: Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("📂 Cargar Excel de Ventas", type=["xlsx"])

    if archivo:
        try:
            df = pd.read_excel(archivo)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # MAPEO PARA TU EXCEL REAL
            mapeo = {
                'FABRICANTE': 'Producto',
                'IMPORTE': 'Precio_Venta',
                'COSTE': 'Coste_Unidad',
                'CANTIDAD': 'Unidades'
            }
            df.rename(columns=mapeo, inplace=True)
            
            columnas_ok = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Unidades']
            
            if all(c in df.columns for c in columnas_ok):
                # Limpieza de datos
                for c in ['Precio_Venta', 'Coste_Unidad', 'Unidades']:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                
                df = df[df['Coste_Unidad'] > 0].copy()
                df['Beneficio'] = (df['Precio_Venta'] - df['Coste_Unidad']) * df['Unidades']
                df['ROI'] = ((df['Precio_Venta'] - df['Coste_Unidad']) / df['Coste_Unidad']) * 100
                
                # AGRUPACIÓN POR FABRICANTE
                resumen = df.groupby('Producto').agg({
                    'Beneficio': 'sum',
                    'ROI': 'mean'
                }).reset_index().rename(columns={'Beneficio': 'Rentabilidad_Total', 'ROI': 'ROI_Porcentaje'})
                resumen = resumen.sort_values('Rentabilidad_Total', ascending=False)

                # --- KPIs SUPERIORES ---
                total_n = resumen['Rentabilidad_Total'].sum()
                roi_m = resumen['ROI_Porcentaje'].mean()
                estrella = resumen.iloc[0]
                eficiente = resumen.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
                bajo = resumen.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

                c1, c2, c3 = st.columns(3)
                c1.metric("💰 BENEFICIO TOTAL", f"{total_n:,.2f} €")
                c2.metric("⭐ ACTIVO ESTRELLA", estrella['Producto'][:15])
                c3.metric("📊 ROI PROMEDIO", f"{roi_m:.1f} %")

                # --- GRÁFICA ---
                st.subheader("📈 Mapa de Rentabilidad Estratégica")
                fig = px.bar(resumen.head(15), x='Producto', y='Rentabilidad_Total', 
                             color='Rentabilidad_Total', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)

                # --- DIAGNÓSTICO IA (IMPORTANTE) ---
                st.divider()
                st.header("🧠 Diagnóstico de Consultoría IA")
                col_l, col_r = st.columns(2)
                
                with col_l:
                    st.markdown(f"""<div class="report-card"><h4>🥇 Liderazgo: {estrella['Producto']}</h4><p>Este fabricante aporta <b>{estrella['Rentabilidad_Total']:,.2f}€</b>. Es tu principal fuente de caja.<br><br><b>Estrategia:</b> Refuerza stock y prioridad en escaparate.</p></div>""", unsafe_allow_html=True)
                
                with col_r:
                    st.markdown(f"""<div class="report-card" style="border-left-color: #28a745;"><h4>📈 Eficiencia: {eficiente['Producto']}</h4><p>Tiene un ROI del <b>{eficiente['ROI_Porcentaje']:.1f}%</b>. Es el que más rápido multiplica tu dinero.<br><br><b>Estrategia:</b> Busca ampliar gama de este proveedor.</p></div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class="report-card" style="border-left-color: #d9534f;"><h4>⚠️ Alerta Crítica: {bajo['Producto']}</h4><p>Rendimiento mínimo (ROI: {bajo['ROI_Porcentaje']:.1f}%). Este inventario está <b>bloqueando capital</b>.<br><br><b>Estrategia:</b> Revisar precios o negociar mejores costes.</p></div>""", unsafe_allow_html=True)

                # --- EXPORTACIÓN ---
                st.sidebar.divider()
                pdf_bytes = generar_pdf_pro(resumen, estrella, eficiente, bajo, total_n, roi_m)
                st.sidebar.download_button("📄 Descargar Informe PDF", data=bytes(pdf_bytes), file_name="Informe_Estrategico.pdf", mime="application/pdf")
                st.sidebar.download_button("📊 Exportar Datos CSV", data=resumen.to_csv(index=False).encode('utf-8'), file_name="analisis.csv")
            
            else:
                st.error("Faltan columnas (Fabricante, Importe, Coste, Cantidad)")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("👋 Sube tu Excel para activar el Diagnóstico IA.")
