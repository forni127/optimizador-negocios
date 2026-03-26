import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Panel de Control", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Introduce tu clave:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave incorrecta")
else:
    st.title("📊 Análisis Estratégico de Ventas")
    
    archivo = st.sidebar.file_uploader("📂 1. Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # LEER ARCHIVO
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            # Limpiar nombres de columnas (Quitar espacios y poner mayúsculas)
            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 2. Ajuste de Columnas")
            st.sidebar.info("Selecciona qué columna es cada cosa para activar la IA:")
            
            # Selectores manuales
            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            # PROCESAMIENTO
            if col_prod and col_vent:
                df_final = df.copy()
                df_final['Producto'] = df_final[col_prod]
                df_final['Ventas'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

                # Intentar buscar Precio e Importe para calcular dinero
                # Buscamos columnas que contengan 'IMP' o 'TOTAL' o 'PREC'
                col_dinero = next((c for c in df.columns if 'IMP' in c or 'TOTAL' in c or 'PREC' in c), None)
                
                if col_dinero:
                    df_final['Dinero'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
                else:
                    df_final['Dinero'] = df_final['Ventas']

                # Agrupar por producto
                res = df_final.groupby('Producto').agg({'Ventas':'sum', 'Dinero':'sum'}).reset_index()
                res = res.sort_values('Dinero', ascending=False).head(20)

                # --- DASHBOARD ---
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("📦 VOLUMEN TOTAL", f"{res['Ventas'].sum():,.0f} uds")
                with c2:
                    etiqueta = "INGRESOS TOTALES" if col_dinero else "TOTAL UNIDADES"
                    st.metric(f"💰 {etiqueta}", f"{res['Dinero'].sum():,.2f} €" if col_dinero else f"{res['Dinero'].sum():,.0f}")
                with c3:
                    st.metric("🏆 LÍDER", str(res.iloc[0]['Producto'])[:15])

                st.divider()
                
                # Gráfica Pro
                st.subheader(f"📈 Top 20: Rendimiento por {col_prod}")
                fig = px.bar(res, x='Producto', y='Dinero', 
                             color='Dinero', 
                             color_continuous_scale='Blues',
                             text_auto='.2s',
                             labels={'Producto': col_prod, 'Dinero': 'Rendimiento'})
                
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

                # Diagnóstico IA
                st.info(f"🧠 **Consejo de la IA:** Tu principal motor de ventas es **{res.iloc[0]['Producto']}**. Concentra tus esfuerzos de marketing aquí para maximizar el retorno.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("👋 Por favor, sube un archivo para empezar el análisis.")
