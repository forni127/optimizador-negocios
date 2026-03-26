import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import anthropic
import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

st.set_page_config(page_title="OptiMarket Pro | Panel de Control", layout="wide")

# ──────────────────────────────────────────────
# DETECCIÓN INTELIGENTE DE COLUMNAS
# ──────────────────────────────────────────────
COLUMN_PATTERNS = {
    "producto": [
        "PRODUCTO", "PROD", "FABRICANTE", "FAB", "ARTICULO", "ARTÍCULO",
        "ART", "ITEM", "NOMBRE", "DESCRIPCION", "DESCRIPCIÓN", "DESC",
        "REFERENCIA", "REF", "SKU", "MARCA", "CATEGORIA", "CATEGORÍA"
    ],
    "cantidad": [
        "CANTIDAD", "CANT", "UNIDADES", "UDS", "UD", "VENTAS", "VENTA",
        "VENDIDO", "VENDIDOS", "QTY", "QUANTITY", "UNITS", "VOLUMEN", "VOL"
    ],
    "importe": [
        "IMPORTE", "IMP", "TOTAL", "PRECIO", "PRICE", "INGRESOS", "INGRESO",
        "FACTURADO", "FACTURACION", "FACTURACIÓN", "REVENUE", "EUROS", "EUR",
        "MONTO", "VALOR", "VAL", "VENTA_TOTAL", "TOTAL_VENTA", "PVP"
    ],
    "tienda": [
        "TIENDA", "STORE", "LOCAL", "SUCURSAL", "DELEGACION", "DELEGACIÓN",
        "PUNTO", "SEDE", "ESTABLECIMIENTO", "COMERCIO", "UBICACION", "UBICACIÓN"
    ],
    "fecha": [
        "FECHA", "DATE", "DIA", "DÍA", "MES", "MES_AÑO", "PERIODO",
        "PERÍODO", "AÑO", "ANO", "YEAR", "MONTH", "TRIMESTRE"
    ],
    "coste": [
        "COSTE", "COSTO", "COST", "PRECIO_COSTE", "PRECIO_COMPRA",
        "COMPRA", "PVC", "MARGEN", "BENEFICIO"
    ]
}

def detectar_columna(columnas, tipo):
    """Detecta automáticamente la columna por tipo usando múltiples patrones."""
    patrones = COLUMN_PATTERNS.get(tipo, [])
    for col in columnas:
        col_upper = col.upper().strip()
        for patron in patrones:
            if patron in col_upper or col_upper in patron:
                return col
    return None

# ──────────────────────────────────────────────
# ANÁLISIS IA CON CLAUDE
# ──────────────────────────────────────────────
def analizar_con_ia(resumen_datos: dict) -> str:
    """Llama a la API de Claude para analizar los datos de ventas."""
    try:
        client = anthropic.Anthropic()
        
        prompt = f"""Eres un consultor experto en retail y optimización de tiendas. 
Analiza estos datos de ventas y proporciona un análisis estratégico en español.

DATOS:
- Tienda analizada: {resumen_datos.get('tienda', 'Todas')}
- Total productos únicos: {resumen_datos.get('total_productos', 0)}
- Volumen total vendido: {resumen_datos.get('volumen_total', 0):,.0f} unidades
- Ingresos totales: {resumen_datos.get('ingresos_totales', 0):,.2f} €
- Top 5 productos por ingresos: {json.dumps(resumen_datos.get('top5', []), ensure_ascii=False)}
- Bottom 5 productos (peor rendimiento): {json.dumps(resumen_datos.get('bottom5', []), ensure_ascii=False)}
- Producto líder: {resumen_datos.get('lider', 'N/A')}
- Producto que más dinero quita: {resumen_datos.get('peor', 'N/A')}

Proporciona:
1. **Diagnóstico rápido** (2-3 frases sobre el estado general)
2. **Oportunidades detectadas** (2-3 acciones concretas)
3. **Alertas** (1-2 riesgos o problemas detectados)
4. **Recomendación prioritaria** (la acción MÁS importante a tomar esta semana)

Sé directo, práctico y específico. Usa los nombres reales de los productos."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ No se pudo conectar con la IA: {str(e)}"

# ──────────────────────────────────────────────
# GENERACIÓN DE PDF CON REPORTLAB
# ──────────────────────────────────────────────
def generar_pdf(resumen_datos: dict, analisis_ia: str, df_tabla: pd.DataFrame) -> bytes:
    """Genera un informe PDF profesional."""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        'TituloCustom',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    estilo_subtitulo = ParagraphStyle(
        'SubtituloCustom',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4a4a8a'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    estilo_seccion = ParagraphStyle(
        'SeccionCustom',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=16,
        spaceAfter=8,
        borderPad=4
    )
    estilo_normal = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        leading=16
    )
    estilo_footer = ParagraphStyle(
        'FooterCustom',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )

    historia = []

    # ── CABECERA ──
    historia.append(Paragraph("OptiMarket Pro", estilo_titulo))
    historia.append(Paragraph("Informe Estratégico de Ventas", estilo_subtitulo))
    historia.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a4a8a')))
    historia.append(Spacer(1, 0.4*cm))
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    historia.append(Paragraph(f"Generado el {fecha_hoy}  |  Tienda: <b>{resumen_datos.get('tienda', 'Todas')}</b>", estilo_normal))
    historia.append(Spacer(1, 0.5*cm))

    # ── KPIs RESUMEN ──
    historia.append(Paragraph("Resumen Ejecutivo", estilo_seccion))
    
    datos_kpi = [
        ["Indicador", "Valor"],
        ["Total productos analizados", f"{resumen_datos.get('total_productos', 0)}"],
        ["Volumen total vendido", f"{resumen_datos.get('volumen_total', 0):,.0f} uds"],
        ["Ingresos totales", f"{resumen_datos.get('ingresos_totales', 0):,.2f} EUR"],
        ["Producto líder", str(resumen_datos.get('lider', 'N/A'))[:40]],
        ["Producto de menor rendimiento", str(resumen_datos.get('peor', 'N/A'))[:40]],
    ]
    
    tabla_kpi = Table(datos_kpi, colWidths=[9*cm, 8*cm])
    tabla_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f2f8'), colors.white]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    historia.append(tabla_kpi)
    historia.append(Spacer(1, 0.5*cm))

    # ── TABLA TOP 20 ──
    historia.append(Paragraph("Top 20 Productos por Rendimiento", estilo_seccion))
    
    if not df_tabla.empty:
        cols_mostrar = ['PROD_AUX', 'VENT_AUX', 'DIN_AUX']
        nombres_col = ['Producto', 'Unidades', 'Importe (EUR)']
        
        if 'MARGEN_AUX' in df_tabla.columns:
            cols_mostrar.append('MARGEN_AUX')
            nombres_col.append('Margen (%)')

        filas_tabla = [nombres_col]
        for _, row in df_tabla[cols_mostrar].head(20).iterrows():
            fila = [
                str(row['PROD_AUX'])[:35],
                f"{row['VENT_AUX']:,.0f}",
                f"{row['DIN_AUX']:,.2f}"
            ]
            if 'MARGEN_AUX' in df_tabla.columns:
                fila.append(f"{row['MARGEN_AUX']:.1f}%")
            filas_tabla.append(fila)

        ancho_cols = [9*cm, 3*cm, 4*cm]
        if 'MARGEN_AUX' in df_tabla.columns:
            ancho_cols = [7*cm, 3*cm, 3.5*cm, 3.5*cm]

        tabla_prod = Table(filas_tabla, colWidths=ancho_cols)
        tabla_prod.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7f7fb'), colors.white]),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('ROWHEIGHT', (0, 0), (-1, -1), 17),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Resaltar top 3
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#d4edda')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#e8f5e9')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f1f8e9')),
        ]))
        historia.append(tabla_prod)

    historia.append(Spacer(1, 0.5*cm))

    # ── ANÁLISIS IA ──
    historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    historia.append(Spacer(1, 0.3*cm))
    historia.append(Paragraph("Análisis Estratégico por Inteligencia Artificial", estilo_seccion))
    
    # Limpiar markdown del texto IA para ReportLab
    lineas_ia = analisis_ia.replace("**", "<b>").split("\n")
    for linea in lineas_ia:
        if linea.strip():
            # Cerrar tags bold correctamente
            linea_limpia = linea.strip()
            # Contar cuántos <b> hay para cerrarlos
            num_b = linea_limpia.count('<b>')
            if num_b % 2 != 0:
                linea_limpia += '</b>'
            try:
                historia.append(Paragraph(linea_limpia, estilo_normal))
            except Exception:
                historia.append(Paragraph(linea.strip().replace('<b>', '').replace('</b>', ''), estilo_normal))

    historia.append(Spacer(1, 0.8*cm))
    historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    historia.append(Spacer(1, 0.3*cm))
    historia.append(Paragraph("Informe generado por OptiMarket Pro · Powered by Claude AI", estilo_footer))

    doc.build(historia)
    buffer.seek(0)
    return buffer.getvalue()

# ──────────────────────────────────────────────
# APP PRINCIPAL
# ──────────────────────────────────────────────
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Acceso Privado")
    clave = st.text_input("Introduce tu clave:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")

else:
    # CSS personalizado
    st.markdown("""
    <style>
    .stMetric { background: #f0f2f8; border-radius: 10px; padding: 10px; }
    .ia-box { background: linear-gradient(135deg, #f0f2f8, #e8eaf6);
              border-left: 4px solid #4a4a8a; border-radius: 8px;
              padding: 20px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 OptiMarket Pro — Análisis Estratégico")

    archivo = st.sidebar.file_uploader("📁 1. Sube tu Excel o CSV", type=["xlsx", "csv", "xls"])

    if archivo:
        try:
            # ── LEER ARCHIVO ──
            if archivo.name.lower().endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python')
            else:
                df = pd.read_excel(archivo)

            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 2. Configuración de Columnas")

            # ── DETECCIÓN AUTOMÁTICA ──
            col_prod_auto    = detectar_columna(df.columns, "producto")
            col_vent_auto    = detectar_columna(df.columns, "cantidad")
            col_dinero_auto  = detectar_columna(df.columns, "importe")
            col_coste_auto   = detectar_columna(df.columns, "coste")
            col_tienda_auto  = detectar_columna(df.columns, "tienda")
            col_fecha_auto   = detectar_columna(df.columns, "fecha")

            # Mostrar estado de detección
            with st.sidebar.expander("🔍 Columnas detectadas automáticamente"):
                for nombre, val in [
                    ("Producto", col_prod_auto), ("Cantidad", col_vent_auto),
                    ("Importe", col_dinero_auto), ("Coste", col_coste_auto),
                    ("Tienda", col_tienda_auto), ("Fecha", col_fecha_auto)
                ]:
                    icono = "✅" if val else "❌"
                    st.write(f"{icono} **{nombre}:** {val or 'No encontrado'}")

            # Selectores manuales con valores por defecto detectados
            lista_cols = list(df.columns)
            
            idx_prod  = lista_cols.index(col_prod_auto)   if col_prod_auto   in lista_cols else 0
            idx_vent  = lista_cols.index(col_vent_auto)   if col_vent_auto   in lista_cols else 0
            idx_din   = lista_cols.index(col_dinero_auto) if col_dinero_auto in lista_cols else 0

            col_prod  = st.sidebar.selectbox("Columna Producto/Fabricante", lista_cols, index=idx_prod)
            col_vent  = st.sidebar.selectbox("Columna Cantidad Vendida",    lista_cols, index=idx_vent)
            col_dinero_sel = st.sidebar.selectbox(
                "Columna Importe/Ingresos (opcional)",
                ["— Sin importe —"] + lista_cols,
                index=([0] + lista_cols).index(col_dinero_auto) if col_dinero_auto in lista_cols else 0
            )
            col_dinero = col_dinero_sel if col_dinero_sel != "— Sin importe —" else None

            # Coste / Margen
            col_coste_sel = st.sidebar.selectbox(
                "Columna Coste (opcional, para margen)",
                ["— Sin coste —"] + lista_cols,
                index=([0] + lista_cols).index(col_coste_auto) if col_coste_auto in lista_cols else 0
            )
            col_coste = col_coste_sel if col_coste_sel != "— Sin coste —" else None

            # ── FILTRO TIENDA ──
            tienda_seleccionada = "TODAS"
            if col_tienda_auto:
                opciones = ["TODAS"] + sorted(df[col_tienda_auto].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("📍 Seleccionar Tienda:", opciones)

            # ── PROCESAMIENTO ──
            df_final = df.copy()

            if col_tienda_auto and tienda_seleccionada != "TODAS":
                df_final = df_final[df_final[col_tienda_auto] == tienda_seleccionada]

            df_final['PROD_AUX'] = df_final[col_prod].astype(str)
            df_final['VENT_AUX'] = pd.to_numeric(df_final[col_vent], errors='coerce').fillna(0)

            if col_dinero:
                df_final['DIN_AUX'] = pd.to_numeric(df_final[col_dinero], errors='coerce').fillna(0)
            else:
                df_final['DIN_AUX'] = df_final['VENT_AUX']

            if col_coste:
                df_final['COST_AUX'] = pd.to_numeric(df_final[col_coste], errors='coerce').fillna(0)

            # Agrupar
            agg_dict = {'VENT_AUX': 'sum', 'DIN_AUX': 'sum'}
            if col_coste:
                agg_dict['COST_AUX'] = 'sum'

            res = df_final.groupby('PROD_AUX').agg(agg_dict).reset_index()

            # Calcular margen si hay coste
            if col_coste and 'COST_AUX' in res.columns:
                res['MARGEN_AUX'] = ((res['DIN_AUX'] - res['COST_AUX']) / res['DIN_AUX'].replace(0, 1) * 100).round(1)

            res_sorted = res.sort_values('DIN_AUX', ascending=False)
            top20      = res_sorted.head(20)
            bottom5    = res_sorted.tail(5)

            if not top20.empty:
                # ── KPIs ──
                st.subheader(f"📍 Resultados: {tienda_seleccionada}")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("📦 VOLUMEN TOTAL", f"{res['VENT_AUX'].sum():,.0f} uds")
                with c2:
                    lbl = "💶 INGRESOS TOTALES" if col_dinero else "📊 TOTAL UNIDADES"
                    val = f"{res['DIN_AUX'].sum():,.2f} €" if col_dinero else f"{res['DIN_AUX'].sum():,.0f}"
                    st.metric(lbl, val)
                with c3:
                    st.metric("🏆 LÍDER", str(top20.iloc[0]['PROD_AUX'])[:18])
                with c4:
                    st.metric("⚠️ MENOR REND.", str(bottom5.iloc[0]['PROD_AUX'])[:18])

                st.divider()

                # ── GRÁFICA TOP 20 ──
                col_g1, col_g2 = st.columns([2, 1])
                with col_g1:
                    st.subheader(f"📈 Top 20: Rendimiento por {col_prod}")
                    fig = px.bar(
                        top20, x='PROD_AUX', y='DIN_AUX',
                        color='DIN_AUX',
                        color_continuous_scale='Blues',
                        text_auto='.2s',
                        labels={'PROD_AUX': col_prod, 'DIN_AUX': 'Rendimiento'}
                    )
                    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                with col_g2:
                    st.subheader("🔴 Peores 5 productos")
                    fig2 = px.bar(
                        bottom5.sort_values('DIN_AUX'),
                        x='DIN_AUX', y='PROD_AUX',
                        orientation='h',
                        color='DIN_AUX',
                        color_continuous_scale='Reds_r',
                        labels={'PROD_AUX': '', 'DIN_AUX': 'Rendimiento'}
                    )
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfica de margen si disponible
                if col_coste and 'MARGEN_AUX' in top20.columns:
                    st.subheader("💹 Margen por producto (Top 20)")
                    fig3 = px.bar(
                        top20.sort_values('MARGEN_AUX', ascending=False),
                        x='PROD_AUX', y='MARGEN_AUX',
                        color='MARGEN_AUX',
                        color_continuous_scale='RdYlGn',
                        text_auto='.1f',
                        labels={'PROD_AUX': col_prod, 'MARGEN_AUX': 'Margen (%)'}
                    )
                    fig3.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig3, use_container_width=True)

                # ── ANÁLISIS IA ──
                st.divider()
                st.subheader("🤖 Análisis IA")

                if st.button("✨ Generar análisis con IA", type="primary"):
                    with st.spinner("Claude está analizando tus datos..."):
                        resumen = {
                            "tienda": tienda_seleccionada,
                            "total_productos": len(res),
                            "volumen_total": float(res['VENT_AUX'].sum()),
                            "ingresos_totales": float(res['DIN_AUX'].sum()),
                            "lider": str(top20.iloc[0]['PROD_AUX']),
                            "peor": str(bottom5.iloc[0]['PROD_AUX']),
                            "top5": top20.head(5)[['PROD_AUX', 'DIN_AUX']].rename(
                                columns={'PROD_AUX': 'producto', 'DIN_AUX': 'importe'}
                            ).to_dict('records'),
                            "bottom5": bottom5[['PROD_AUX', 'DIN_AUX']].rename(
                                columns={'PROD_AUX': 'producto', 'DIN_AUX': 'importe'}
                            ).to_dict('records'),
                        }
                        st.session_state['analisis_ia'] = analizar_con_ia(resumen)
                        st.session_state['resumen_datos'] = resumen
                        st.session_state['df_top20'] = top20.copy()

                if 'analisis_ia' in st.session_state:
                    st.markdown(
                        f"<div class='ia-box'>{st.session_state['analisis_ia'].replace(chr(10), '<br>')}</div>",
                        unsafe_allow_html=True
                    )

                    # ── DESCARGAR PDF ──
                    st.divider()
                    st.subheader("📄 Exportar Informe")
                    if st.button("📥 Generar PDF profesional", type="secondary"):
                        with st.spinner("Generando informe PDF..."):
                            pdf_bytes = generar_pdf(
                                st.session_state['resumen_datos'],
                                st.session_state['analisis_ia'],
                                st.session_state['df_top20']
                            )
                            nombre_pdf = f"OptiMarket_Informe_{tienda_seleccionada}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                            st.download_button(
                                label="⬇️ Descargar informe PDF",
                                data=pdf_bytes,
                                file_name=nombre_pdf,
                                mime="application/pdf",
                                type="primary"
                            )

                # ── TABLA DETALLE ──
                with st.expander("🗂️ Ver tabla completa de datos"):
                    cols_show = ['PROD_AUX', 'VENT_AUX', 'DIN_AUX']
                    rename = {'PROD_AUX': col_prod, 'VENT_AUX': 'Unidades', 'DIN_AUX': 'Importe (€)'}
                    if col_coste and 'MARGEN_AUX' in res_sorted.columns:
                        cols_show.append('MARGEN_AUX')
                        rename['MARGEN_AUX'] = 'Margen (%)'
                    st.dataframe(res_sorted[cols_show].rename(columns=rename), use_container_width=True)

            else:
                st.warning("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.exception(e)

    else:
        st.info("📁 Por favor, sube un archivo Excel o CSV para empezar el análisis.")
