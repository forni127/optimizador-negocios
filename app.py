import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Análisis Tallas", layout="wide")

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
    st.title(" Análisis de Ventas por Fabricante y Talla")
    
    archivo = st.sidebar.file_uploader(" 1. Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader(" 2. Configuración")
            
            # Buscamos columnas clave
            col_talla_found = next((c for c in df.columns if any(x in c for x in ['NUMERO', 'TALLA', 'SIZE'])), None)
            col_tienda_found = next((c for c in df.columns if 'TIENDA' in c), None)
            
            # Selectores de Producto y Ventas
            col_prod = st.sidebar.selectbox("¿Qué columna es el Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad?", df.columns)

            # --- FILTROS ---
            tienda_sel = "TODAS"
            if col_tienda_found:
                tienda_sel = st.sidebar.selectbox("📍 Tienda:", ["TODAS"] + sorted(df[col_tienda_found].dropna().unique().tolist()))

            # --- PROCESAMIENTO ---
            df_final = df.copy()
            if col_tienda_found and tienda_sel != "TODAS":
                df_final = df_final[df_final[col_tienda_found] == tienda_sel]

            df_final['PROD_AUX'] = df_final[col_prod]
            df_final['VENT_AUX'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

            # --- NUEVO: SELECTOR DE FABRICANTE PARA VER TALLAS ---
            st.subheader(f"🕵️ Explorador de Tallas")
            fabricante_sel = st.selectbox("Selecciona un Fabricante para ver sus tallas más vendidas:", 
                                         sorted(df_final['PROD_AUX'].unique().tolist()))

            if fabricante_sel and col_talla_found:
                # Filtramos por el fabricante elegido
                df_tallas = df_final[df_final['PROD_AUX'] == fabricante_sel]
                
                # Agrupamos por número de pie
                res_tallas = df_tallas.groupby(col_talla_found)['VENT_AUX'].sum().reset_index()
                res_tallas.columns = ['Talla', 'Vendidas']
                res_tallas = res_tallas.sort_values('Talla') # Ordenamos por número de pie

                # Gráfica de Tallas
                fig_tallas = px.bar(res_tallas, x='Talla', y='Vendidas', 
                                   title=f"Curva de Tallas vendidas de: {fabricante_sel}",
                                   color='Vendidas', color_continuous_scale='Reds',
                                   text_auto=True)
                st.plotly_chart(fig_tallas, use_container_width=True)
            
            st.divider()

            # --- RANKING GENERAL (Tu gráfica de siempre) ---
            st.subheader(f"📊 Ranking General de Fabricantes ({tienda_sel})")
            res_gen = df_final.groupby('PROD_AUX')['VENT_AUX'].sum().reset_index().sort_values('VENT_AUX', ascending=False).head(15)
            
            fig_gen = px.bar(res_gen, x='PROD_AUX', y='VENT_AUX', color='VENT_AUX', color_continuous_scale='Blues')
            st.plotly_chart(fig_gen, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info(" Sube el Excel para analizar las tallas.")
