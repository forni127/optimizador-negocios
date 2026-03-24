import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="OptiMarket Pro", page_icon="🚀", layout="wide")

# Estilos visuales
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); color: black; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PDF SEGURA (Simplificada para evitar errores)
def crear_pdf_seguro(df, estrella_nom, estrella_val, eficiente_nom, eficiente_roi, total):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Informe de Optimizacion OptiMarket", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Beneficio Total: {total:.2f} EUR", ln=True)
        pdf.cell(200, 10, f"Producto Estrella: {estrella_nom}", ln=True)
        pdf.cell(200, 10, f"ROI Maximo: {eficiente_roi:.1f}% ({eficiente_nom})", ln=True)
        return pdf.output(dest='S').encode('latin-1', 'replace')
    except:
        return None

# --- APP PRINCIPAL ---
st.title("🚀 OptiMarket Pro")
st.subheader("Consultoría de Negocios Automática")

archivo = st.sidebar.file_uploader("Sube tu Excel aquí", type=["xlsx"])

if archivo is not None:
    # Leer datos
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    
    # Cálculos básicos
    df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
    df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
    beneficio_total = df['Rentabilidad_Total'].sum()
    
    # Extraer ganadores
    estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
    eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]

    # MOSTRAR MÉTRICAS
    col1, col2, col3 = st.columns(3)
    col1.metric("Beneficio Neto", f"{beneficio_total:,.2f} €")
    col2.metric("Líder", estrella['Producto'])
    col3.metric("ROI Máximo", f"{eficiente['ROI_Porcentaje']:.1f}%")

    # MOSTRAR GRÁFICA
    st.subheader("📊 Análisis Visual")
    fig = px.bar(df, x='Producto', y='Rentabilidad_Total', color='ROI_Porcentaje', 
                 color_continuous_scale='RdYlGn', title="Rentabilidad por Producto")
    st.plotly_chart(fig, use_container_width=True)

    # MOSTRAR COMENTARIOS IA
    st.divider()
    st.header("🧠 Informe del Consultor IA")
    
    st.markdown(f"""
    <div class="report-card">
        <h4>🥇 Análisis del Líder: {estrella['Producto']}</h4>
        <p>Este producto ha generado <b>{estrella['Rentabilidad_Total']:.2f}€</b> netos. Es el motor de tu caja mensual.</p>
    </div>
    <div class="report-card" style="border-left-color: #28a745;">
        <h4>📈 El Rey del ROI: {eficiente['Producto']}</h4>
        <p>Es tu producto más eficiente con un <b>{eficiente['ROI_Porcentaje']:.0f}%</b> de retorno por euro invertido.</p>
    </div>
    """, unsafe_allow_html=True)

    # DESCARGAS EN LA BARRA LATERAL
    st.sidebar.divider()
    
    # Botón PDF con control de errores
    pdf_data = crear_pdf_seguro(df, estrella['Producto'], estrella['Rentabilidad_Total'], 
                                eficiente['Producto'], eficiente['ROI_Porcentaje'], beneficio_total)
    
    if pdf_data:
        st.sidebar.download_button("📄 Descargar Informe PDF", data=pdf_data, file_name="informe.pdf", mime="application/pdf")
    
    st.sidebar.download_button("📥 Descargar Excel", data=df.to_csv(index=False), file_name="datos.csv")

else:
    st.info("👋 Esperando archivo Excel...")
