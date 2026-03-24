import streamlit as st
import pandas as pd
import plotly.express as px

# 1. IDENTIDAD VISUAL Y MARCA
st.set_page_config(
    page_title="OptiMarket Pro | Consultor de Inventario",
    page_icon="🚀",
    layout="wide"
)

# Estilo profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 OptiMarket Pro")
st.subheader("Sistema de Inteligencia de Negocio y Optimización de Márgenes")
st.divider()

# 2. CARGA DE DATOS
st.sidebar.header("📂 Panel de Control")
archivo = st.sidebar.file_uploader("Sube tu Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip() 
    
    # CÁLCULOS AVANZADOS
    df['Margen_Unitario'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad_Total'] = df['Margen_Unitario'] * df['Ventas_Mes_Unidades']
    df['ROI_Porcentaje'] = (df['Margen_Unitario'] / df['Coste_Unidad']) * 100
    
    # 3. MÉTRICAS RESUMEN
    col1, col2, col3 = st.columns(3)
    beneficio_total = df['Rentabilidad_Total'].sum()
    mejor_prod = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
    roi_medio = df['ROI_Porcentaje'].mean()
    
    col1.metric("Beneficio Neto Total", f"{beneficio_total:,.2f} €")
    col2.metric("Líder en Ventas", mejor_prod['Producto'], f"+{mejor_prod['Rentabilidad_Total']:.0f}€")
    col3.metric("Eficiencia Media (ROI)", f"{roi_medio:.1f} %")

    # 4. GRÁFICA DE ANÁLISIS
    st.subheader("📊 Análisis de Rendimiento por Producto")
    fig = px.bar(df, x='Producto', y='Rentabilidad_Total', 
                 color='ROI_Porcentaje', 
                 title="Beneficio Total (Altura) vs Rentabilidad ROI (Color)",
                 labels={'Rentabilidad_Total': 'Euros Netos Ganados', 'ROI_Porcentaje': '% ROI'},
                 color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

    # 5. EL CEREBRO DE LA IA (Consultoría Trabajada)
    st.divider()
    st.header("🧠 Informe Estratégico del Consultor IA")
    
    # Lógica para detectar perfiles
    estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
    eficiente = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
    bajo_rendimiento = df.sort_values('ROI_Porcentaje', ascending=True).iloc[0]

    # BLOQUE 1: PRODUCTO ESTRELLA (EJEMPLO IPHONE)
    st.markdown(f"""
    <div class="report-card">
        <h4>🥇 Análisis del Líder de Ingresos: <b>{estrella['Producto']}</b></h4>
        <p>Este producto es el motor financiero de tu negocio actualmente. Ha generado <b>{estrella['Rentabilidad_Total']:.2f}€</b> de beneficio neto. 
        Aunque su precio de venta sea alto, su volumen de ventas lo convierte en tu prioridad número 1. 
        <b>Acción recomendada:</b> Mantener stock de seguridad y considerar campañas de 'Upselling' (vender accesorios) para este producto.</p>
    </div>
    """, unsafe_allow_html=True)

    # BLOQUE 2: EFICIENCIA (EJEMPLO FUNDAS)
    st.markdown(f"""
    <div class="report-card" style="border-left-color: #28a745;">
        <h4>📈 El Rey del ROI: <b>{eficiente['Producto']}</b></h4>
        <p>¡Atención aquí! Por cada euro que inviertes en este producto, obtienes un retorno del <b>{eficiente['ROI_Porcentaje']:.0f}%</b>. 
        Es mucho más eficiente que el resto. <b>Análisis:</b> A menudo, productos como {eficiente['Producto']} pasan desapercibidos frente a otros más caros, 
        pero son los que realmente hacen crecer tu margen sin arriesgar mucho capital.</p>
    </div>
    """, unsafe_allow_html=True)

    # BLOQUE 3: ALERTA DE OPTIMIZACIÓN
    st.markdown(f"""
    <div class="report-card" style="border-left-color: #dc3545;">
        <h4>⚠️ Alerta de Optimización: <b>{bajo_rendimiento['Producto']}</b></h4>
        <p>Este producto presenta el ROI más bajo de tu cartera (<b>{bajo_rendimiento['ROI_Porcentaje']:.1f}%</b>). 
        Estás inmovilizando capital por un retorno muy pobre. 
        <b>Sugerencia:</b> Revisa si puedes subir el precio de venta o si es momento de liquidar este stock para reinvertir el dinero en <b>{eficiente['Producto']}</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    # 6. EXPORTACIÓN
    st.sidebar.download_button(
        label="📥 Descargar Análisis para el Cliente",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='informe_consultoria_optimarket.csv',
        mime='text/csv',
    )
else:
    st.info("👋 Sube un archivo Excel para activar el Consultor Estratégico.")
