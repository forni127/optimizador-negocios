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

            # Limpiar nombres de columnas
            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader(" 2. Ajuste de Columnas")
            
            # --- FILTRO DE TIENDA ---
            col_tienda_found = next((c for c in df.columns if 'TIENDA' in c), None)
            tienda_seleccionada = "TODAS"
            
            if col_tienda_found:
                opciones = ["TODAS"] + sorted(df[col_tienda_found].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox(" Seleccionar Tienda:", opciones)

            # --- SELECTOR DE TALLAS (Detectar columna NUMERO) ---
            col_talla = next((c for c in df.columns if any(x in c for x in ['NUMERO', 'TALLA', 'SIZE'])), None)

            # Selectores manuales
            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            # PROCESAMIENTO
            if col_prod and col_vent:
                df_final = df.copy()
                
                if col_tienda_found and tienda_seleccionada != "TODAS":
                    df_final = df_final[df_final[col_tienda_found] == tienda_seleccionada]

                df_final['PROD_AUX'] = df_final[col_prod]
                df_final['VENT_AUX'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

                col_dinero = next((c for c in df.columns if any(x in c for x in ['IMP', 'TOTAL', 'PREC'])), None)
                if col_dinero:
                    df_final['DIN_AUX'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
                else:
                    df_final['DIN_AUX'] = df_final['VENT_AUX']

                # Agrupar para el ranking general
                res = df_final.groupby('PROD_AUX').agg({'VENT_AUX':'sum', 'DIN_AUX':'sum'}).reset_index()
                res = res.sort_values('DIN_AUX', ascending=False).head(20)

                if not res.empty:
                    # --- DASHBOARD ---
                    st.subheader(f" Resultados: {tienda_seleccionada}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric(" VOLUMEN TOTAL", f"{res['VENT_AUX'].sum():,.0f} uds")
                    with c2:
                        etiqueta = "INGRESOS TOTALES" if col_dinero else "TOTAL UNIDADES"
                        st.metric(f" {etiqueta}", f"{res['DIN_AUX'].sum():,.2f} €" if col_dinero else f"{res['DIN_AUX'].sum():,.0f}")
                    with c3:
                        st.metric(" LÍDER", str(res.iloc[0]['PROD_AUX'])[:15])

                    st.divider()
                    
                    # Gráfica Principal
                    st.subheader(f" Top 20: Rendimiento por {col_prod}")
                    fig = px.bar(res, x='PROD_AUX', y='DIN_AUX', color='DIN_AUX', color_continuous_scale='Blues', text_auto='.2s')
                    st.plotly_chart(fig, use_container_width=True)

                    # --- NUEVA SECCIÓN: CURVA DE TALLAS ---
                    if col_talla:
                        st.divider()
                        st.subheader("👟 Análisis de Curva de Tallas")
                        # Selector para elegir qué fabricante analizar detalladamente
                        fab_detalle = st.selectbox("Selecciona un fabricante para ver su curva de tallas:", res['PROD_AUX'].unique())
                        
                        if fab_detalle:
                            df_tallas = df_final[df_final['PROD_AUX'] == fab_detalle]
                            # Agrupar por el número de pie
                            res_tallas = df_tallas.groupby(col_talla)['VENT_AUX'].sum().reset_index()
                            res_tallas.columns = ['Talla', 'Ventas']
                            # Ordenar por número de pie (36, 37, 38...)
                            res_tallas = res_tallas.sort_values('Talla')
                            
                            fig_tallas = px.bar(res_tallas, x='Talla', y='Ventas', 
                                                title=f"Unidades vendidas por Talla - {fab_detalle}",
                                                text_auto=True, color='Ventas', color_continuous_scale='Reds')
                            st.plotly_chart(fig_tallas, use_container_width=True)

                else:
                    st.warning("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info(" Por favor, sube un archivo para empezar el análisis.")
