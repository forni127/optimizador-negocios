import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    "producto": ["PRODUCTO","PROD","FABRICANTE","FAB","ARTICULO","ARTÍCULO",
                 "ART","ITEM","NOMBRE","DESCRIPCION","DESCRIPCIÓN","DESC",
                 "REFERENCIA","REF","SKU","MARCA","CATEGORIA","CATEGORÍA"],
    "cantidad":  ["CANTIDAD","CANT","UNIDADES","UDS","UD","VENTAS","VENTA",
                  "VENDIDO","VENDIDOS","QTY","QUANTITY","UNITS","VOLUMEN","VOL"],
    "importe":   ["IMPORTE","IMP","TOTAL","INGRESOS","INGRESO","FACTURADO",
                  "FACTURACION","FACTURACIÓN","REVENUE","EUROS","EUR","MONTO",
                  "VALOR","VAL","VENTA_TOTAL","TOTAL_VENTA","PVP"],
    "precio":    ["PRECIO","PRICE","PVP","TARIFA"],
    "tienda":    ["TIENDA","STORE","LOCAL","SUCURSAL","DELEGACION","DELEGACIÓN",
                  "PUNTO","SEDE","ESTABLECIMIENTO","COMERCIO","UBICACION","UBICACIÓN"],
    "fecha":     ["FECHA","DATE","DIA","DÍA","MES","MES_AÑO","PERIODO",
                  "PERÍODO","AÑO","ANO","YEAR","MONTH","TRIMESTRE"],
    "coste":     ["COSTE","COSTO","COST","PRECIO_COSTE","PRECIO_COMPRA",
                  "COMPRA","PVC","COSTE_UNIT","COSTO_UNIT"],
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
# CÁLCULO DE ROI y MÉTRICAS
# ──────────────────────────────────────────────
def calcular_metricas(res: pd.DataFrame) -> pd.DataFrame:
    """
    Añade al DataFrame agrupado:
      - BENEFICIO  = DIN_AUX - COST_AUX
      - MARGEN_AUX = BENEFICIO / DIN_AUX * 100
      - ROI_AUX    = BENEFICIO / COST_AUX * 100
      - TICKET_AUX = DIN_AUX / VENT_AUX
    """
    df = res.copy()
    if 'COST_AUX' in df.columns:
        df['BENEFICIO']  = df['DIN_AUX'] - df['COST_AUX']
        df['MARGEN_AUX'] = (df['BENEFICIO'] / df['DIN_AUX'].replace(0, 1) * 100).round(2)
        df['ROI_AUX']    = (df['BENEFICIO'] / df['COST_AUX'].replace(0, 1) * 100).round(2)
    df['TICKET_AUX'] = (df['DIN_AUX'] / df['VENT_AUX'].replace(0, 1)).round(2)
    return df

# ──────────────────────────────────────────────
# ANÁLISIS AUTOMÁTICO
# ──────────────────────────────────────────────
def analizar_automatico(res, tienda, tiene_dinero, tiene_coste):
    total_prods   = len(res)
    total_uds     = res['VENT_AUX'].sum()
    total_din     = res['DIN_AUX'].sum()
    top1          = res.iloc[0]
    top3          = res.head(3)
    bottom5       = res.tail(5)
    top20pct_din  = res.head(max(1, int(total_prods * 0.2)))['DIN_AUX'].sum()
    concentracion = (top20pct_din / total_din * 100) if total_din > 0 else 0
    top1_pct      = (top1['DIN_AUX'] / total_din * 100) if total_din > 0 else 0

    umbral_bajo  = res['DIN_AUX'].quantile(0.15)
    prod_muertos = res[res['DIN_AUX'] <= umbral_bajo]
    n_muertos    = len(prod_muertos)

    # ROI insights
    roi_insights = []
    if tiene_coste and 'ROI_AUX' in res.columns:
        roi_medio    = res['ROI_AUX'].mean()
        mejor_roi    = res.sort_values('ROI_AUX', ascending=False).iloc[0]
        peor_roi     = res.sort_values('ROI_AUX').iloc[0]
        roi_neg      = res[res['ROI_AUX'] < 0]
        total_benef  = res['BENEFICIO'].sum() if 'BENEFICIO' in res.columns else 0

        roi_insights = {
            "roi_medio":   roi_medio,
            "mejor_roi":   mejor_roi,
            "peor_roi":    peor_roi,
            "roi_neg":     roi_neg,
            "total_benef": total_benef,
        }

    # Concentración
    if concentracion > 80:
        diag_conc = (f"Concentración **muy alta**: el 20% de productos genera el "
                     f"**{concentracion:.0f}%** de ingresos. Rentable pero arriesgado.")
    elif concentracion > 60:
        diag_conc = (f"El 20% de tus productos genera el **{concentracion:.0f}%** de ingresos. "
                     f"Concentración moderada con productos estrella definidos.")
    else:
        diag_conc = (f"Catálogo **bien distribuido**: el 20% superior genera el {concentracion:.0f}% "
                     f"de ingresos. Cartera equilibrada.")

    top3_pct = top3['DIN_AUX'].sum() / total_din * 100 if total_din > 0 else 0
    unidad   = "ingresos" if tiene_dinero else "unidades"

    diagnostico = [
        (f"Análisis de **{total_prods} productos** en "
         f"{'todas las tiendas' if tienda == 'TODAS' else f'la tienda {tienda}'}. "
         f"Volumen: **{total_uds:,.0f} uds** | "
         f"{'Ingresos: **' + f'{total_din:,.2f} €**' if tiene_dinero else f'Total: **{total_din:,.0f}**'}."),
        (f"Líder: **{top1['PROD_AUX']}** con el **{top1_pct:.1f}%** del total de {unidad}. "
         f"El top 3 acumula el **{top3_pct:.1f}%**."),
        diag_conc,
    ]
    if roi_insights:
        benef_txt = f"{roi_insights['total_benef']:,.2f} €"
        diagnostico.append(
            f"ROI medio del catálogo: **{roi_insights['roi_medio']:.1f}%** | "
            f"Beneficio total estimado: **{benef_txt}**. "
            f"Mejor ROI: **{roi_insights['mejor_roi']['PROD_AUX']}** "
            f"({roi_insights['mejor_roi']['ROI_AUX']:.1f}%)."
        )

    # Oportunidades
    oportunidades = []
    if roi_insights:
        mr = roi_insights['mejor_roi']
        if mr['PROD_AUX'] != top1['PROD_AUX']:
            oportunidades.append(
                f"**{mr['PROD_AUX']} tiene el mejor ROI** ({mr['ROI_AUX']:.1f}%) "
                f"pero quizás no es el más promocionado. Potenciarlo es la forma más eficiente "
                f"de aumentar beneficio sin aumentar costes.")
        # Productos con alto volumen pero ROI bajo
        if 'ROI_AUX' in res.columns:
            alto_vol_bajo_roi = res[
                (res['VENT_AUX'] > res['VENT_AUX'].quantile(0.6)) &
                (res['ROI_AUX'] < roi_insights['roi_medio'])
            ].sort_values('VENT_AUX', ascending=False).head(2)
            if not alto_vol_bajo_roi.empty:
                nombres = ", ".join(alto_vol_bajo_roi['PROD_AUX'].tolist())
                oportunidades.append(
                    f"**{nombres}** venden mucho pero su ROI está por debajo de la media. "
                    f"Renegocia el precio de compra con el proveedor o ajusta el PVP al alza.")

    ticket_col = 'TICKET_AUX' if 'TICKET_AUX' in res.columns else None
    if ticket_col:
        mejor_ticket = res.sort_values(ticket_col, ascending=False).iloc[0]
        if mejor_ticket['PROD_AUX'] != top1['PROD_AUX']:
            oportunidades.append(
                f"**{mejor_ticket['PROD_AUX']}** tiene el mejor valor por unidad "
                f"(**{mejor_ticket[ticket_col]:,.2f} €/ud**). "
                f"Considera combinarlo con el líder en pack o promoción cruzada.")

    if concentracion > 70:
        oportunidades.append(
            f"**Diversifica para reducir riesgo**: {concentracion:.0f}% de ingresos en pocos productos. "
            f"Potencia 2-3 del segundo nivel como seguro ante imprevistos.")

    # Alertas
    alertas = []
    if n_muertos > 0:
        pct      = n_muertos / total_prods * 100
        nombres  = ", ".join(prod_muertos['PROD_AUX'].tolist()[:3])
        alertas.append(
            f"**{n_muertos} productos de bajo rendimiento** ({pct:.0f}% del catálogo): "
            f"{nombres}{'...' if n_muertos > 3 else ''}. "
            f"Ocupan capital sin retorno — evalúa liquidarlos.")
    if top1_pct > 35:
        alertas.append(
            f"**Alta dependencia de {top1['PROD_AUX']}** ({top1_pct:.0f}% de ingresos). "
            f"Si falla este proveedor el impacto es crítico. Trabaja alternativas.")
    elif top1_pct > 20:
        alertas.append(
            f"**{top1['PROD_AUX']}** concentra el {top1_pct:.0f}% de ingresos. "
            f"Asegura stock y negocia condiciones estables.")
    if roi_insights:
        neg = roi_insights['roi_neg']
        if not neg.empty:
            alertas.append(
                f"**{len(neg)} producto(s) con ROI negativo**: "
                f"{', '.join(neg['PROD_AUX'].tolist()[:3])}. "
                f"Estás perdiendo dinero con cada venta. Actúa esta semana.")
        pr = roi_insights['peor_roi']
        if pr['ROI_AUX'] < 5 and pr['ROI_AUX'] >= 0:
            alertas.append(
                f"**{pr['PROD_AUX']}** tiene un ROI muy bajo ({pr['ROI_AUX']:.1f}%). "
                f"Apenas cubre costes. Revisa si merece la pena mantenerlo.")

    # Recomendación
    if roi_insights and not roi_insights['roi_neg'].empty:
        rec = (f"Esta semana: **elimina o renegocia los productos con ROI negativo** "
               f"({', '.join(roi_insights['roi_neg']['PROD_AUX'].tolist()[:2])}). "
               f"Cada venta de esos productos te cuesta dinero.")
    elif top1_pct > 40:
        rec = (f"Esta semana: **asegura el suministro de {top1['PROD_AUX']}** — "
               f"negocia stock garantizado con el proveedor. Es tu motor principal.")
    elif n_muertos > total_prods * 0.3:
        rec = ("Esta semana: **limpia el catálogo**. Más del 30% de productos están por debajo "
               "del umbral mínimo. Libera capital liquidándolos.")
    elif roi_insights and roi_insights['roi_medio'] < 15:
        rec = (f"Esta semana: **revisa los precios de compra del top 10**. "
               f"Con un ROI medio del {roi_insights['roi_medio']:.1f}% hay margen de mejora "
               f"renegociando con proveedores o ajustando PVPs.")
    else:
        rec = (f"Esta semana: **potencia {roi_insights['mejor_roi']['PROD_AUX']}"
               f" (ROI {roi_insights['mejor_roi']['ROI_AUX']:.1f}%)** — "
               f"es tu producto más rentable y puede crecer más."
               if roi_insights else
               f"Esta semana: **revisa precios del top 5** comparando con competencia. "
               f"Con base sólida, ajustar márgenes mejora rentabilidad sin tocar volumen.")

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
                t = t.replace("**", "<b>", 1).replace("**", "</b>", 1)
            html += f"• {t}<br><br>"
        html += "</div>"
    rec = analisis["recomendacion"]
    while "**" in rec:
        rec = rec.replace("**", "<b>", 1).replace("**", "</b>", 1)
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
    s_h2   = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                             textColor=colors.HexColor('#1a1a2e'), spaceBefore=14, spaceAfter=6)
    s_body = ParagraphStyle('B',  parent=styles['Normal'],  fontSize=10,
                             textColor=colors.HexColor('#333333'), spaceAfter=5, leading=15)
    s_bul  = ParagraphStyle('BU', parent=styles['Normal'],  fontSize=10,
                             textColor=colors.HexColor('#333333'), spaceAfter=4, leading=14, leftIndent=12)
    s_foot = ParagraphStyle('F',  parent=styles['Normal'],  fontSize=8,
                             textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    def p(t, style):
        while "**" in t:
            t = t.replace("**", "<b>", 1).replace("**", "</b>", 1)
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
    kpi_rows = [
        ["Indicador", "Valor"],
        ["Total productos analizados", str(resumen.get('total_productos', 0))],
        ["Volumen total vendido",       f"{resumen.get('volumen_total', 0):,.0f} uds"],
        ["Ingresos totales",            f"{resumen.get('ingresos_totales', 0):,.2f} EUR"],
    ]
    if resumen.get('beneficio_total') is not None:
        kpi_rows.append(["Beneficio total estimado", f"{resumen['beneficio_total']:,.2f} EUR"])
    if resumen.get('roi_medio') is not None:
        kpi_rows.append(["ROI medio del catalogo",   f"{resumen['roi_medio']:.1f}%"])
    if resumen.get('margen_medio') is not None:
        kpi_rows.append(["Margen medio",              f"{resumen['margen_medio']:.1f}%"])
    kpi_rows += [
        ["Producto lider",              str(resumen.get('lider','N/A'))[:40]],
        ["Producto menor rendimiento",  str(resumen.get('peor','N/A'))[:40]],
    ]
    if resumen.get('mejor_roi_prod'):
        kpi_rows.append(["Mejor ROI", f"{resumen['mejor_roi_prod']} ({resumen.get('mejor_roi_val',0):.1f}%)"])

    tk = Table(kpi_rows, colWidths=[9*cm, 8*cm])
    tk.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
        ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f0f2f8'), colors.white]),
        ('ALIGN',         (1,0),(1,-1), 'RIGHT'),
        ('GRID',          (0,0),(-1,-1), 0.4, colors.HexColor('#cccccc')),
        ('ROWHEIGHT',     (0,0),(-1,-1), 20),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (0,0),(-1,-1), 8),
    ]))
    h.append(tk)
    h.append(Spacer(1, 0.5*cm))

    # Top 20
    h.append(p("Top 20 Productos por Rendimiento", s_h2))
    if not df_tabla.empty:
        cols  = ['PROD_AUX','VENT_AUX','DIN_AUX']
        heads = ['Producto','Unidades','Importe (EUR)']
        has_coste = 'COST_AUX' in df_tabla.columns
        if has_coste:
            cols  += ['BENEFICIO','ROI_AUX','MARGEN_AUX']
            heads += ['Beneficio','ROI (%)','Margen (%)']

        filas = [heads]
        for _, row in df_tabla[cols].head(20).iterrows():
            f = [str(row['PROD_AUX'])[:30], f"{row['VENT_AUX']:,.0f}", f"{row['DIN_AUX']:,.2f}"]
            if has_coste:
                f += [f"{row['BENEFICIO']:,.2f}", f"{row['ROI_AUX']:.1f}%", f"{row['MARGEN_AUX']:.1f}%"]
            filas.append(f)

        aw = ([8.5*cm, 2.5*cm, 3.5*cm, 2.5*cm, 2*cm, 2*cm]
              if has_coste else [9*cm, 3*cm, 5*cm])
        tp = Table(filas, colWidths=aw)
        tp.setStyle(TableStyle([
            ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#4a4a8a')),
            ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
            ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0),(-1,-1), 8),
            ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f7f7fb'), colors.white]),
            ('ALIGN',         (1,0),(-1,-1), 'RIGHT'),
            ('GRID',          (0,0),(-1,-1), 0.3, colors.HexColor('#dddddd')),
            ('ROWHEIGHT',     (0,0),(-1,-1), 16),
            ('LEFTPADDING',   (0,0),(-1,-1), 5),
            ('RIGHTPADDING',  (0,0),(-1,-1), 5),
            ('BACKGROUND',    (0,1),(-1,1), colors.HexColor('#d4edda')),
            ('BACKGROUND',    (0,2),(-1,2), colors.HexColor('#e8f5e9')),
            ('BACKGROUND',    (0,3),(-1,3), colors.HexColor('#f1f8e9')),
        ]))
        h.append(tp)

    h.append(Spacer(1, 0.5*cm))
    h.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    h.append(Spacer(1, 0.2*cm))
    h.append(p("Analisis Estrategico Automatico", s_h2))

    for titulo_sec, items in [
        ("Diagnostico rapido",       analisis["diagnostico"]),
        ("Oportunidades detectadas", analisis["oportunidades"]),
        ("Alertas",                  analisis["alertas"]),
    ]:
        h.append(p(f"<b>{titulo_sec}</b>", s_body))
        for item in items: h.append(p(f"• {item}", s_bul))
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
            col_dinero_auto = detectar_columna(df.columns, "importe") or detectar_columna(df.columns, "precio")
            col_coste_auto  = detectar_columna(df.columns, "coste")
            col_tienda_auto = detectar_columna(df.columns, "tienda")

            with st.sidebar.expander("🔍 Columnas detectadas"):
                for n, v in [("Producto",col_prod_auto),("Cantidad",col_vent_auto),
                              ("Importe",col_dinero_auto),("Coste",col_coste_auto),
                              ("Tienda",col_tienda_auto)]:
                    st.write(f"{'✅' if v else '❌'} **{n}:** {v or 'No detectado'}")

            lc  = list(df.columns)
            idx = lambda c: lc.index(c) if c and c in lc else 0

            col_prod = st.sidebar.selectbox("Columna Producto/Fabricante", lc, index=idx(col_prod_auto))
            col_vent = st.sidebar.selectbox("Columna Cantidad Vendida",    lc, index=idx(col_vent_auto))

            opc_din = ["— Sin importe —"] + lc
            col_din_sel = st.sidebar.selectbox("Columna Importe/Ingresos", opc_din,
                index=opc_din.index(col_dinero_auto) if col_dinero_auto in opc_din else 0)
            col_dinero = col_din_sel if col_din_sel != "— Sin importe —" else None

            opc_cost = ["— Sin coste —"] + lc
            col_cost_sel = st.sidebar.selectbox("Columna Coste (para ROI y margen)", opc_cost,
                index=opc_cost.index(col_coste_auto) if col_coste_auto in opc_cost else 0)
            col_coste = col_cost_sel if col_cost_sel != "— Sin coste —" else None

            tienda_seleccionada = "TODAS"
            if col_tienda_auto:
                ops = ["TODAS"] + sorted(df[col_tienda_auto].dropna().unique().tolist())
                tienda_seleccionada = st.sidebar.selectbox("📍 Seleccionar Tienda:", ops)

            # ── PROCESAMIENTO ──
            df_f = df.copy()
            if col_tienda_auto and tienda_seleccionada != "TODAS":
                df_f = df_f[df_f[col_tienda_auto] == tienda_seleccionada]

            df_f['PROD_AUX'] = df_f[col_prod].astype(str)
            df_f['VENT_AUX'] = pd.to_numeric(df_f[col_vent],    errors='coerce').fillna(0)
            df_f['DIN_AUX']  = (pd.to_numeric(df_f[col_dinero], errors='coerce').fillna(0)
                                if col_dinero else df_f['VENT_AUX'])
            if col_coste:
                df_f['COST_AUX'] = pd.to_numeric(df_f[col_coste], errors='coerce').fillna(0)

            agg = {'VENT_AUX':'sum','DIN_AUX':'sum'}
            if col_coste: agg['COST_AUX'] = 'sum'
            res = df_f.groupby('PROD_AUX').agg(agg).reset_index()
            res = calcular_metricas(res)

            res_sorted = res.sort_values('DIN_AUX', ascending=False)
            top20      = res_sorted.head(20).copy()
            bottom5    = res_sorted.tail(5).copy()
            tiene_coste = col_coste and 'COST_AUX' in res.columns

            if not top20.empty:
                # ── KPIs ──
                st.subheader(f"📍 Resultados: {tienda_seleccionada}")

                if tiene_coste:
                    c1,c2,c3,c4,c5,c6 = st.columns(6)
                else:
                    c1,c2,c3,c4 = st.columns(4)

                with c1: st.metric("📦 VOLUMEN",        f"{res['VENT_AUX'].sum():,.0f} uds")
                with c2: st.metric("💶 INGRESOS",       f"{res['DIN_AUX'].sum():,.2f} €"
                                    if col_dinero else f"{res['DIN_AUX'].sum():,.0f}")
                with c3: st.metric("🏆 LÍDER",          str(top20.iloc[0]['PROD_AUX'])[:16])
                with c4: st.metric("⚠️ MENOR REND.",    str(bottom5.iloc[0]['PROD_AUX'])[:16])
                if tiene_coste:
                    benef_total = res['BENEFICIO'].sum()
                    roi_medio   = res['ROI_AUX'].mean()
                    with c5: st.metric("💰 BENEFICIO",  f"{benef_total:,.2f} €",
                                       delta=f"{'↑' if benef_total>0 else '↓'}")
                    with c6: st.metric("📈 ROI MEDIO",  f"{roi_medio:.1f}%",
                                       delta=f"{'Bueno' if roi_medio>20 else 'Revisar'}")

                st.divider()

                # ── GRÁFICAS PRINCIPALES ──
                cg1, cg2 = st.columns([2,1])
                with cg1:
                    st.subheader(f"📈 Top 20 por {col_prod}")
                    fig = px.bar(top20, x='PROD_AUX', y='DIN_AUX', color='DIN_AUX',
                                 color_continuous_scale='Blues', text_auto='.2s',
                                 labels={'PROD_AUX': col_prod, 'DIN_AUX': 'Ingresos (€)'})
                    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with cg2:
                    st.subheader("🔴 Peores 5 productos")
                    fig2 = px.bar(bottom5.sort_values('DIN_AUX'), x='DIN_AUX', y='PROD_AUX',
                                  orientation='h', color='DIN_AUX', color_continuous_scale='Reds_r',
                                  labels={'PROD_AUX':'','DIN_AUX':'Ingresos'})
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

                # ── GRÁFICAS ROI ──
                if tiene_coste:
                    st.divider()
                    r1, r2, r3 = st.columns(3)

                    with r1:
                        st.subheader("📈 ROI por producto (Top 20)")
                        roi_sorted = top20.sort_values('ROI_AUX', ascending=False)
                        colores_roi = ['#d32f2f' if v < 0 else '#f57c00' if v < 15
                                       else '#388e3c' for v in roi_sorted['ROI_AUX']]
                        fig_roi = go.Figure(go.Bar(
                            x=roi_sorted['PROD_AUX'], y=roi_sorted['ROI_AUX'],
                            marker_color=colores_roi,
                            text=[f"{v:.1f}%" for v in roi_sorted['ROI_AUX']],
                            textposition='outside'
                        ))
                        fig_roi.update_layout(xaxis_tickangle=-45, showlegend=False,
                                              yaxis_title="ROI (%)",
                                              shapes=[dict(type='line', x0=-0.5,
                                                           x1=len(roi_sorted)-0.5,
                                                           y0=0, y1=0,
                                                           line=dict(color='black',width=1))])
                        st.plotly_chart(fig_roi, use_container_width=True)

                    with r2:
                        st.subheader("💹 Margen por producto (Top 20)")
                        marg_sorted = top20.sort_values('MARGEN_AUX', ascending=False)
                        fig3 = px.bar(marg_sorted, x='PROD_AUX', y='MARGEN_AUX',
                                      color='MARGEN_AUX', color_continuous_scale='RdYlGn',
                                      text_auto='.1f',
                                      labels={'PROD_AUX': col_prod, 'MARGEN_AUX': 'Margen (%)'})
                        fig3.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig3, use_container_width=True)

                    with r3:
                        st.subheader("🔵 Ingresos vs Beneficio (Top 20)")
                        fig4 = px.scatter(top20, x='DIN_AUX', y='BENEFICIO',
                                          size='VENT_AUX', color='ROI_AUX',
                                          color_continuous_scale='RdYlGn',
                                          hover_name='PROD_AUX',
                                          labels={'DIN_AUX':'Ingresos (€)',
                                                  'BENEFICIO':'Beneficio (€)',
                                                  'ROI_AUX':'ROI (%)'})
                        fig4.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                        st.plotly_chart(fig4, use_container_width=True)

                    # Cuadrante ROI vs Volumen
                    st.subheader("🗺️ Mapa de Rentabilidad Estratégica")
                    st.caption("Tamaño = ingresos | Color = ROI | Cuadrante ideal: arriba a la derecha")
                    roi_med = res['ROI_AUX'].median()
                    vol_med = res['VENT_AUX'].median()
                    fig5 = px.scatter(res_sorted.head(30), x='VENT_AUX', y='ROI_AUX',
                                      size='DIN_AUX', color='ROI_AUX',
                                      color_continuous_scale='RdYlGn',
                                      hover_name='PROD_AUX',
                                      labels={'VENT_AUX':'Unidades vendidas',
                                              'ROI_AUX':'ROI (%)',
                                              'DIN_AUX':'Ingresos (€)'})
                    fig5.add_vline(x=vol_med, line_dash="dot", line_color="gray", opacity=0.5)
                    fig5.add_hline(y=roi_med, line_dash="dot", line_color="gray", opacity=0.5)
                    fig5.add_hline(y=0,       line_dash="dash", line_color="red",  opacity=0.4)
                    # Etiquetas de cuadrantes
                    fig5.add_annotation(x=res_sorted['VENT_AUX'].max()*0.85, y=res_sorted['ROI_AUX'].max()*0.9,
                                        text="⭐ Estrellas", showarrow=False,
                                        font=dict(color="#2e7d32", size=11))
                    fig5.add_annotation(x=res_sorted['VENT_AUX'].max()*0.85, y=roi_med*0.1,
                                        text="⚠️ Volumen sin margen", showarrow=False,
                                        font=dict(color="#e65100", size=11))
                    st.plotly_chart(fig5, use_container_width=True)

                # ── ANÁLISIS AUTOMÁTICO ──
                st.divider()
                st.subheader("🤖 Análisis Estratégico Automático")

                if st.button("✨ Generar análisis", type="primary"):
                    analisis = analizar_automatico(
                        res_sorted.copy(), tienda_seleccionada,
                        tiene_dinero=bool(col_dinero),
                        tiene_coste=bool(tiene_coste)
                    )
                    resumen = {
                        "tienda":           tienda_seleccionada,
                        "total_productos":  len(res),
                        "volumen_total":    float(res['VENT_AUX'].sum()),
                        "ingresos_totales": float(res['DIN_AUX'].sum()),
                        "lider":            str(top20.iloc[0]['PROD_AUX']),
                        "peor":             str(bottom5.iloc[0]['PROD_AUX']),
                    }
                    if tiene_coste:
                        resumen['beneficio_total'] = float(res['BENEFICIO'].sum())
                        resumen['roi_medio']       = float(res['ROI_AUX'].mean())
                        resumen['margen_medio']    = float(res['MARGEN_AUX'].mean())
                        mejor_roi_row = res.sort_values('ROI_AUX', ascending=False).iloc[0]
                        resumen['mejor_roi_prod']  = str(mejor_roi_row['PROD_AUX'])
                        resumen['mejor_roi_val']   = float(mejor_roi_row['ROI_AUX'])

                    st.session_state['analisis']      = analisis
                    st.session_state['resumen_datos'] = resumen
                    st.session_state['df_top20']      = top20.copy()

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

                # Tabla detalle
                with st.expander("🗂️ Ver tabla completa"):
                    cs = ['PROD_AUX','VENT_AUX','DIN_AUX']
                    rn = {'PROD_AUX': col_prod, 'VENT_AUX': 'Unidades', 'DIN_AUX': 'Importe (€)'}
                    if tiene_coste:
                        cs += ['COST_AUX','BENEFICIO','ROI_AUX','MARGEN_AUX','TICKET_AUX']
                        rn.update({'COST_AUX':'Coste (€)','BENEFICIO':'Beneficio (€)',
                                   'ROI_AUX':'ROI (%)','MARGEN_AUX':'Margen (%)','TICKET_AUX':'Ticket (€)'})
                    else:
                        cs.append('TICKET_AUX')
                        rn['TICKET_AUX'] = 'Ticket (€)'
                    st.dataframe(res_sorted[cs].rename(columns=rn), use_container_width=True)

            else:
                st.warning("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.exception(e)
    else:
        st.info("📁 Por favor, sube un archivo Excel o CSV para empezar el análisis.")
