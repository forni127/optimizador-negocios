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
from reportlab.lib.enums import TA_CENTER

st.set_page_config(page_title="OptiMarket Pro", layout="wide")

# ──────────────────────────────────────────────
# DETECCIÓN DE COLUMNAS
# ──────────────────────────────────────────────
PATTERNS = {
    "producto": ["FABRICANTE","FAB","PRODUCTO","PROD","ARTICULO","ARTÍCULO","ART",
                 "ITEM","NOMBRE","DESCRIPCION","DESCRIPCIÓN","DESC","REFERENCIA",
                 "REF","SKU","MARCA","CATEGORIA","CATEGORÍA"],
    "cantidad": ["CANTIDAD","CANT","UNIDADES","UDS","UD","VENTAS","VENTA",
                 "VENDIDO","VENDIDOS","QTY","QUANTITY","UNITS","VOLUMEN","VOL"],
    "importe":  ["IMPORTE","IMP","TOTAL","INGRESOS","INGRESO","FACTURADO",
                 "FACTURACION","FACTURACIÓN","REVENUE","EUROS","EUR","MONTO",
                 "VALOR","VAL","VENTA_TOTAL","TOTAL_VENTA","PVP","PRECIO","PRICE"],
    "coste":    ["COSTE","COSTO","COST","PRECIO_COSTE","PRECIO_COMPRA",
                 "COMPRA","PVC","COSTE_UNIT","COSTO_UNIT"],
    "tienda":   ["TIENDA","STORE","LOCAL","SUCURSAL","DELEGACION","DELEGACIÓN",
                 "PUNTO","SEDE","ESTABLECIMIENTO","UBICACION","UBICACIÓN"],
}

def detectar(columnas, tipo):
    for col in columnas:
        u = col.upper().strip()
        for p in PATTERNS.get(tipo, []):
            if p in u or u in p:
                return col
    return None

# ──────────────────────────────────────────────
# MÉTRICAS
# ──────────────────────────────────────────────
def calcular_metricas(df):
    d = df.copy()
    if 'COST_AUX' in d.columns:
        d['BENEFICIO']  = (d['DIN_AUX'] - d['COST_AUX']).round(2)
        d['MARGEN_AUX'] = (d['BENEFICIO'] / d['DIN_AUX'].replace(0,1) * 100).round(2)
        d['ROI_AUX']    = (d['BENEFICIO'] / d['COST_AUX'].replace(0,1) * 100).round(2)
    d['TICKET_AUX'] = (d['DIN_AUX'] / d['VENT_AUX'].replace(0,1)).round(2)
    return d

# ──────────────────────────────────────────────
# ANÁLISIS AUTOMÁTICO
# ──────────────────────────────────────────────
def analizar(res, tienda, tiene_coste):
    n          = len(res)
    total_uds  = res['VENT_AUX'].sum()
    total_din  = res['DIN_AUX'].sum()
    top1       = res.iloc[0]
    top3_din   = res.head(3)['DIN_AUX'].sum()
    bottom5    = res.tail(5)
    conc       = res.head(max(1,int(n*0.2)))['DIN_AUX'].sum() / total_din * 100 if total_din else 0
    top1_pct   = top1['DIN_AUX'] / total_din * 100 if total_din else 0
    muertos    = res[res['DIN_AUX'] <= res['DIN_AUX'].quantile(0.15)]

    # ── DIAGNÓSTICO ──
    if conc > 80:
        txt_conc = f"Concentración **muy alta**: el 20% de productos genera el **{conc:.0f}%** de ingresos. Rentable pero frágil."
    elif conc > 60:
        txt_conc = f"El 20% de productos genera el **{conc:.0f}%** de ingresos. Concentración moderada con productos estrella claros."
    else:
        txt_conc = f"Catálogo **equilibrado**: el 20% superior genera el {conc:.0f}% de ingresos, sin dependencia excesiva."

    diag = [
        f"Análisis de **{n} productos** · {'todas las tiendas' if tienda=='TODAS' else tienda} · "
        f"**{total_uds:,.0f} uds** vendidas · **{total_din:,.2f} €** en ingresos.",
        f"Líder: **{top1['PROD_AUX']}** representa el **{top1_pct:.1f}%** de ingresos. "
        f"El top 3 acumula el **{top3_din/total_din*100:.1f}%**.",
        txt_conc,
    ]
    if tiene_coste and 'ROI_AUX' in res.columns:
        roi_med   = res['ROI_AUX'].mean()
        benef_tot = res['BENEFICIO'].sum()
        best_roi  = res.sort_values('ROI_AUX', ascending=False).iloc[0]
        diag.append(
            f"ROI medio: **{roi_med:.1f}%** · Beneficio total: **{benef_tot:,.2f} €** · "
            f"Producto más rentable: **{best_roi['PROD_AUX']}** ({best_roi['ROI_AUX']:.1f}%)"
        )

    # ── OPORTUNIDADES ──
    opps = []
    if tiene_coste and 'ROI_AUX' in res.columns:
        roi_med  = res['ROI_AUX'].mean()
        best_roi = res.sort_values('ROI_AUX', ascending=False).iloc[0]
        if best_roi['PROD_AUX'] != top1['PROD_AUX']:
            opps.append(
                f"**{best_roi['PROD_AUX']}** tiene el mejor ROI ({best_roi['ROI_AUX']:.1f}%) "
                f"pero no es el líder de ventas. Potenciarlo es la forma más eficiente de aumentar beneficio.")
        bajo_roi = res[
            (res['VENT_AUX'] > res['VENT_AUX'].quantile(0.6)) & (res['ROI_AUX'] < roi_med)
        ].head(2)
        if not bajo_roi.empty:
            opps.append(
                f"**{', '.join(bajo_roi['PROD_AUX'].tolist())}** venden mucho pero su ROI está bajo la media. "
                f"Renegocia precio de compra o ajusta PVP al alza.")
    best_ticket = res.sort_values('TICKET_AUX', ascending=False).iloc[0]
    if best_ticket['PROD_AUX'] != top1['PROD_AUX']:
        opps.append(
            f"**{best_ticket['PROD_AUX']}** tiene el mejor ticket medio ({best_ticket['TICKET_AUX']:,.2f} €/ud). "
            f"Combínalo con el líder en packs o promoción cruzada.")
    if conc > 70:
        opps.append(
            f"Diversifica: con {conc:.0f}% de ingresos concentrados, potencia 2-3 productos del segundo nivel como seguro.")
    else:
        opps.append("Base diversificada sólida. Analiza qué producto del top 5-10 tiene tendencia creciente e invierte en él.")

    # ── ALERTAS ──
    alertas = []
    if len(muertos) > 0:
        nombres = ", ".join(muertos['PROD_AUX'].tolist()[:3])
        alertas.append(
            f"**{len(muertos)} productos de bajo rendimiento** ({len(muertos)/n*100:.0f}% del catálogo): "
            f"{nombres}{'...' if len(muertos)>3 else ''}. Ocupan capital sin retorno.")
    if top1_pct > 35:
        alertas.append(
            f"**Dependencia crítica de {top1['PROD_AUX']}** ({top1_pct:.0f}% de ingresos). "
            f"Un fallo de suministro sería devastador. Trabaja alternativas ahora.")
    elif top1_pct > 20:
        alertas.append(
            f"**{top1['PROD_AUX']}** concentra el {top1_pct:.0f}% de ingresos. "
            f"Asegura stock y negocia condiciones estables.")
    if tiene_coste and 'ROI_AUX' in res.columns:
        neg = res[res['ROI_AUX'] < 0]
        if not neg.empty:
            alertas.append(
                f"**{len(neg)} producto(s) con ROI negativo**: {', '.join(neg['PROD_AUX'].tolist()[:3])}. "
                f"Cada venta te cuesta dinero. Actúa esta semana.")
        peor_roi = res.sort_values('ROI_AUX').iloc[0]
        if 0 <= peor_roi['ROI_AUX'] < 5:
            alertas.append(
                f"**{peor_roi['PROD_AUX']}** tiene ROI del {peor_roi['ROI_AUX']:.1f}%. "
                f"Apenas cubre costes. Revisa si merece la pena mantenerlo.")

    # ── RECOMENDACIÓN ──
    if tiene_coste and 'ROI_AUX' in res.columns:
        neg = res[res['ROI_AUX'] < 0]
        roi_med = res['ROI_AUX'].mean()
        best_roi = res.sort_values('ROI_AUX', ascending=False).iloc[0]
        if not neg.empty:
            rec = (f"Esta semana: **elimina o renegocia los productos con ROI negativo** "
                   f"({', '.join(neg['PROD_AUX'].tolist()[:2])}). Cada venta te cuesta dinero real.")
        elif roi_med < 15:
            rec = (f"Esta semana: **revisa precios de compra del top 10**. "
                   f"Con ROI medio del {roi_med:.1f}% hay margen de mejora renegociando con proveedores.")
        else:
            rec = (f"Esta semana: **potencia {best_roi['PROD_AUX']} (ROI {best_roi['ROI_AUX']:.1f}%)** — "
                   f"es tu producto más rentable y tiene recorrido de crecimiento.")
    elif top1_pct > 40:
        rec = f"Esta semana: **asegura el suministro de {top1['PROD_AUX']}** — negocia stock garantizado con el proveedor."
    elif len(muertos) > n * 0.3:
        rec = "Esta semana: **limpia el catálogo**. Más del 30% de productos están por debajo del umbral mínimo."
    else:
        rec = "Esta semana: **revisa precios del top 5** comparando con competencia. Ajustar márgenes mejora rentabilidad sin tocar volumen."

    return {"diagnostico": diag, "oportunidades": opps, "alertas": alertas, "recomendacion": rec}


def html_analisis(a):
    html = ""
    for titulo, items, bg, col in [
        ("🩺 Diagnóstico rápido",       a["diagnostico"],   "#e8f4fd","#1565c0"),
        ("💡 Oportunidades",            a["oportunidades"], "#e8f5e9","#2e7d32"),
        ("⚠️ Alertas",                  a["alertas"],       "#fff8e1","#e65100"),
    ]:
        html += f"<div style='background:{bg};border-left:4px solid {col};border-radius:8px;padding:14px 18px;margin:10px 0'>"
        html += f"<b style='color:{col};font-size:15px'>{titulo}</b><br><br>"
        for it in items:
            t = it
            while "**" in t: t = t.replace("**","<b>",1).replace("**","</b>",1)
            html += f"• {t}<br><br>"
        html += "</div>"
    rec = a["recomendacion"]
    while "**" in rec: rec = rec.replace("**","<b>",1).replace("**","</b>",1)
    html += (f"<div style='background:#f3e5f5;border-left:4px solid #7b1fa2;border-radius:8px;"
             f"padding:14px 18px;margin:10px 0'>"
             f"<b style='color:#7b1fa2;font-size:15px'>🎯 Recomendación prioritaria</b><br><br>{rec}</div>")
    return html


# ──────────────────────────────────────────────
# PDF
# ──────────────────────────────────────────────
def generar_pdf(resumen, analisis, df_top):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    st_ = getSampleStyleSheet()
    def sty(name, **kw):
        return ParagraphStyle(name, parent=st_['Normal'], **kw)

    s_tit  = sty('tit',  fontSize=22, textColor=colors.HexColor('#1a1a2e'), spaceAfter=4,  alignment=TA_CENTER)
    s_sub  = sty('sub',  fontSize=11, textColor=colors.HexColor('#4a4a8a'), spaceAfter=18, alignment=TA_CENTER)
    s_h2   = sty('h2',   fontSize=13, textColor=colors.HexColor('#1a1a2e'), spaceBefore=14, spaceAfter=6,
                 fontName='Helvetica-Bold')
    s_body = sty('body', fontSize=10, textColor=colors.HexColor('#333333'), spaceAfter=5,  leading=15)
    s_bul  = sty('bul',  fontSize=10, textColor=colors.HexColor('#333333'), spaceAfter=4,  leading=14, leftIndent=12)
    s_foot = sty('foot', fontSize=8,  textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    def p(txt, s):
        while "**" in txt: txt = txt.replace("**","<b>",1).replace("**","</b>",1)
        try:    return Paragraph(txt, s)
        except: return Paragraph(txt.replace("<b>","").replace("</b>",""), s)

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
    kpi = [["Indicador","Valor"],
           ["Productos analizados",        str(resumen.get('n_prods',0))],
           ["Volumen total",               f"{resumen.get('vol_total',0):,.0f} uds"],
           ["Ingresos totales",            f"{resumen.get('ingresos',0):,.2f} EUR"]]
    if resumen.get('benef') is not None:
        kpi += [["Beneficio total",        f"{resumen['benef']:,.2f} EUR"],
                ["ROI medio catalogo",     f"{resumen.get('roi_med',0):.1f}%"],
                ["Margen medio",           f"{resumen.get('marg_med',0):.1f}%"],
                ["Mejor ROI",              f"{resumen.get('best_roi_prod','N/A')} ({resumen.get('best_roi_val',0):.1f}%)"]]
    kpi += [["Producto lider",             str(resumen.get('lider','N/A'))[:40]],
            ["Producto menor rendimiento", str(resumen.get('peor','N/A'))[:40]]]

    tk = Table(kpi, colWidths=[9*cm,8*cm])
    tk.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f2f8'),colors.white]),
        ('ALIGN',(1,0),(1,-1),'RIGHT'),
        ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),
        ('ROWHEIGHT',(0,0),(-1,-1),20),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
    ]))
    h.append(tk)
    h.append(Spacer(1,0.5*cm))

    # Top 20
    h.append(p("Top 20 Productos", s_h2))
    has_c = 'COST_AUX' in df_top.columns
    cols  = ['PROD_AUX','VENT_AUX','DIN_AUX']
    heads = ['Producto','Uds','Ingresos (EUR)']
    if has_c:
        cols  += ['COST_AUX','BENEFICIO','ROI_AUX','MARGEN_AUX']
        heads += ['Coste','Beneficio','ROI%','Margen%']

    rows = [heads]
    for _, r in df_top[cols].head(20).iterrows():
        f = [str(r['PROD_AUX'])[:28], f"{r['VENT_AUX']:,.0f}", f"{r['DIN_AUX']:,.2f}"]
        if has_c:
            f += [f"{r['COST_AUX']:,.2f}", f"{r['BENEFICIO']:,.2f}",
                  f"{r['ROI_AUX']:.1f}%", f"{r['MARGEN_AUX']:.1f}%"]
        rows.append(f)

    aw = ([7*cm,1.8*cm,2.5*cm,2.2*cm,2.2*cm,1.8*cm,1.8*cm]
          if has_c else [10*cm,3*cm,4.5*cm])
    tp = Table(rows, colWidths=aw)
    tp.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4a4a8a')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f7f7fb'),colors.white]),
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#dddddd')),
        ('ROWHEIGHT',(0,0),(-1,-1),16),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('BACKGROUND',(0,1),(-1,1),colors.HexColor('#d4edda')),
        ('BACKGROUND',(0,2),(-1,2),colors.HexColor('#e8f5e9')),
        ('BACKGROUND',(0,3),(-1,3),colors.HexColor('#f1f8e9')),
    ]))
    h.append(tp)
    h.append(Spacer(1,0.5*cm))
    h.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor('#cccccc')))
    h.append(Spacer(1,0.2*cm))
    h.append(p("Analisis Estrategico", s_h2))

    for sec, items in [("Diagnostico",analisis["diagnostico"]),
                       ("Oportunidades",analisis["oportunidades"]),
                       ("Alertas",analisis["alertas"])]:
        h.append(p(f"<b>{sec}</b>", s_body))
        for it in items: h.append(p(f"• {it}", s_bul))
        h.append(Spacer(1,0.2*cm))

    h.append(p("<b>Recomendacion prioritaria</b>", s_body))
    h.append(p(analisis["recomendacion"], s_bul))
    h.append(Spacer(1,0.8*cm))
    h.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor('#cccccc')))
    h.append(Spacer(1,0.2*cm))
    h.append(p("OptiMarket Pro · Analisis automatico sin dependencias externas", s_foot))
    doc.build(h)
    buf.seek(0)
    return buf.getvalue()


# ──────────────────────────────────────────────
# APP
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
    st.title("📊 OptiMarket Pro")

    # ── SIDEBAR MINIMALISTA ──
    st.sidebar.title("⚙️ Configuración")
    archivo = st.sidebar.file_uploader("Sube tu Excel o CSV", type=["xlsx","csv","xls"])

    if archivo:
        try:
            df = (pd.read_csv(archivo, sep=None, engine='python')
                  if archivo.name.lower().endswith('.csv')
                  else pd.read_excel(archivo))
            df.columns = [str(c).strip().upper() for c in df.columns]
            lc = list(df.columns)

            # Detección automática
            d_prod  = detectar(df.columns,"producto")
            d_cant  = detectar(df.columns,"cantidad")
            d_imp   = detectar(df.columns,"importe")
            d_coste = detectar(df.columns,"coste")
            d_tiend = detectar(df.columns,"tienda")

            st.sidebar.divider()

            # ── 4 selectores básicos ──
            idx = lambda c: lc.index(c) if c and c in lc else 0

            col_prod  = st.sidebar.selectbox("🏷️ Producto",  lc, index=idx(d_prod))
            col_cant  = st.sidebar.selectbox("📦 Cantidad",  lc, index=idx(d_cant))
            col_imp   = st.sidebar.selectbox("💶 Importe",   lc, index=idx(d_imp))
            opc_c     = ["— Sin coste —"] + lc
            col_c_sel = st.sidebar.selectbox("💰 Coste",     opc_c,
                            index=opc_c.index(d_coste) if d_coste in opc_c else 0)
            col_coste = col_c_sel if col_c_sel != "— Sin coste —" else None

            # Filtro tienda (solo si existe)
            tienda = "TODAS"
            if d_tiend:
                st.sidebar.divider()
                ops   = ["TODAS"] + sorted(df[d_tiend].dropna().unique().tolist())
                tienda = st.sidebar.selectbox("📍 Tienda", ops)

            # Estado detección (colapsado)
            with st.sidebar.expander("🔍 Ver detección automática"):
                for n,v in [("Producto",d_prod),("Cantidad",d_cant),
                             ("Importe",d_imp),("Coste",d_coste),("Tienda",d_tiend)]:
                    st.write(f"{'✅' if v else '❌'} **{n}:** {v or 'No detectado'}")

            # ── PROCESAMIENTO ──
            df_f = df.copy()
            if d_tiend and tienda != "TODAS":
                df_f = df_f[df_f[d_tiend] == tienda]

            df_f['PROD_AUX'] = df_f[col_prod].astype(str)
            df_f['VENT_AUX'] = pd.to_numeric(df_f[col_cant], errors='coerce').fillna(0)
            df_f['DIN_AUX']  = pd.to_numeric(df_f[col_imp],  errors='coerce').fillna(0)
            if col_coste:
                df_f['COST_AUX'] = pd.to_numeric(df_f[col_coste], errors='coerce').fillna(0)

            agg = {'VENT_AUX':'sum','DIN_AUX':'sum'}
            if col_coste: agg['COST_AUX'] = 'sum'
            res        = calcular_metricas(df_f.groupby('PROD_AUX').agg(agg).reset_index())
            res_sorted = res.sort_values('DIN_AUX', ascending=False)
            top20      = res_sorted.head(20).copy()
            bottom5    = res_sorted.tail(5).copy()
            tiene_c    = col_coste and 'COST_AUX' in res.columns

            if top20.empty:
                st.warning("No hay datos para esta selección.")
            else:
                st.subheader(f"📍 {tienda}")

                # ── KPIs ──
                if tiene_c:
                    k1,k2,k3,k4,k5,k6 = st.columns(6)
                else:
                    k1,k2,k3,k4 = st.columns(4)

                with k1: st.metric("📦 Unidades",    f"{res['VENT_AUX'].sum():,.0f}")
                with k2: st.metric("💶 Ingresos",    f"{res['DIN_AUX'].sum():,.2f} €")
                with k3: st.metric("🏆 Líder",       str(top20.iloc[0]['PROD_AUX'])[:16])
                with k4: st.metric("⚠️ Menor rend.", str(bottom5.iloc[0]['PROD_AUX'])[:16])
                if tiene_c:
                    benef = res['BENEFICIO'].sum()
                    roi_m = res['ROI_AUX'].mean()
                    with k5:
                        st.metric("💰 Beneficio", f"{benef:,.2f} €",
                                  delta=f"{'positivo' if benef>0 else 'negativo'}")
                    with k6:
                        st.metric("📈 ROI medio", f"{roi_m:.1f}%",
                                  delta=f"{'✓ bueno' if roi_m>20 else '↓ revisar'}")

                st.divider()

                # ── GRÁFICAS ──
                g1, g2 = st.columns([2,1])
                with g1:
                    st.subheader("📈 Top 20 — Ingresos")
                    fig = px.bar(top20, x='PROD_AUX', y='DIN_AUX', color='DIN_AUX',
                                 color_continuous_scale='Blues', text_auto='.2s',
                                 labels={'PROD_AUX': col_prod, 'DIN_AUX': 'Ingresos (€)'})
                    fig.update_layout(xaxis_tickangle=-45, showlegend=False,
                                      xaxis_title="", coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.subheader("🔴 Peores 5")
                    fig2 = px.bar(bottom5.sort_values('DIN_AUX'), x='DIN_AUX', y='PROD_AUX',
                                  orientation='h', color='DIN_AUX', color_continuous_scale='Reds_r',
                                  labels={'PROD_AUX':'','DIN_AUX':'Ingresos (€)'})
                    fig2.update_layout(showlegend=False, coloraxis_showscale=False)
                    st.plotly_chart(fig2, use_container_width=True)

                if tiene_c:
                    r1, r2, r3 = st.columns(3)

                    with r1:
                        st.subheader("📊 ROI por producto")
                        rs = top20.sort_values('ROI_AUX', ascending=False)
                        clr = ['#d32f2f' if v<0 else '#f57c00' if v<15 else '#388e3c'
                               for v in rs['ROI_AUX']]
                        fig_r = go.Figure(go.Bar(
                            x=rs['PROD_AUX'], y=rs['ROI_AUX'],
                            marker_color=clr,
                            text=[f"{v:.1f}%" for v in rs['ROI_AUX']],
                            textposition='outside'))
                        fig_r.update_layout(
                            xaxis_tickangle=-45, yaxis_title="ROI (%)",
                            shapes=[dict(type='line',x0=-0.5,x1=len(rs)-0.5,
                                        y0=0,y1=0,line=dict(color='black',width=1))])
                        st.plotly_chart(fig_r, use_container_width=True)

                    with r2:
                        st.subheader("💹 Margen por producto")
                        ms = top20.sort_values('MARGEN_AUX', ascending=False)
                        fig3 = px.bar(ms, x='PROD_AUX', y='MARGEN_AUX',
                                      color='MARGEN_AUX', color_continuous_scale='RdYlGn',
                                      text_auto='.1f',
                                      labels={'PROD_AUX':col_prod,'MARGEN_AUX':'Margen (%)'})
                        fig3.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
                        st.plotly_chart(fig3, use_container_width=True)

                    with r3:
                        st.subheader("🔵 Ingresos vs Beneficio")
                        fig4 = px.scatter(top20, x='DIN_AUX', y='BENEFICIO',
                                          size='VENT_AUX', color='ROI_AUX',
                                          color_continuous_scale='RdYlGn',
                                          hover_name='PROD_AUX',
                                          labels={'DIN_AUX':'Ingresos (€)',
                                                  'BENEFICIO':'Beneficio (€)',
                                                  'ROI_AUX':'ROI (%)'})
                        fig4.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                        st.plotly_chart(fig4, use_container_width=True)

                    # Mapa estratégico
                    st.subheader("🗺️ Mapa de Rentabilidad Estratégica")
                    st.caption("Tamaño = ingresos · Color = ROI · Ideal: arriba a la derecha")
                    roi_med = float(res['ROI_AUX'].median())
                    vol_med = float(res['VENT_AUX'].median())
                    plot_df = res_sorted.head(30)
                    fig5 = px.scatter(plot_df, x='VENT_AUX', y='ROI_AUX',
                                      size='DIN_AUX', color='ROI_AUX',
                                      color_continuous_scale='RdYlGn',
                                      hover_name='PROD_AUX',
                                      labels={'VENT_AUX':'Unidades vendidas',
                                              'ROI_AUX':'ROI (%)',
                                              'DIN_AUX':'Ingresos (€)'})
                    fig5.add_vline(x=vol_med, line_dash="dot", line_color="gray", opacity=0.5)
                    fig5.add_hline(y=roi_med, line_dash="dot", line_color="gray", opacity=0.5)
                    fig5.add_hline(y=0,       line_dash="dash", line_color="red",  opacity=0.4)
                    x_max = float(plot_df['VENT_AUX'].max())
                    y_max = float(plot_df['ROI_AUX'].max())
                    fig5.add_annotation(x=x_max*0.85, y=y_max*0.9,
                                        text="⭐ Estrellas", showarrow=False,
                                        font=dict(color="#2e7d32",size=11))
                    fig5.add_annotation(x=x_max*0.85, y=roi_med*0.2,
                                        text="⚠️ Volumen sin margen", showarrow=False,
                                        font=dict(color="#e65100",size=11))
                    st.plotly_chart(fig5, use_container_width=True)

                # ── ANÁLISIS AUTOMÁTICO ──
                st.divider()
                st.subheader("🤖 Análisis Estratégico")

                if st.button("✨ Generar análisis", type="primary"):
                    an = analizar(res_sorted.copy(), tienda, tiene_c)
                    rsm = {
                        "tienda":   tienda,
                        "n_prods":  len(res),
                        "vol_total":float(res['VENT_AUX'].sum()),
                        "ingresos": float(res['DIN_AUX'].sum()),
                        "lider":    str(top20.iloc[0]['PROD_AUX']),
                        "peor":     str(bottom5.iloc[0]['PROD_AUX']),
                    }
                    if tiene_c:
                        br = res.sort_values('ROI_AUX', ascending=False).iloc[0]
                        rsm.update({
                            "benef":         float(res['BENEFICIO'].sum()),
                            "roi_med":       float(res['ROI_AUX'].mean()),
                            "marg_med":      float(res['MARGEN_AUX'].mean()),
                            "best_roi_prod": str(br['PROD_AUX']),
                            "best_roi_val":  float(br['ROI_AUX']),
                        })
                    st.session_state.update({'an':an,'rsm':rsm,'top20':top20.copy()})

                if 'an' in st.session_state:
                    st.markdown(html_analisis(st.session_state['an']), unsafe_allow_html=True)

                    st.divider()
                    st.subheader("📄 Exportar Informe PDF")
                    if st.button("📥 Generar PDF", type="secondary"):
                        with st.spinner("Generando PDF..."):
                            pdf = generar_pdf(st.session_state['rsm'],
                                              st.session_state['an'],
                                              st.session_state['top20'])
                        nombre = f"OptiMarket_{tienda}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                        st.download_button("⬇️ Descargar PDF", pdf, nombre,
                                           "application/pdf", type="primary")

                # Tabla completa
                with st.expander("🗂️ Tabla completa de datos"):
                    cs = ['PROD_AUX','VENT_AUX','DIN_AUX']
                    rn = {'PROD_AUX':col_prod,'VENT_AUX':'Unidades','DIN_AUX':'Ingresos (€)'}
                    if tiene_c:
                        cs += ['COST_AUX','BENEFICIO','ROI_AUX','MARGEN_AUX','TICKET_AUX']
                        rn.update({'COST_AUX':'Coste (€)','BENEFICIO':'Beneficio (€)',
                                   'ROI_AUX':'ROI (%)','MARGEN_AUX':'Margen (%)','TICKET_AUX':'Ticket (€)'})
                    else:
                        cs.append('TICKET_AUX'); rn['TICKET_AUX'] = 'Ticket (€)'
                    st.dataframe(res_sorted[cs].rename(columns=rn), use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
    else:
        st.info("📁 Sube un archivo Excel o CSV para empezar.")
