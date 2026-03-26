import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 🛠️ SINÓNIMOS INTELIGENTES (Añade aquí si un cliente usa nombres raros)
# =========================================================
SINONIMOS_PRODUCTO = ['FABRICANTE', 'PRODUCTO', 'REFERENC.', 'MODELO', 'ARTICULO']
SINONIMOS_VENTAS   = ['CANTIDAD', 'VENDIDO', 'UNIDADES', 'VENTAS', 'CANT']
SINONIMOS_COSTE    = ['COSTE', 'COSTO', 'COMPRA', 'PRECIO_COMPRA']
SINONIMOS_PRECIO   = ['PRECIO', 'IMPORTE', 'VENTA', 'PVP', 'VALOR']

st.set_page_config(page_title="OptiMarket Pro", layout="wide")

# --- SEGURIDAD ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso Clientes")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Incorrecta")
else:
    st.title("📊 Inteligencia de Negocio")
    archivo = st.sidebar.file_uploader("📂 Sube tu archivo (Excel o CSV)", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # --- BLOQUE DETECTOR DE FORMATO (Aquí estaba el fallo) ---
            nombre_archivo = archivo.name.lower()
            
            if nombre_archivo.endswith('.csv'):
                # Si es CSV, probamos con coma o punto y coma
                try:
                    df_raw = pd.read_csv(archivo, sep=None, engine='python')
                except:
                    df_raw = pd.read_csv(archivo, sep=',', encoding='utf-8')
            else:
                # Si es Excel (.xlsx o .xls)
                df_raw = pd.read_excel(archivo)

            # --- DETECCIÓN DE FILA DE CABECERA ---
            # Si la primera fila está vacía (como en tu excel de zapatos), saltamos una
            if df_raw.columns.str.contains('Unnamed').sum() > (len(df_raw.columns) / 2):
                if nombre_archivo.endswith('.csv'):
                    archivo.seek(0)
                    df = pd.read_csv(archivo, skiprows=1, sep=None, engine='python')
                else:
                    df = pd.read_excel(archivo, skiprows=1)
            else:
                df = df_raw

            # --- LIMPIEZA Y MAPEO ---
            df.columns = [str(c).strip().upper() for c in df.columns]
            mapeo = {}
            for col in df.columns:
                if any(x in col for x in SINONIMOS_PRODUCTO): mapeo[col] = 'Producto'
                elif any(x in col for x in SINONIMOS_VENTAS): mapeo[col] = 'Ventas'
                elif any(x in col for x in SINONIMOS_COSTE): mapeo[col] = 'Coste'
                elif any(x in col for x in SINONIMOS_PRECIO): mapeo[col] = 'Precio'

            df = df.rename(columns=mapeo)

            # --- ANÁLISIS ---
            if 'Producto' in df.columns and 'Ventas' in df.columns:
                for c in ['Ventas', 'Coste', 'Precio']:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

                # Si tenemos dinero, calculamos beneficio
                if 'Precio' in df.columns and 'Coste' in df.columns:
                    df['Beneficio'] = (df['Precio'] - df['Coste']) * df['Ventas']
                else:
                    df['Beneficio'] = df['Ventas']

                res = df.groupby('Producto').agg({'Ventas':'sum', 'Beneficio':'sum'}).reset_index()
                res = res.sort_values('Beneficio', ascending=False)

                # --- DASHBOARD ---
                c1, c2, c3 = st.columns(3)
                c1.metric("VENTAS TOTALES", f"{res['Ventas'].sum():,.0f}")
                c2.metric("BENEFICIO TOTAL", f"{res['Beneficio'].sum():,.2f} €")
                c3.metric("TOP PRODUCTO", str(res.iloc[0]['Producto'])[:15])

                fig = px.bar(res.head(15), x='Producto', y='Beneficio', color='Beneficio', 
                             color_continuous_scale='Greens', title="Rentabilidad por Fabricante/Producto")
                st.plotly_chart(fig, use_container_width=True)
                
                st.success("✅ ¡Archivo procesado con éxito! He identificado las columnas automáticamente.")
            else:
                st.warning("⚠️ No encuentro las columnas clave. Revisa los nombres en el Excel.")
                st.write("Columnas detectadas:", list(df.columns))

        except Exception as e:
            st.error(f"Hubo un error al leer el archivo: {e}")
    else:
        st.info("👋 Por favor, sube un archivo Excel o CSV para analizar.")
