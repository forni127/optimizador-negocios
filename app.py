import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Curva Correcta", layout="wide")

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
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader(" 2. Ajuste de Columnas")
            
            # Buscamos columnas clave
            col_tienda_found = next((c for c in df.columns if 'TIENDA' in c), None)
            col_talla = next((c for c in df.columns if any(x in c for x in ['NUMERO', 'TALLA', 'SIZE'])), None)
            
            tienda_seleccionada = "TODAS"
            if col_tienda_found:
                opciones = ["TODAS"] + sorted(df[col_tienda_found].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox(" Seleccionar Tienda:", opciones)

            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            if col_prod and col_vent:
                df_final = df.copy()
                if col_tienda_found and tienda_seleccionada != "TODAS":
                    df_final = df_final[df_final[col_tienda_found] == tienda_seleccionada]

                df_final['PROD_AUX'] = df_final[col_prod]
                df_final['VENT_AUX'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)
                
                # --- LIMPIEZA CRÍTICA DE TALLAS ---
                if col_talla:
                    # Convertimos a número para que el orden sea 37, 38, 39... y no 37, 40, 38
                    df_final[col_talla] = pd.to_numeric(df_final[col_talla], errors='coerce')

                # Gráfica Principal
                res = df_final.groupby('PROD_AUX').agg({'VENT_AUX':'sum'}).reset_index()
                res = res.sort_values('VENT_AUX', ascending=False).head(20)

                st.subheader(f" Top 20 Fabricantes ({tienda_seleccionada})")
                fig = px.bar(res, x='PROD_AUX', y='VENT_AUX', color='VENT_AUX', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)

                # --- SECCIÓN CURVA DE TALLAS CORREGIDA ---
                if col_talla:
                    st.divider()
                    st.subheader("👟 Curva de Tallas Optimizada")
                    fab_detalle = st.selectbox("Elige fabricante para ver su curva real:", sorted(df_final['PROD_AUX'].unique()))
                    
                    if fab_detalle:
                        df_tallas = df_final[df_final['PROD_AUX'] == fab_detalle].copy()
                        # Agrupar y asegurar que la talla es un número para el eje X
                        res_tallas = df_tallas.groupby(col_talla)['VENT_AUX'].sum().reset_index()
                        res_tallas.columns = ['Talla', 'Ventas']
                        
                        # ORDENAR NUMÉRICAMENTE
                        res_tallas = res_tallas.sort_values('Talla')
                        
                        fig_tallas = px.bar(res_tallas, x='Talla', y='Ventas', 
                                            text_auto=True,
                                            color='Ventas', color_continuous_scale='Viridis',
                                            labels={'Talla': 'Número de Pie', 'Ventas': 'Pares Vendidos'})
                        
                        # Forzar que el eje X trate los números como etiquetas ordenadas
                        fig_tallas.update_xaxes(type='category')
                        st.plotly_chart(fig_tallas, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info(" Sube un archivo para ver la curva de tallas corregida.")
