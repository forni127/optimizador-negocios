import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 🛠️ DICCIONARIO MAESTRO DE SINÓNIMOS
# =========================================================
# Si un cliente usa un nombre raro, añádelo aquí
S_PROD = ['PRODUCTO', 'FABRICANTE', 'REFERENC', 'MODELO', 'ARTICULO', 'ITEM', 'REF']
S_VENT = ['CANTIDAD', 'VENDIDO', 'UNIDADES', 'VENTAS', 'CANT', 'TOTAL_VENTAS']
S_COST = ['COSTE', 'COSTO', 'COMPRA', 'PRECIO_COMPRA', 'P_COMPRA']
S_PREC = ['PRECIO', 'IMPORTE', 'VENTA', 'PVP', 'VALOR', 'P_VENTA']

st.set_page_config(page_title="OptiMarket Pro | Global", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Sistema")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Clave Incorrecta")
else:
    st.title("📊 Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("📂 Sube tu archivo (Excel o CSV)", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # 1. LEER ARCHIVO SEGÚN FORMATO
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            # 2. LIMPIEZA DE FILAS VACÍAS AL PRINCIPIO
            # Si la cabecera real no está en la fila 1, la buscamos
            if df.columns.str.contains('Unnamed').sum() > (len(df.columns) / 2):
                # Buscamos la fila que contenga alguna de nuestras palabras clave
                for i in range(len(df.head(10))):
                    fila_test = df.iloc[i].astype(str).str.upper().tolist()
                    if any(word in " ".join(fila_test) for word in S_PROD):
                        if archivo.name.lower().endswith('.csv'):
                            archivo.seek(0)
                            df = pd.read_csv(archivo, skiprows=i+1, sep=None, engine='python')
                        else:
                            df = pd.read_excel(archivo, skiprows=i+1)
                        break

            # 3. NORMALIZAR COLUMNAS
            df.columns = [str(c).strip().upper() for c in df.columns]

            # 4. MAPEO INTELIGENTE
            mapeo = {}
            for col in df.columns:
                if any(x in col for x in S_PROD): mapeo[col] = 'Producto'
                elif any(x in col for x in S_VENT): mapeo[col] = 'Ventas'
                elif any(x in col for x in S_COST): mapeo[col] = 'Coste'
                elif any(x in col for x in S_PREC): mapeo[col] = 'Precio'

            df = df.rename(columns=mapeo)

            # 5. VALIDACIÓN Y CÁLCULOS
            if 'Producto' in df.columns and 'Ventas' in df.columns:
                # Convertir a números
                for c in ['Ventas', 'Coste', 'Precio']:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

                # Cálculo de beneficio si hay datos
                if 'Precio' in df.columns and 'Coste' in df.columns:
                    df['Beneficio'] = (df['Precio'] - df['Coste']) * df['Ventas']
                else:
                    df['Beneficio'] = df['Ventas']

                # Agrupación Final
                resumen = df.groupby('Producto').agg({'Ventas':'sum', 'Beneficio':'sum'}).reset_index()
                resumen = resumen.sort_values('Beneficio', ascending=False)

                # --- DASHBOARD ---
                k1, k2, k3 = st.columns(3)
                k1.metric("📦 TOTAL UNIDADES", f"{resumen['Ventas'].sum():,.0f}")
                k2.metric("💰 RENTABILIDAD", f"{resumen['Beneficio'].sum():,.2f} €")
                k3.metric("🏆 TOP VENTAS", str(resumen.iloc[0]['Producto'])[:15])

                st.subheader("Análisis de Rendimiento")
                fig = px.bar(resumen.head(15), x='Producto', y='Beneficio', color='Beneficio',
                             color_continuous_scale='Turbo', labels={'Beneficio': 'Ganancia/Unidades'})
                st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"✅ Detectado correctamente como: {list(mapeo.values())}")
            else:
                st.error("❌ No he podido identificar las columnas.")
                st.info("Asegúrate de que tu Excel tenga títulos como: Fabricante, Cantidad, Precio...")
                st.write("Columnas detectadas actualmente:", list(df.columns))

        except Exception as e:
            st.error(f"Error técnico al procesar: {e}")
    else:
        st.info("👋 Sube un archivo para analizar los datos de cualquier cliente.")
