import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Optimizador Pro", layout="wide")

st.title("📊 Panel de Optimización de Recursos")
st.markdown("""
Esta herramienta analiza tus ventas y te dice exactamente dónde priorizar tu inversión 
para maximizar el beneficio mensual.
""")

# 2. CARGA DE DATOS
st.sidebar.header("Configuración")
archivo = st.sidebar.file_uploader("Sube tu Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip() # Limpieza automática
    
    # CÁLCULOS
    df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad'] = df['Margen'] * df['Ventas_Mes_Unidades']
    
    # 3. MÉTRICAS RESUMEN
    col1, col2, col3 = st.columns(3)
    total_beneficio = df['Rentabilidad'].sum()
    producto_top = df.sort_values('Rentabilidad', ascending=False).iloc[0]['Producto']
    
    col1.metric("Beneficio Total", f"{total_beneficio:,.2f}€")
    col2.metric("Producto Estrella", producto_top)
    col3.metric("Productos Analizados", len(df))

    # 4. GRÁFICA INTERACTIVA
    st.subheader("Análisis Visual de Rentabilidad")
    fig = px.bar(df, x='Producto', y='Rentabilidad', color='Rentabilidad',
                 text_auto='.2s', title="Efectivo generado por cada producto")
    st.plotly_chart(fig, use_container_width=True)

    # 5. BOTÓN DE DESCARGA
    st.download_button(
        label="Descargar Informe Optimizado",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='plan_optimizacion.csv',
        mime='text/csv',
    )
else:
    st.info("👋 Por favor, sube un archivo Excel en la barra lateral para comenzar.")
    # --- EL CEREBRO DE LA IA (Consultoría Automática) ---
st.header("💡 Recomendaciones del Consultor IA")

# 1. Encontrar el Producto Estrella (Más beneficio total)
estrella = df.sort_values('Rentabilidad', ascending=False).iloc[0]

# 2. Encontrar el Producto con mejor ROI (Eficiencia del dinero)
df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
mejor_roi = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]

# 3. Encontrar productos con bajas ventas pero mucho margen (Oportunidades)
oportunidad = df[(df['Margen'] > df['Margen'].median()) & (df['Ventas_Mes_Unidades'] < df['Ventas_Mes_Unidades'].median())]

# MOSTRAR LOS INSIGHTS EN LA WEB
col_a, col_b = st.columns(2)

with col_a:
    st.success(f"🌟 **Producto Estrella:** {estrella['Producto']}")
    st.write(f"Este producto te ha generado **{estrella['Rentabilidad']:.2f}€**. Es tu motor principal, ¡asegúrate de tener siempre stock!")

with col_b:
    st.info(f"📈 **Mejor Inversión (ROI):** {mejor_roi['Producto']}")
    st.write(f"Ganas un **{mejor_roi['ROI_Porcentaje']:.0f}%** por cada euro invertido. Es extremadamente eficiente.")

if not oportunidad.empty:
    st.warning(f"🔍 **Oportunidad Oculta:** {oportunidad.iloc[0]['Producto']}")
    st.write("Tiene un margen muy alto pero se vende poco. ¿Has probado a hacerle más publicidad?")
