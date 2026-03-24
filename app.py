import streamlit as st
import pandas as pd
import plotly.express as px

# 1. IDENTIDAD VISUAL Y MARCA
st.set_page_config(
    page_title="OptiMarket Pro | Consultor de Inventario",
    page_icon="🚀",
    layout="wide"
)

# Estilo para que se vea más profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 OptiMarket Pro")
st.subheader("Análisis Inteligente para Maximizar tus Beneficios")
st.divider()

# 2. CARGA DE DATOS EN BARRA LATERAL
st.sidebar.header("📂 Panel de Control")
archivo = st.sidebar.file_uploader("Sube tu Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip() # Limpiar nombres de columnas
    
    # CÁLCULOS CLAVE
    df['Margen'] = df['Precio_Venta'] - df['Coste_Unidad']
    df['Rentabilidad_Total'] = df['Margen'] * df['Ventas_Mes_Unidades']
    df['ROI_Porcentaje'] = (df['Margen'] / df['Coste_Unidad']) * 100
    
    # 3. MÉTRICAS RESUMEN (Tarjetas visuales)
    col1, col2, col3 = st.columns(3)
    beneficio_total = df['Rentabilidad_Total'].sum()
    mejor_prod = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]['Producto']
    roi_medio = df['ROI_Porcentaje'].mean()
    
    col1.metric("Beneficio Total Mes", f"{beneficio_total:,.2f} €")
    col2.metric("Producto Estrella", mejor_prod)
    col3.metric("ROI Medio del Stock", f"{roi_medio:.1f} %")

    # 4. GRÁFICA DE RENTABILIDAD
    st.subheader("📊 Radiografía de tus Ganancias")
    fig = px.bar(df, x='Producto', y='Rentabilidad_Total', 
                 color='Rentabilidad_Total', text_auto='.2s',
                 title="Euros netos generados por cada producto")
    st.plotly_chart(fig, use_container_width=True)

    # 5. EL CEREBRO DE LA IA (Consultoría Automática)
    st.divider()
    st.header("💡 Recomendaciones del Consultor IA")
    
    estrella = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
    mejor_eficiencia = df.sort_values('ROI_Porcentaje', ascending=False).iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"🌟 **Prioridad de Venta:** {estrella['Producto']}")
        st.write(f"Es tu mayor fuente de ingresos (**{estrella['Rentabilidad_Total']:.2f}€**). No permitas que se agote el stock.")
    with c2:
        st.info(f"📈 **Eficiencia Máxima:** {mejor_eficiencia['Producto']}")
        st.write(f"Este producto te da un **{mejor_eficiencia['ROI_Porcentaje']:.0f}%** de retorno. Invertir 1€ aquí es tu mejor jugada.")

    # 6. BOTÓN DE DESCARGA PARA EL CLIENTE
    st.sidebar.download_button(
        label="📥 Descargar Informe PDF/CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='analisis_optmarket.csv',
        mime='text/csv',
    )
else:
    st.info("👋 Bienvenido a OptiMarket. Por favor, sube tu archivo Excel en la izquierda para empezar el análisis.")
