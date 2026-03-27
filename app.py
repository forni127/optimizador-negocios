import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Panel de Control", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title(" Acceso Privado")
    clave = st.text_input("Introduce tu clave:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave incorrecta")
else:
    st.title(" Análisis Estratégico de Ventas")
   
    archivo = st.sidebar.file_uploader(" 1. Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

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
            st.sidebar.subheader(" 2. Ajuste de Columnas")
           
            # --- FILTRO DE TIENDA (Añadido) ---
            col_tienda_found = next((c for c in df.columns if 'TIENDA' in c), None)
            tienda_seleccionada = "TODAS"
           
            if col_tienda_found:
                opciones = ["TODAS"] + sorted(df[col_tienda_found].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("📍 Seleccionar Tienda:", opciones)

            # Selectores manuales
            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            # PROCESAMIENTO
            if col_prod and col_vent:
                df_final = df.copy()
               
                # Aplicar filtro de tienda si existe
                if col_tienda_found and tienda_seleccionada != "TODAS":
                    df_final = df_final[df_final[col_tienda_found] == tienda_seleccionada]

                # Crear columnas de trabajo seguras
                df_final['PROD_AUX'] = df_final[col_prod]
                df_final['VENT_AUX'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

                # Buscar columna de dinero
                col_dinero = next((c for c in df.columns if any(x in c for x in ['IMP', 'TOTAL', 'PREC'])), None)
               
                if col_dinero:
                    df_final['DIN_AUX'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
                else:
                    df_final['DIN_AUX'] = df_final['VENT_AUX']

                # Agrupar por producto
                res = df_final.groupby('PROD_AUX').agg({'VENT_AUX':'sum', 'DIN_AUX':'sum'}).reset_index()
                res = res.sort_values('DIN_AUX', ascending=False).head(20)

                if not res.empty:
                    # --- DASHBOARD ---
                    st.subheader(f"📍 Resultados: {tienda_seleccionada}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric(" VOLUMEN TOTAL", f"{res['VENT_AUX'].sum():,.0f} uds")
                    with c2:
                        etiqueta = "INGRESOS TOTALES" if col_dinero else "TOTAL UNIDADES"
                        st.metric(f" {etiqueta}", f"{res['DIN_AUX'].sum():,.2f} €" if col_dinero else f"{res['DIN_AUX'].sum():,.0f}")
                    with c3:
                        st.metric(" LÍDER", str(res.iloc[0]['PROD_AUX'])[:15])

                    st.divider()
                   
                    # Gráfica Pro
                    st.subheader(f" Top 20: Rendimiento por {col_prod}")
                    fig = px.bar(res, x='PROD_AUX', y='DIN_AUX',
                                 color='DIN_AUX',
                                 color_continuous_scale='Blues',
                                 text_auto='.2s',
                                 labels={'PROD_AUX': col_prod, 'DIN_AUX': 'Rendimiento'})
                   
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)

                    # Diagnóstico IA
                    st.info(f" **Consejo de la IA:** En {tienda_seleccionada}, tu principal motor es **{res.iloc[0]['PROD_AUX']}**.")
                else:
                    st.warning("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info(" Por favor, sube un archivo para empezar el análisis.")
