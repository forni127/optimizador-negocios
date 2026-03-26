import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

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
    patrones = COLUMN_PATTERNS.get(tipo, [])
    for col in columnas:
        col_upper = col.upper().strip()
        for patron in patrones:
            if patron in col_upper or col_upper in patron:
                return col
    return None

# ──────────────────────────────────────────────
# ANÁLISIS AUTOMÁTICO SIN API — LÓGICA PYTHON
# ──────────────────────────────────────────────
def analizar_automatico(res, tienda, tiene_dinero, tiene_margen):
    total_prods  = len(res)
    total_uds    = res['VENT_AUX'].sum()
    total_din    = res['DIN_AUX'].sum()
    top1         = res.iloc[0]
    top3         = res.head(3)
    bottom5      = res.tail(5)
    top20pct_din = res.head(max(1, int(total_prods * 0.2)))['DIN_AUX'].sum()
    concentracion = (top20pct_din / total_din * 100) if total_din > 0 else 0
    top1_pct      = (top1['DIN_AUX'] / total_din * 100) if total_din > 0 else 0

    umbral_bajo  = res['DIN_AUX'].quantile(0.15)
    prod_muertos = res[res['DIN_AUX'] <= umbral_bajo]

    res_ticket = res.copy()
    res_ticket['TICKET'] = res_ticket.apply(
        lambda r: r['DIN_AUX'] / r['VENT_AUX'] if r['VENT_AUX'] > 0 else 0, axis=1)
    mejor_ticket = res_ticket.sort_values('TICKET', ascending=False).iloc[0]

    # Diagnóstico
    if concentracion > 80:
        diag_conc = (f"Tu catálogo tiene **concentración muy alta**: el 20% de productos genera "
                     f"el **{concentracion:.0f}%** de ingresos. Rentable a corto plazo pero arriesgado.")
    elif concentracion > 60:
        diag_conc = (f"El 20% de tus productos genera el **{concentracion:.0f}%** de ingresos. "
                     f"Concentración moderada con productos estrella bien definidos.")
    else:
        diag_conc = (f"Catálogo **bien distribuido**: el 20% superior genera el {concentracion:.0f}% "
                     f"de ingresos, sin dependencia excesiva de un solo producto.")

    top3_pct = top3['DIN_AUX'].sum() / total_din * 100 if total_din > 0 else 0
    unidad_txt = "ingresos" if tiene_dinero else "unidades"
    diagnostico = [
        (f"Análisis de **{total_prods} productos** en "
         f"{'todas las tiendas' if tienda == 'TODAS' else f'la tienda {tienda}'}. "
         f"Volumen: **{total_uds:,.0f} uds** | "
         f"{'Ingresos: **' + f'{total_din:,.2f} €**' if tiene_dinero else f'Total: **{total_din:,.0f}**'}."),
        (f"Producto líder: **{top1['PROD_AUX']}** con el **{top1_pct:.1f}%** del total de {unidad_txt}. "
         f"Los 3 primeros suman el **{top3_pct:.1f}%** del total."),
        diag_conc,
    ]

    # Oportunidades
    oportunidades = []
    if mejor_ticket['TICKET'] > 0 and mejor_ticket['PROD_AUX'] != top1['PROD_AUX']:
        oportunidades.append(
            f"**Potencia {mejor_ticket['PROD_AUX']}**: mejor valor por unidad "
            f"(**{mejor_ticket['TICKET']:,.2f} €/ud**). Dale más visibilidad o combínalo con el líder.")
    if tiene_dinero:
        res_ratio = res[res['VENT_AUX'] > res['VENT_AUX'].quantile(0.5)].copy()
        res_ratio['RATIO'] = res_ratio['DIN_AUX'] / res_ratio['VENT_AUX'].replace(0,1)
        bajo_precio = res_ratio.sort_values('RATIO').head(2)
        if not bajo_precio.empty:
            nombres = ", ".join(bajo_precio['PROD_AUX'].tolist())
            oportunidades.append(
                f"**Revisa precios de {nombres}**: mucho volumen, poco ingreso por unidad. "
                f"Un ajuste del 5-10% puede mejorar la facturación sin perder ventas.")
    if concentracion > 70:
        oportunidades.append(
            f"**Diversifica para reducir riesgo**: con {concentracion:.0f}% concentrado en pocos productos, "
            f"potencia 2-3 del segundo nivel como seguro ante imprevistos.")
    else:
        oportunidades.append(
            f"**Identifica tu próximo estrella**: base diversificada sólida. "
            f"Analiza qué producto del top 5-10 tiene tendencia creciente e invierte en él.")

    # Alertas
    alertas = []
    n_muertos = len(prod_muertos)
    if n_muertos > 0:
        pct = n_muertos / total_prods * 100
        nombres = ", ".join(prod_muertos['PROD_AUX'].tolist()[:3])
        alertas.append(
            f"**{n_muertos} productos de bajo rendimiento** ({pct:.0f}% del catálogo): "
            f"{nombres}{'...' if n_muertos > 3 else ''}. "
            f"Ocupan capital sin retorno — evalúa liquidarlos o eliminarlos.")
    if top1_pct > 35:
        alertas.append(
            f"**Alta dependencia de {top1['PROD_AUX']}** ({top1_pct:.0f}% de ingresos). "
            f"Si falla este proveedor o sube precios, el impacto es crítico. Trabaja alternativas.")
    elif top1_pct > 20:
        alertas.append(
            f"**{top1['PROD_AUX']}** concentra el {top1_pct:.0f}% de ingresos. "
            f"Asegura stock y negocia condiciones estables con el proveedor.")
    if tiene_margen and 'MARGEN_AUX' in res.columns:
        neg = res[res['MARGEN_AUX'] < 0]
        if not neg.empty:
            alertas.append(
                f"**Productos con margen negativo**: {', '.join(neg['PROD_AUX'].tolist()[:2])}. "
                f"Estás perdiendo dinero con cada venta. Actúa urgentemente.")

    # Recomendación
    if top1_pct > 40:
        rec = (f"Esta semana: **asegura el suministro de {top1['PROD_AUX']}** — "
               f"contacta al proveedor y negocia stock garantizado. Es tu motor principal.")
    elif n_muertos > total_prods * 0.3:
        rec = ("Esta semana: **limpia el catálogo**. Más del 30% de productos están por debajo del umbral. "
               "Liquidar ese stock libera capital y simplifica la operación.")
    elif concentracion > 80:
        rec = ("Esta semana: **potencia el segundo nivel** — escoge 2 productos del top 5-10 "
               "y dales más exposición. Reduce dependencia del top actual.")
    else:
        rec = ("Esta semana: **revisa precios del top 5** comparando con competencia. "
               "Con una base sólida, ajustar márgenes mejora rentabilidad sin tocar volumen.")

    return {"diagnostico": diagnostico, "oportunidades": oportunidades,
            "alertas": alertas, "recomendacion": rec}


def formatear_html(analisis):
    html = ""
    secciones = [
        ("🩺 Diagnóstico rápido",       analisis["diagnostico"],   "#e8f4fd", "#1565c0"),
        ("💡 Oportunidades detectadas",  analisis["oportunidades"], "#e8f5e9", "#2e7d32"),
        ("⚠️ Alertas",                   analisis["alertas"],       "#fff8e1", "#e65100"),
    ]
    for titulo, items, bg, color in secciones:
        html += (f"<div style='background:{bg};border-left:4px solid {color};"
                 f"border-radius:8px;padding:14px 18px;margin:10px 0'>")
        html += f"<b style='color:{color};font-size:15px'>{titulo}</b><br><br>"
        for item in items:
            t = item
            while "**" in t:
                t = t.replace("**","<b>",1).replace("**","</b>",1)
            html += f"• {t}<br><br>"
        html += "</div>"
    rec = analisis["recomendacion"]
    while "**" in rec:
        rec = rec.replace("**","<b>",1).replace("**","</b>",1)
    html += (f"<div style='background:#f3e5f5;border-left:4px solid #7b1fa2;"
             f"border-radius:8px;padding:14px 18px;margin:10px 0'>"
             f"<b style='color:#7b1fa2;font-size:15px'>🎯 Recomendación prioritaria</b>"
             f"<br><br>{rec}</div>")
    return html


# ──────────────────────────────────────────────
# GENERACIÓN DE PDF
# ──────────────────────────────────────────────
def generar_pdf(resumen, analisis, df_tabla):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    s_tit  = ParagraphStyle('T',  parent=styles['Title'],   fontSize=22,
                             textColor=colors.HexColor('#1a1a2e'), spaceAfter=4,  alignment=TA_CENTER)
    s_sub  = ParagraphStyle('S',  parent=styles['Normal'],  fontSize=11,
                             textColor=colors.HexColor('#4a4a8a'), spaceAfter=18, alignment=TA_CENTER)
    s_h2   = ParagraphStyle('H2', parent=styles['Heading2'],fontSize=13,
                             textColor=colors.HexColor('#1a1a2e'), spaceBefore=14, spaceAfter=6)
    s_body = ParagraphStyle('B',  parent=styles['Normal'],  fontSize=10,
                             textColor=colors.HexColor('#333333'), spaceAfter=5, leading=15)
    s_bul  = ParagraphStyle('BU', parent=styles['Normal'],  fontSize=10,
                             textColor=colors.HexColor('#333333'), spaceAfter=4, leading=14, leftIndent=12)
    s_foot = ParagraphStyle('F',  parent=styles['Normal'],  fontSize=8,
                             textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    def p(t, style):
        while "**" in t:
            t = t.replace("**","<b>",1).replace("**","</b>",1)
        try:    return Paragraph(t, style)
        except: return Paragraph(t.replace("<b>","").replace("</b>",""), style)

    h = []
    h.append(p("OptiMarket Pro", s_tit))
    h.append(p("Informe Estratégico de Ventas", s_sub))
    h.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a4a8a')))
    h.append(Spacer(1, 0.3*cm))
    h.append(p(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
               f"Tienda: <b>{resumen.get('tienda','Todas')}</b>", s_body))
    h.append(Spacer(1, 0.4*cm))

    # KPIs
    h.append(p("Resumen Ejecutivo", s_h2))
    kpi = [
        ["Indicador", "Valor"],
        ["Total productos analizados", str(resumen.get('total_productos',0))],
        ["Volumen total vendido",       f"{resumen.get('volumen_total',0):,.0f} uds"],
        ["Ingresos totales",            f"{resumen.get('ingresos_totales',0):,.2f} EUR"],
        ["Producto líder",              str(resumen.get('lider','N/A'))[:40]],
        ["Producto menor rendimiento",  str(resumen.get('peor','N/A'))[:40]],
    ]
    tk = Table(kpi, colWidths=[9*cm, 8*cm])
    tk.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0),(-1,0),colors.white),
        ('FONTNAME',  (0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',  (0,0),(-1,-1),10),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f2f8'),colors.white]),
        ('ALIGN',    (1,0),(1,-1),'RIGHT'),
        ('GRID',     (0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),
        ('ROWHEIGHT',(0,0),(-1,-1),20),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
    ]))
    h.append(tk)
    h.append(Spacer(1, 0.5*cm))

    # Top 20
    h.append(p("Top 20 Productos por Rendimiento", s_h2))
    if not df_tabla.empty:
        cols  = ['PROD_AUX','VENT_AUX','DIN_AUX']
        heads = ['Producto','Unidades','Importe (EUR)']
        if 'MARGEN_AUX' in df_tabla.columns:
            cols.append('MARGEN_AUX'); heads.append('Margen (%)')
        filas = [heads]
        for _, row in df_tabla[cols].head(20).iterrows():
            f = [str(row['PROD_AUX'])[:35], f"{row['VENT_AUX']:,.0f}", f"{row['DIN_AUX']:,.2f}"]
            if 'MARGEN_AUX' in df_tabla.columns: f.append(f"{row['MARGEN_AUX']:.1f}%")
            filas.append(f)
        aw = [8.5*cm,3*cm,4*cm] if 'MARGEN_AUX' not in df_tabla.columns else [7*cm,3*cm,3.5*cm,3.5*cm]
        tp = Table(filas, colWidths=aw)
        tp.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4a4a8a')),
            ('TEXTCOLOR', (0,0),(-1,0),colors.white),
            ('FONTNAME',  (0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',  (0,0),(-1,-1),9),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f7f7fb'),colors.white]),
            ('ALIGN',(1,0),(-1,-1),'RIGHT'),
            ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#dddddd')),
            ('ROWHEIGHT',(0,0),(-1,-1),17),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('BACKGROUND',(0,1),(-1,1),colors.HexColor('#d4edda')),
            ('BACKGROUND',(0,2),(-1,2),colors.HexColor('#e8f5e9')),
            ('BACKGROUND',(0,3),(-1,3),colors.HexColor('#f1f8e9')),
        ]))
        h.append(tp)

    h.append(Spacer(1, 0.5*cm))
    h.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    h.append(Spacer(1, 0.2*cm))
    h.append(p("Análisis Estratégico Automático", s_h2))

    for titulo_sec, items in [
        ("Diagnóstico rápido",       analisis["diagnostico"]),
        ("Oportunidades detectadas", analisis["oportunidades"]),
        ("Alertas",                  analisis["alertas"]),
    ]:
        h.append(p(f"<b>{titulo_sec}</b>", s_body))
        for item in items:
            h.append(p(f"• {item}", s_bul))
        h.append(Spacer(1, 0.2*cm))

    h.append(p("<b>Recomendacion prioritaria</b>", s_body))
    h.append(p(analisis["recomendacion"], s_bul))
    h.append(Spacer(1, 0.8*cm))
    h.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    h.append(Spacer(1, 0.2*cm))
    h.append(p("Informe generado por OptiMarket Pro · Analisis automatico sin dependencias externas", s_foot))

    doc.build(h)
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
    st.markdown("<style>.stMetric{background:#f0f2f8;border-radius:10px;padding:10px}</style>",
                unsafe_allow_html=True)
    st.title("📊 OptiMarket Pro — Análisis Estratégico")
    archivo = st.sidebar.file_uploader("📁 1. Sube tu Excel o CSV", type=["xlsx","csv","xls"])

    if archivo:
        try:
            df = (pd.read_csv(archivo, sep=None, engine='python')
                  if archivo.name.lower().endswith('.csv')
                  else pd.read_excel(archivo))
            df.columns = [str(c).strip().upper() for c in df.columns]

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 2. Configuración de Columnas")

            col_prod_auto   = detectar_columna(df.columns, "producto")
            col_vent_auto   = detectar_columna(df.columns, "cantidad")
            col_dinero_auto = detectar_columna(df.columns, "importe")
            col_coste_auto  = detectar_columna(df.columns, "coste")
            col_tienda_auto = detectar_columna(df.columns, "tienda")

            with st.sidebar.expander("🔍 Columnas detectadas"):
                for n, v in [("Producto", col_prod_auto), ("Cantidad", col_vent_auto),
                              ("Importe", col_dinero_auto), ("Coste", col_coste_auto),
                              ("Tienda", col_tienda_auto)]:
                    st.write(f"{'✅' if v else '❌'} **{n}:** {v or 'No detectado'}")

            lc   = list(df.columns)
            idx  = lambda c: lc.index(c) if c and c in lc else 0

            col_prod = st.sidebar.selectbox("Columna Producto/Fabricante", lc, index=idx(col_prod_auto))
            col_vent = st.sidebar.selectbox("Columna Cantidad Vendida",    lc, index=idx(col_vent_auto))

            opc_din = ["— Sin importe —"] + lc
            col_din_sel = st.sidebar.selectbox("Columna Importe/Ingresos (opcional)", opc_din,
                index=opc_din.index(col_dinero_auto) if col_dinero_auto in opc_din else 0)
            col_dinero = col_din_sel if col_din_sel != "— Sin importe —" else None

            opc_cost = ["— Sin coste —"] + lc
            col_cost_sel = st.sidebar.selectbox("Columna Coste (opcional, para margen)", opc_cost,
                index=opc_cost.index(col_coste_auto) if col_coste_auto in opc_cost else 0)
            col_coste = col_cost_sel if col_cost_sel != "— Sin coste —" else None

            tienda_seleccionada = "TODAS"
            if col_tienda_auto:
                ops = ["TODAS"] + sorted(df[col_tienda_auto].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("📍 Seleccionar Tienda:", ops)

            # Procesamiento
            df_f = df.copy()
            if col_tienda_auto and tienda_seleccionada != "TODAS":
                df_f = df_f[df_f[col_tienda_auto] == tienda_seleccionada]

            df_f['PROD_AUX'] = df_f[col_prod].astype(str)
            df_f['VENT_AUX'] = pd.to_numeric(df_f[col_vent], errors='coerce').fillna(0)
            df_f['DIN_AUX']  = (pd.to_numeric(df_f[col_dinero], errors='coerce').fillna(0)
                                if col_dinero else df_f['VENT_AUX'])
            if col_coste:
                df_f['COST_AUX'] = pd.to_numeric(df_f[col_coste], errors='coerce').fillna(0)

            agg = {'VENT_AUX':'sum','DIN_AUX':'sum'}
            if col_coste: agg['COST_AUX'] = 'sum'
            res = df_f.groupby('PROD_AUX').agg(agg).reset_index()
            if col_coste and 'COST_AUX' in res.columns:
                res['MARGEN_AUX'] = ((res['DIN_AUX']-res['COST_AUX'])/res['DIN_AUX'].replace(0,1)*100).round(1)

            res_sorted = res.sort_values('DIN_AUX', ascending=False)
            top20      = res_sorted.head(20).copy()
            bottom5    = res_sorted.tail(5).copy()

            if not top20.empty:
                st.subheader(f"📍 Resultados: {tienda_seleccionada}")
                c1,c2,c3,c4 = st.columns(4)
                with c1: st.metric("📦 VOLUMEN TOTAL", f"{res['VENT_AUX'].sum():,.0f} uds")
                with c2:
                    st.metric("💶 INGRESOS TOTALES" if col_dinero else "📊 TOTAL UNIDADES",
                              f"{res['DIN_AUX'].sum():,.2f} €" if col_dinero else f"{res['DIN_AUX'].sum():,.0f}")
                with c3: st.metric("🏆 LÍDER",       str(top20.iloc[0]['PROD_AUX'])[:18])
                with c4: st.metric("⚠️ MENOR REND.", str(bottom5.iloc[0]['PROD_AUX'])[:18])

                st.divider()

                cg1, cg2 = st.columns([2,1])
                with cg1:
                    st.subheader(f"📈 Top 20 por {col_prod}")
                    fig = px.bar(top20, x='PROD_AUX', y='DIN_AUX', color='DIN_AUX',
                                 color_continuous_scale='Blues', text_auto='.2s',
                                 labels={'PROD_AUX': col_prod, 'DIN_AUX': 'Rendimiento'})
                    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with cg2:
                    st.subheader("🔴 Peores 5 productos")
                    fig2 = px.bar(bottom5.sort_values('DIN_AUX'), x='DIN_AUX', y='PROD_AUX',
                                  orientation='h', color='DIN_AUX', color_continuous_scale='Reds_r',
                                  labels={'PROD_AUX':'','DIN_AUX':'Rendimiento'})
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

                if col_coste and 'MARGEN_AUX' in top20.columns:
                    st.subheader("💹 Margen por producto (Top 20)")
                    fig3 = px.bar(top20.sort_values('MARGEN_AUX', ascending=False),
                                  x='PROD_AUX', y='MARGEN_AUX', color='MARGEN_AUX',
                                  color_continuous_scale='RdYlGn', text_auto='.1f',
                                  labels={'PROD_AUX': col_prod, 'MARGEN_AUX': 'Margen (%)'})
                    fig3.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig3, use_container_width=True)

                # Análisis automático
                st.divider()
                st.subheader("🤖 Análisis Estratégico Automático")

                if st.button("✨ Generar análisis", type="primary"):
                    analisis = analizar_automatico(
                        res_sorted.copy(), tienda_seleccionada,
                        tiene_dinero=bool(col_dinero),
                        tiene_margen=bool(col_coste and 'MARGEN_AUX' in res.columns)
                    )
                    st.session_state['analisis']      = analisis
                    st.session_state['resumen_datos'] = {
                        "tienda":           tienda_seleccionada,
                        "total_productos":  len(res),
                        "volumen_total":    float(res['VENT_AUX'].sum()),
                        "ingresos_totales": float(res['DIN_AUX'].sum()),
                        "lider":            str(top20.iloc[0]['PROD_AUX']),
                        "peor":             str(bottom5.iloc[0]['PROD_AUX']),
                    }
                    st.session_state['df_top20'] = top20.copy()

                if 'analisis' in st.session_state:
                    st.markdown(formatear_html(st.session_state['analisis']), unsafe_allow_html=True)

                    st.divider()
                    st.subheader("📄 Exportar Informe")
                    if st.button("📥 Generar PDF profesional", type="secondary"):
                        with st.spinner("Generando PDF..."):
                            pdf_bytes = generar_pdf(
                                st.session_state['resumen_datos'],
                                st.session_state['analisis'],
                                st.session_state['df_top20']
                            )
                        nombre = f"OptiMarket_{tienda_seleccionada}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                        st.download_button("⬇️ Descargar informe PDF", pdf_bytes,
                                           nombre, "application/pdf", type="primary")

                with st.expander("🗂️ Ver tabla completa"):
                    cs = ['PROD_AUX','VENT_AUX','DIN_AUX']
                    rn = {'PROD_AUX': col_prod, 'VENT_AUX': 'Unidades', 'DIN_AUX': 'Importe (€)'}
                    if col_coste and 'MARGEN_AUX' in res_sorted.columns:
                        cs.append('MARGEN_AUX'); rn['MARGEN_AUX'] = 'Margen (%)'
                    st.dataframe(res_sorted[cs].rename(columns=rn), use_container_width=True)
            else:
                st.warning("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.exception(e)
    else:
        st.info("📁 Por favor, sube un archivo Excel o CSV para empezar el análisis.")
