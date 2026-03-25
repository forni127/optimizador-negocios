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

    # --- FUNCIÓN PDF POTENCIADA ---
    def generar_pdf_pro(df, estrella, eficiente, bajo, total, roi_medio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 22)
        pdf.set_text_color(0, 71, 171)
        pdf.cell(200, 15, "OPTIMARKET PRO", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 12, "1. RESUMEN EJECUTIVO", ln=True)
        pdf.set_font("Arial", '', 12)
        resumen = (f"Durante el periodo analizado, el negocio ha generado un beneficio neto total de {total:,.2f} EUR, "
                   f"con un retorno de inversion (ROI) promedio del {roi_medio:.1f}% sobre el inventario movilizado.")
        pdf.multi_cell(0, 8, resumen)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, "2. ANALISIS ESTRATEGICO (INSIGHTS)", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"> LIDER DE INGRESOS: {estrella['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Este activo representa el mayor flujo de caja ({estrella['Rentabilidad_Total']:,.2f} EUR).")
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"> MAXIMA EFICIENCIA: {eficiente['Producto']}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, f"Con un ROI del {eficiente['ROI_Porcentaje']:.1f}%, es el mejor multiplicador de capital.")
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(90, 10, " Item", 1)
        pdf.cell(50, 10, " Beneficio (EUR)", 1)
        pdf.cell(40, 10, " ROI %", 1, 1)
        pdf.set_font("Arial", '', 10)
        for i, row in df.iterrows():
            pdf.cell(90, 10, f" {str(row['Producto'])[:35]}", 1)
            pdf.cell(50, 10, f" {row['Rentabilidad_Total']:,.2f}", 1)
            pdf.cell(40, 10, f" {row['ROI_Porcentaje']:.1f}%", 1, 1)
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

            # --- GRÁFICA CON COLORES DE SEMÁFORO Y ROI (ACTUALIZADA) ---
            st.subheader("📈 Mapa de Rentabilidad Estratégica")
            fig = px.bar(
                df,
                x='Producto',
                y='Rentabilidad_Total',
                color='Rentabilidad_Total',
                color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                text_auto='.2s',
                hover_data={'ROI_Porcentaje': ':.1f'} # Muestra el ROI al pasar el ratón
            )
            # Personalizamos el texto del tooltip para que quede profesional
            fig.update_traces(hovertemplate='<b>%{x}</b><br>Rentabilidad: %{y:,.2f}€<br>ROI: %{customdata[0]:.1f}%')
           
            st.plotly_chart(fig, use_container_width=True)

            # DIAGNÓSTICO IA
            st.divider()
            st.header("🧠 Diagnóstico de Consultoría IA")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown(f"""<div class="report-card"><h4>🥇 Liderazgo de Mercado: {estrella['Producto']}</h4><p>Este activo es tu principal generador de liquidez. Aporta una parte crítica al beneficio total.<br><br><b>Estrategia:</b> No compitas por precio; compite por servicio.</p></div>""", unsafe_allow_html=True)
            with col_r:
                st.markdown(f"""<div class="report-card" style="border-left-color: #28a745;"><h4>📈 Optimización de Capital: {eficiente['Producto']}</h4><p>Presenta una eficiencia del {eficiente['ROI_Porcentaje']:.0f}%. Es un multiplicador de dinero.<br><br><b>Estrategia:</b> Escalar las ventas de este ítem.</p></div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="report-card" style="border-left-color: #d9534f;"><h4>⚠️ Alerta de Rendimiento: {bajo['Producto']}</h4><p>Este ítem está <b>secuestrando capital</b> con el ROI más bajo ({bajo['ROI_Porcentaje']:.1f}%).<br><br><b>Estrategia:</b> Evalúa una subida de precio o liquidación.</p></div>""", unsafe_allow_html=True)

            # EXPORTACIÓN
            st.sidebar.divider()
            pdf_bytes = generar_pdf_pro(df, estrella, eficiente, bajo, total_neto, roi_medio)
            st.sidebar.download_button("📄 Descargar Informe PDF", data=pdf_bytes, file_name="Informe.pdf")
            st.sidebar.download_button("📊 Exportar CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="datos.csv")
        else:
            st.error("⚠️ Columnas no detectadas.")
    else:
        st.info("👋 Bienvenida/o a OptiMarket Pro. Por favor, cargue su archivo de ventas en el panel lateral para iniciar el diagnóstico de inteligencia de negocio.")
