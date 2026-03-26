import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OptiMarket Pro | Definitivo", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Sistema")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Incorrecta")
else:
    st.title("📊 Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("📂 Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # 1. LEER EL ARCHIVO
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            # 2. LIMPIEZA DE COLUMNAS (Quitar espacios y poner mayúsculas)
            df.columns = [str(c).strip().upper() for c in df.columns]

            # 3. SELECTORES MANUALES (Para que no falle nunca)
            st.sidebar.subheader("⚙️ Configuración de Columnas")
            st.sidebar.write("Si no ves datos, selecciona las columnas correctas aquí:")
            
            # Buscamos si hay alguna que se parezca a Producto o Ventas para ponerla por defecto
            idx_prod = 0
            idx_vent = 0
            for i, col in enumerate(df.columns):
                if any(x in col for x in ['PROD', 'FABRI', 'REF', 'MOD']): idx_prod = i
                if any(x in col for x in ['CANT', 'VEND', 'VENT']): idx_vent = i

            col_producto = st.sidebar.selectbox("Columna de Producto/Fabricante:", df.columns, index=idx_prod)
            col_ventas = st.sidebar.selectbox("Columna de Unidades/Ventas:", df.columns, index=idx_vent)

            # 4. PROCESAMIENTO
            if col_producto and col_ventas:
                # Copiamos los datos a nombres fijos para el resto del código
                df_final = df.copy()
                df_final['Producto'] = df_final[col_producto]
                df_final['Ventas'] = pd.to_numeric(df_final[col_ventas], errors='coerce').fillna(0)

                # Intentamos buscar precio y coste de forma automática
                for col in df.columns:
                    if 'PREC' in col or 'IMP' in col: df_final['Precio'] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    if 'COST' in col: df_final['Coste'] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                # Cálculos
                if 'Precio' in df_final.columns and 'Coste' in df_final.columns:
                    df_final['Beneficio'] = (df_final['Precio'] - df_final['Coste']) * df_final['Ventas']
                else:
                    df_final['Beneficio'] = df_final['Ventas']

                # Resumen
                res = df_final.groupby('Producto').agg({'Ventas':'sum', 'Beneficio':'sum'}).reset_index()
                res = res.sort_values('Beneficio', ascending=False)

                # --- DASHBOARD ---
                c1, c2 = st.columns(2)
                c1.metric("📦 TOTAL UNIDADES", f"{res['Ventas'].sum():,.0f}")
                c2.metric("🏆 PRODUCTO LÍDER", str(res.iloc[0]['Producto'])[:20])

                st.subheader("Gráfica de Rendimiento")
                fig = px.bar(res.head(15), x='Producto', y='Beneficio', color='Beneficio', color_continuous_scale='Turbo')
                st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"Analizando columna: {col_producto} como producto y {col_ventas} como ventas.")
            
        except Exception as e:
            st.error(f"Error al procesar: {e}")
            st.write("Prueba a subir el archivo de nuevo o comprueba que no esté abierto en tu ordenador.")
    else:
        st.info("👋 Sube un archivo en el panel izquierdo para empezar.")
