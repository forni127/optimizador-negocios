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
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 2. Configuración")
            
            # --- NUEVA FUNCIÓN: FILTRO DE TIENDA ---
            col_tienda = next((c for c in df.columns if 'TIENDA' in c), None)
            tienda_seleccionada = "TODAS"
            
            if col_tienda:
                opciones_tienda = ["TODAS"] + sorted(df[col_tienda].unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("Seleccionar Tienda:", opciones_tienda)

            col_prod = st.sidebar.selectbox("¿Qué columna es el Producto/Fabricante?", df.columns)
            col_vent = st.sidebar.selectbox("¿Qué columna es la Cantidad Vendida?", df.columns)

            if col_prod and col_vent:
                df_final = df.copy()
                
                # Aplicar filtro de tienda si no es "TODAS"
                if tienda_seleccionada != "TODAS":
                    df_final = df_final[df_final[col_tienda] == tienda_seleccionada]

                df_final['Producto'] = df_final[col_prod]
                df_final['Ventas'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

                col_dinero = next((c for c in df.columns if any(x in c for x in ['IMP', 'TOTAL', 'PREC'])), None)
                if col_dinero:
                    df_final['Dinero'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
                else:
                    df_final['Dinero'] = df_final['Ventas']

                # --- GRÁFICA POR TIENDA (Si quieres ver quién vende más en total) ---
                if tienda_seleccionada == "TODAS" and col_tienda:
                    st.subheader("🏢 Comparativa de Ventas por Tienda")
                    ventas_tienda = df_final.groupby(col_tienda)['Dinero'].sum().reset_index().sort_values('Dinero', ascending=False)
                    fig_tiendas = px.bar(ventas_tienda, x=col_tienda, y='Dinero', color='Dinero', color_continuous_scale='Greens')
                    st.plotly_chart(fig_tiendas, use_container_width=True)
                    st.divider()

                # --- ANÁLISIS POR PRODUCTO ---
                res = df_final.groupby('Producto').agg({'Ventas':'sum', 'Dinero':'sum'}).reset_index()
                res = res.sort_values('Dinero', ascending=False).head(20)

                st.subheader(f"🔝 Top 20 en {tienda_seleccionada}")
                c1, c2, c3 = st.columns(3)
                c1.metric("📦 VOLUMEN", f"{res['Ventas'].sum():,.0f} uds")
                c2.metric("💰 INGRESOS", f"{res['Dinero'].sum():,.2f} €")
                c3.metric("🏆 LÍDER", str(res.iloc[0]['Producto'])[:15])

                fig = px.bar(res, x='Producto', y='Dinero', color='Dinero', color_continuous_scale='Blues', text_auto='.2s')
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("👋 Sube un archivo para ver los datos por tienda.")
