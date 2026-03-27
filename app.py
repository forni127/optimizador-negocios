import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import io
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="OptiMarket Pro | Intelligence",
                   page_icon="🚀", layout="wide")

# ─────────────────────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.report-card {
    background: #ffffff; padding: 22px; border-radius: 12px;
    border-left: 6px solid #0047AB; margin-bottom: 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08); color: #1e1e1e;
}
.report-card h4 { color: #0047AB; margin: 0 0 10px 0; font-size: 15px; }
.kpi-box {
    background: #f8f9ff; border-radius: 12px; border: 1px solid #dde3f0;
    padding: 18px; text-align: center;
}
.stMetric { background: #f8f9ff; border-radius: 10px; padding: 14px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DETECCIÓN DINÁMICA DE COLUMNAS
# Acepta múltiples variantes por tipo, no solo una palabra exacta
# ─────────────────────────────────────────────────────────────
PATTERNS = {
    "producto":    ["PRODUCTO","PROD","FABRICANTE","FAB","ARTICULO","ARTÍCULO",
                    "ART","MODELO","ITEM","NOMBRE","DESC","DESCRIPCION","DESCRIPCIÓN",
                    "REFERENCIA","REF","SKU","MARCA","CATEGORIA","CATEGORÍA"],
    "precio_venta":["PRECIO_VENTA","PRECIO VENTA","PVP","TARIFA","VENTA","PRICE",
                    "IMPORTE","IMP","INGRESOS","INGRESO","REVENUE","TOTAL_VENTA",
                    "EUROS","EUR","VALOR"],
    "coste":       ["COSTE","COSTO","COST","PRECIO_COSTE","PRECIO COSTE",
                    "PRECIO_COMPRA","PRECIO COMPRA","COMPRA","PVC",
                    "COSTE_UNIT","COSTO_UNIT"],
    "cantidad":    ["VENTAS","VENTA","UNIDADES","UDS","UD","CANTIDAD","CANT",
                    "VENDIDO","VENDIDOS","QTY","QUANTITY","UNITS","VOLUMEN","VOL"],
    "tienda":      ["TIENDA","STORE","LOCAL","SUCURSAL","DELEGACION","DELEGACIÓN",
                    "SEDE","PUNTO","ESTABLECIMIENTO","UBICACION","UBICACIÓN"],
}

def detectar(columnas, tipo):
    """Detecta la columna buscando cualquier patrón dentro del nombre."""
    for col in columnas:
        u = col.upper().strip().replace(" ","_")
        for pat in PATTERNS.get(tipo, []):
            if pat in u or u in pat:
                return col
    return None

# ─────────────────────────────────────────────────────────────
# ANÁLISIS / COMENTARIOS IA
# ─────────────────────────────────────────────────────────────
def generar_comentarios(df, estrella, eficiente, bajo, total_neto, roi_medio):
    """
    Genera comentarios estratégicos ricos basados en los datos reales.
    Sin API externa — lógica Python pura.
    """
    n          = len(df)
    top3_benef = df.nlargest(3, 'Rentabilidad_Total')['Rentabilidad_Total'].sum()
    conc_pct   = top3_benef / df['Rentabilidad_Total'].sum() * 100 if df['Rentabilidad_Total'].sum() else 0
    neg_count  = (df['Rentabilidad_Total'] < 0).sum()
    roi_max    = df['ROI_Porcentaje'].max()
    roi_min    = df['ROI_Porcentaje'].min()
    spread_roi = roi_max - roi_min

    # Diagnóstico general
    if roi_medio > 40:
        salud = "excelente"
        salud_detalle = "El catálogo opera con márgenes sólidos y una estructura de costes muy eficiente."
    elif roi_medio > 20:
        salud = "bueno"
        salud_detalle = "El negocio genera retornos positivos, aunque hay margen de optimización en varios productos."
    elif roi_medio > 0:
        salud = "ajustado"
        salud_detalle = "Los márgenes son positivos pero estrechos. Pequeñas subidas de precio o bajadas de coste tendrían gran impacto."
    else:
        salud = "crítico"
        salud_detalle = "El catálogo presenta pérdidas netas. Es urgente revisar precios y eliminar productos ineficientes."

    # Concentración
    if conc_pct > 80:
        txt_conc = f"El top 3 genera el <b>{conc_pct:.0f}%</b> del beneficio total — concentración muy alta. Un fallo en cualquiera de ellos impacta directamente en la cuenta de resultados."
    elif conc_pct > 60:
        txt_conc = f"El top 3 concentra el <b>{conc_pct:.0f}%</b> del beneficio — dependencia moderada-alta. Considera potenciar el segundo nivel del catálogo."
    else:
        txt_conc = f"El beneficio está <b>bien distribuido</b>: el top 3 solo representa el {conc_pct:.0f}%. Cartera equilibrada y resiliente."

    # Dispersión ROI
    if spread_roi > 100:
        txt_spread = f"La diferencia entre el mejor ROI ({roi_max:.1f}%) y el peor ({roi_min:.1f}%) es de <b>{spread_roi:.0f} puntos</b>. Hay productos arrastrando hacia abajo la media de forma significativa."
    else:
        txt_spread = f"Los ROIs del catálogo son relativamente homogéneos (rango de {spread_roi:.0f} puntos), lo que indica una gestión de costes consistente."

    # Productos negativos
    txt_neg = (f"⚠️ <b>{neg_count} producto(s)</b> generan beneficio negativo — cada unidad vendida destruye valor."
               if neg_count > 0 else
               "✅ Todos los productos generan beneficio positivo.")

    comentarios = {
        "salud":        salud,
        "salud_detalle":salud_detalle,
        "conc_pct":     conc_pct,
        "txt_conc":     txt_conc,
        "txt_spread":   txt_spread,
        "txt_neg":      txt_neg,
        "neg_count":    neg_count,
        "spread_roi":   spread_roi,
    }

    # Tarjetas individuales
    # ESTRELLA
    estrella_card = {
        "titulo":  f"🥇 Líder de Ingresos: {estrella['Producto']}",
        "color":   "#0047AB",
        "cuerpo":  (
            f"Con <b>{estrella['Rentabilidad_Total']:,.2f} €</b> de beneficio neto, este producto es "
            f"el principal motor del negocio. Su ROI del <b>{estrella['ROI_Porcentaje']:.1f}%</b> "
            f"{'supera ampliamente la media del catálogo' if estrella['ROI_Porcentaje'] > roi_medio else 'está en línea con la media'}. "
            f"<br><br><b>Estrategia recomendada:</b> Asegura el suministro con stock garantizado y "
            f"no compitas por precio — compite por disponibilidad y servicio postventa. "
            f"Una rotura de stock aquí tiene impacto directo y crítico."
        )
    }

    # EFICIENTE
    if eficiente['Producto'] != estrella['Producto']:
        eficiente_body = (
            f"Con un ROI del <b>{eficiente['ROI_Porcentaje']:.1f}%</b>, es el mejor multiplicador de capital del catálogo "
            f"aunque no sea el líder en volumen. Por cada euro invertido en coste, devuelve "
            f"<b>{eficiente['ROI_Porcentaje']/100:.2f} €</b> de beneficio. "
            f"<br><br><b>Estrategia recomendada:</b> Escala las ventas de este producto — "
            f"aumentar su peso en el mix mejora la rentabilidad global sin necesidad de subir precios ni reducir costes."
        )
    else:
        eficiente_body = (
            f"El líder de ingresos coincide con el de mayor eficiencia (ROI <b>{eficiente['ROI_Porcentaje']:.1f}%</b>). "
            f"Posición muy sólida, pero también implica una concentración de riesgo elevada. "
            f"<br><br><b>Estrategia recomendada:</b> Diversifica potenciando el segundo producto más eficiente."
        )

    eficiente_card = {
        "titulo": f"📈 Máxima Eficiencia: {eficiente['Producto']}",
        "color":  "#28a745",
        "cuerpo": eficiente_body,
    }

    # BAJO RENDIMIENTO
    if bajo['ROI_Porcentaje'] < 0:
        bajo_detalle = (
            f"<b>ROI negativo: {bajo['ROI_Porcentaje']:.1f}%</b>. "
            f"Cada unidad vendida destruye <b>{abs(bajo['Rentabilidad_Total']):,.2f} €</b> de valor. "
            f"No es un problema de volumen — es un problema estructural de precio/coste."
            f"<br><br><b>Acción inmediata:</b> Congela los pedidos de este producto. "
            f"Sube el precio de venta al menos un {abs(bajo['ROI_Porcentaje']):.0f}% o negocia una reducción de coste equivalente."
        )
    elif bajo['ROI_Porcentaje'] < 10:
        bajo_detalle = (
            f"ROI de solo <b>{bajo['ROI_Porcentaje']:.1f}%</b> — apenas cubre costes y no justifica "
            f"el capital inmovilizado. El diferencial respecto al mejor ROI ({roi_max:.1f}%) es de "
            f"<b>{roi_max - bajo['ROI_Porcentaje']:.0f} puntos</b>."
            f"<br><br><b>Estrategia:</b> Evalúa una subida de precio del 10-15% o prepara la liquidación del stock."
        )
    else:
        bajo_detalle = (
            f"Con un ROI del <b>{bajo['ROI_Porcentaje']:.1f}%</b> es positivo pero el más débil del catálogo. "
            f"La brecha con el producto más eficiente ({roi_max:.1f}%) es de {roi_max - bajo['ROI_Porcentaje']:.0f} puntos."
            f"<br><br><b>Estrategia:</b> Revisa si los costes de adquisición se pueden reducir renegociando con el proveedor."
        )

    bajo_card = {
        "titulo": f"⚠️ Alerta de Rendimiento: {bajo['Producto']}",
        "color":  "#d9534f",
        "cuerpo": bajo_detalle,
    }

    return comentarios, estrella_card, eficiente_card, bajo_card


# ─────────────────────────────────────────────────────────────
# GENERACIÓN DE PDF PROFESIONAL CON REPORTLAB
# ─────────────────────────────────────────────────────────────
def generar_pdf(df, estrella, eficiente, bajo, total_neto, roi_medio,
                comentarios, tienda):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    base = getSampleStyleSheet()

    def sty(name, **kw):
        return ParagraphStyle(name, parent=base['Normal'], **kw)

    s_tit   = sty('tit',  fontSize=24, textColor=colors.HexColor('#0047AB'),
                  spaceAfter=4, alignment=TA_CENTER, fontName='Helvetica-Bold')
    s_sub   = sty('sub',  fontSize=11, textColor=colors.HexColor('#4a4a8a'),
                  spaceAfter=20, alignment=TA_CENTER)
    s_h2    = sty('h2',   fontSize=13, textColor=colors.HexColor('#0047AB'),
                  spaceBefore=16, spaceAfter=6, fontName='Helvetica-Bold')
    s_body  = sty('body', fontSize=10, textColor=colors.HexColor('#333333'),
                  spaceAfter=5, leading=16)
    s_bul   = sty('bul',  fontSize=10, textColor=colors.HexColor('#333333'),
                  spaceAfter=4, leading=15, leftIndent=14)
    s_foot  = sty('foot', fontSize=8,  textColor=colors.HexColor('#999999'),
                  alignment=TA_CENTER)
    s_badge = sty('badge',fontSize=11, textColor=colors.white,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')

    def p(txt, s):
        # convierte **x** → <b>x</b> y limpia HTML básico para ReportLab
        import re
        txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', txt)
        txt = txt.replace('<br><br>','<br/>').replace('<br>','<br/>')
        txt = re.sub(r'<(?!b>|/b>|br/>)[^>]+>', '', txt)  # quita otros tags HTML
        try:    return Paragraph(txt, s)
        except: return Paragraph(re.sub(r'<[^>]+>','',txt), s)

    h = []

    # ── CABECERA ──
    h.append(p("OptiMarket Pro", s_tit))
    h.append(p("Informe Estratégico de Rentabilidad", s_sub))
    h.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0047AB')))
    h.append(Spacer(1, 0.3*cm))
    tienda_txt = "Todas las tiendas" if tienda == "TODAS" else tienda
    h.append(p(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}  |  "
               f"<b>{tienda_txt}</b>  |  {len(df)} productos analizados", s_body))
    h.append(Spacer(1, 0.4*cm))

    # ── SALUD GENERAL (badge) ──
    colores_salud = {
        "excelente": colors.HexColor('#1b5e20'),
        "bueno":     colors.HexColor('#2e7d32'),
        "ajustado":  colors.HexColor('#e65100'),
        "crítico":   colors.HexColor('#b71c1c'),
    }
    salud = comentarios['salud']
    badge_data = [[p(f"Estado del negocio: {salud.upper()}", s_badge)]]
    badge = Table(badge_data, colWidths=[17*cm])
    badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), colores_salud.get(salud, colors.grey)),
        ('ROWHEIGHT',  (0,0),(-1,-1), 28),
        ('LEFTPADDING',(0,0),(-1,-1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    h.append(badge)
    h.append(Spacer(1, 0.2*cm))
    h.append(p(comentarios['salud_detalle'], s_body))
    h.append(Spacer(1, 0.4*cm))

    # ── KPIs ──
    h.append(p("Resumen Ejecutivo", s_h2))
    n_neg = comentarios['neg_count']
    kpi_data = [
        ["Indicador", "Valor"],
        ["Beneficio neto total",          f"{total_neto:,.2f} EUR"],
        ["ROI medio del catalogo",        f"{roi_medio:.1f}%"],
        ["Lider de ingresos",             str(estrella['Producto'])[:38]],
        ["Beneficio lider",               f"{estrella['Rentabilidad_Total']:,.2f} EUR"],
        ["ROI lider",                     f"{estrella['ROI_Porcentaje']:.1f}%"],
        ["Producto mas eficiente (ROI)",  str(eficiente['Producto'])[:38]],
        ["ROI maximo del catalogo",       f"{df['ROI_Porcentaje'].max():.1f}%"],
        ["ROI minimo del catalogo",       f"{df['ROI_Porcentaje'].min():.1f}%"],
        ["Productos con ROI negativo",    str(n_neg) + (" ⚠" if n_neg > 0 else " OK")],
    ]
    tk = Table(kpi_data, colWidths=[10*cm, 7*cm])
    tk.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0),  colors.HexColor('#0047AB')),
        ('TEXTCOLOR',     (0,0),(-1,0),  colors.white),
        ('FONTNAME',      (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 10),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f0f4ff'), colors.white]),
        ('ALIGN',         (1,0),(1,-1),  'RIGHT'),
        ('GRID',          (0,0),(-1,-1), 0.4, colors.HexColor('#cccccc')),
        ('ROWHEIGHT',     (0,0),(-1,-1), 20),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (0,0),(-1,-1), 8),
    ]))
    h.append(tk)
    h.append(Spacer(1, 0.5*cm))

    # ── TABLA DE PRODUCTOS ──
    h.append(p("Detalle por Producto", s_h2))
    df_sorted = df.sort_values('Rentabilidad_Total', ascending=False)
    rows = [["Producto", "PVP (EUR)", "Coste (EUR)", "Uds", "Beneficio (EUR)", "ROI (%)", "Margen (%)"]]
    for _, r in df_sorted.iterrows():
        margen_pct = (r['Margen'] / r['Precio_Venta'] * 100) if r['Precio_Venta'] else 0
        rows.append([
            str(r['Producto'])[:30],
            f"{r['Precio_Venta']:,.2f}",
            f"{r['Coste_Unidad']:,.2f}",
            f"{r['Ventas_Mes_Unidades']:,.0f}",
            f"{r['Rentabilidad_Total']:,.2f}",
            f"{r['ROI_Porcentaje']:.1f}%",
            f"{margen_pct:.1f}%",
        ])
    tp = Table(rows, colWidths=[5.5*cm,2.2*cm,2.2*cm,1.5*cm,2.8*cm,2*cm,1.8*cm])
    # Color rojo en filas con beneficio negativo
    style_cmds = [
        ('BACKGROUND',    (0,0),(-1,0),  colors.HexColor('#0047AB')),
        ('TEXTCOLOR',     (0,0),(-1,0),  colors.white),
        ('FONTNAME',      (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#f7f9ff'), colors.white]),
        ('ALIGN',         (1,0),(-1,-1), 'RIGHT'),
        ('GRID',          (0,0),(-1,-1), 0.3, colors.HexColor('#dddddd')),
        ('ROWHEIGHT',     (0,0),(-1,-1), 16),
        ('LEFTPADDING',   (0,0),(-1,-1), 5),
        ('RIGHTPADDING',  (0,0),(-1,-1), 5),
        # Top 3 verde
        ('BACKGROUND',    (0,1),(-1,1),  colors.HexColor('#c8e6c9')),
        ('BACKGROUND',    (0,2),(-1,2),  colors.HexColor('#dcedc8')),
        ('BACKGROUND',    (0,3),(-1,3),  colors.HexColor('#f1f8e9')),
    ]
    # Filas negativas en rojo claro
    for i, (_, r) in enumerate(df_sorted.iterrows(), start=1):
        if r['Rentabilidad_Total'] < 0:
            style_cmds.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#ffcdd2')))
    tp.setStyle(TableStyle(style_cmds))
    h.append(tp)
    h.append(Spacer(1, 0.5*cm))

    # ── ANÁLISIS ESTRATÉGICO ──
    h.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    h.append(Spacer(1, 0.2*cm))
    h.append(p("Analisis Estrategico", s_h2))

    h.append(p(f"<b>Diagnostico de concentracion:</b>", s_body))
    h.append(p(comentarios['txt_conc'].replace('<b>','').replace('</b>',''), s_bul))
    h.append(p(f"<b>Dispersion de rentabilidad:</b>", s_body))
    h.append(p(comentarios['txt_spread'].replace('<b>','').replace('</b>',''), s_bul))
    h.append(p(f"<b>Estado de productos:</b>", s_body))
    h.append(p(comentarios['txt_neg'].replace('<b>','').replace('</b>','').replace('⚠️','').replace('✅',''), s_bul))
    h.append(Spacer(1, 0.3*cm))

    for card_titulo, card_cuerpo in [
        (f"Lider de Ingresos: {estrella['Producto']}",
         f"Beneficio: {estrella['Rentabilidad_Total']:,.2f} EUR | ROI: {estrella['ROI_Porcentaje']:.1f}%"),
        (f"Maxima Eficiencia: {eficiente['Producto']}",
         f"ROI del {eficiente['ROI_Porcentaje']:.1f}% — mejor multiplicador de capital del catalogo."),
        (f"Alerta: {bajo['Producto']}",
         f"ROI mas bajo: {bajo['ROI_Porcentaje']:.1f}%. Evalua subida de precio o liquidacion."),
    ]:
        h.append(p(f"<b>{card_titulo}</b>", s_body))
        h.append(p(card_cuerpo, s_bul))
        h.append(Spacer(1, 0.2*cm))

    h.append(Spacer(1, 0.6*cm))
    h.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    h.append(Spacer(1, 0.2*cm))
    h.append(p("Informe generado por OptiMarket Pro · Analisis automatico sin dependencias externas", s_foot))

    doc.build(h)
    buf.seek(0)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
# SEGURIDAD
# ─────────────────────────────────────────────────────────────
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Privado")
    clave = st.text_input("Introduce la contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "SOCIO2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")

else:
    st.title("🚀 OptiMarket Pro — Intelligence")

    # ── SIDEBAR ──
    st.sidebar.title("⚙️ Configuración")
    archivo = st.sidebar.file_uploader("📂 Cargar datos de ventas", type=["xlsx","csv","xls"])

    if archivo:
        try:
            df_raw = (pd.read_csv(archivo, sep=None, engine='python')
                      if archivo.name.lower().endswith('.csv')
                      else pd.read_excel(archivo))
            df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]

            # ── DETECCIÓN DINÁMICA ──
            d_prod  = detectar(df_raw.columns, "producto")
            d_pvp   = detectar(df_raw.columns, "precio_venta")
            d_coste = detectar(df_raw.columns, "coste")
            d_cant  = detectar(df_raw.columns, "cantidad")
            d_tiend = detectar(df_raw.columns, "tienda")

            with st.sidebar.expander("🔍 Detección de columnas"):
                for n, v in [("Producto",d_prod),("Precio venta",d_pvp),
                              ("Coste",d_coste),("Cantidad",d_cant),("Tienda",d_tiend)]:
                    st.write(f"{'✅' if v else '❌'} **{n}:** {v or 'No detectado'}")

            lc  = list(df_raw.columns)
            idx = lambda c: lc.index(c) if c and c in lc else 0

            # ── 4 SELECTORES BÁSICOS ──
            st.sidebar.divider()
            col_prod  = st.sidebar.selectbox("🏷️ Producto",     lc, index=idx(d_prod))
            col_pvp   = st.sidebar.selectbox("💶 Precio venta", lc, index=idx(d_pvp))
            col_coste = st.sidebar.selectbox("💰 Coste",        lc, index=idx(d_coste))
            col_cant  = st.sidebar.selectbox("📦 Cantidad",     lc, index=idx(d_cant))

            tienda = "TODAS"
            if d_tiend:
                st.sidebar.divider()
                ops   = ["TODAS"] + sorted(df_raw[d_tiend].dropna().unique().tolist())
                tienda = st.sidebar.selectbox("📍 Tienda", ops)

            # ── PROCESAMIENTO ──
            df = df_raw.copy()
            if d_tiend and tienda != "TODAS":
                df = df[df[d_tiend] == tienda]

            df['Producto']             = df[col_prod].astype(str)
            df['Precio_Venta']         = pd.to_numeric(df[col_pvp],   errors='coerce').fillna(0)
            df['Coste_Unidad']         = pd.to_numeric(df[col_coste], errors='coerce').fillna(0)
            df['Ventas_Mes_Unidades']  = pd.to_numeric(df[col_cant],  errors='coerce').fillna(0)

            # Agrupar por producto (por si hay varias filas)
            df = df.groupby('Producto').agg({
                'Precio_Venta':        'mean',
                'Coste_Unidad':        'mean',
                'Ventas_Mes_Unidades': 'sum',
            }).reset_index()

            df['Margen']             = df['Precio_Venta'] - df['Coste_Unidad']
            df['Rentabilidad_Total'] = (df['Margen'] * df['Ventas_Mes_Unidades']).round(2)
            df['ROI_Porcentaje']     = (df['Margen'] / df['Coste_Unidad'].replace(0,1) * 100).round(2)
            df['Margen_Porcentaje']  = (df['Margen'] / df['Precio_Venta'].replace(0,1) * 100).round(2)
            df['Ticket_Medio']       = df['Precio_Venta'].round(2)

            total_neto = df['Rentabilidad_Total'].sum()
            roi_medio  = df['ROI_Porcentaje'].mean()
            estrella   = df.sort_values('Rentabilidad_Total', ascending=False).iloc[0]
            eficiente  = df.sort_values('ROI_Porcentaje',     ascending=False).iloc[0]
            bajo       = df.sort_values('ROI_Porcentaje',     ascending=True ).iloc[0]

            # ── KPIs CABECERA ──
            st.subheader(f"📍 {'Todas las tiendas' if tienda=='TODAS' else tienda}")
            k1,k2,k3,k4,k5,k6 = st.columns(6)
            roi_color = "normal" if roi_medio > 20 else "inverse"
            with k1: st.metric("💰 Beneficio neto",   f"{total_neto:,.2f} €",
                                delta=f"{'positivo' if total_neto>0 else 'negativo'}")
            with k2: st.metric("📈 ROI medio",         f"{roi_medio:.1f} %",
                                delta=f"{'bueno' if roi_medio>20 else 'revisar'}")
            with k3: st.metric("🥇 Líder ingresos",    str(estrella['Producto'])[:16])
            with k4: st.metric("⚡ Más eficiente",     str(eficiente['Producto'])[:16])
            with k5: st.metric("📦 Unidades totales",  f"{df['Ventas_Mes_Unidades'].sum():,.0f}")
            with k6: st.metric("⚠️ ROI mínimo",        f"{df['ROI_Porcentaje'].min():.1f} %",
                                delta=f"{'OK' if df['ROI_Porcentaje'].min()>=0 else 'negativo'}",
                                delta_color="inverse" if df['ROI_Porcentaje'].min()<0 else "normal")

            st.divider()

            # ── GRÁFICA 1: RENTABILIDAD CON SEMÁFORO ──
            g1, g2 = st.columns([2,1])
            with g1:
                st.subheader("📊 Rentabilidad Total por Producto")
                df_sorted = df.sort_values('Rentabilidad_Total', ascending=False)
                fig = px.bar(df_sorted, x='Producto', y='Rentabilidad_Total',
                             color='Rentabilidad_Total',
                             color_continuous_scale=[(0,"#d32f2f"),(0.5,"#fbc02d"),(1,"#388e3c")],
                             text_auto='.2s',
                             labels={'Rentabilidad_Total':'Beneficio (€)','Producto':''})
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>Beneficio: %{y:,.2f} €<br>ROI: %{customdata[0]:.1f}%',
                    customdata=df_sorted[['ROI_Porcentaje']].values)
                fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.4)
                fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False,
                                  xaxis_title="", yaxis_title="Beneficio (€)")
                st.plotly_chart(fig, use_container_width=True)

            with g2:
                st.subheader("🔴 Peores 5 productos")
                worst = df.nsmallest(5,'ROI_Porcentaje')
                fig2  = px.bar(worst.sort_values('ROI_Porcentaje'), x='ROI_Porcentaje', y='Producto',
                               orientation='h', color='ROI_Porcentaje',
                               color_continuous_scale='RdYlGn',
                               text_auto='.1f',
                               labels={'ROI_Porcentaje':'ROI (%)','Producto':''})
                fig2.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
                fig2.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig2, use_container_width=True)

            # ── GRÁFICA 2: ROI ──
            r1, r2, r3 = st.columns(3)
            with r1:
                st.subheader("📈 ROI por producto")
                rs  = df.sort_values('ROI_Porcentaje', ascending=False)
                clr = ['#d32f2f' if v<0 else '#f57c00' if v<15 else '#388e3c'
                       for v in rs['ROI_Porcentaje']]
                fig3 = go.Figure(go.Bar(
                    x=rs['Producto'], y=rs['ROI_Porcentaje'],
                    marker_color=clr,
                    text=[f"{v:.1f}%" for v in rs['ROI_Porcentaje']],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>ROI: %{y:.1f}%<extra></extra>'
                ))
                fig3.add_hline(y=0,       line_dash="dash",  line_color="black", opacity=0.4)
                fig3.add_hline(y=roi_medio,line_dash="dot",  line_color="#0047AB", opacity=0.6,
                               annotation_text=f"Media: {roi_medio:.1f}%",
                               annotation_position="top right")
                fig3.update_layout(xaxis_tickangle=-45, yaxis_title="ROI (%)", showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)

            with r2:
                st.subheader("💹 Margen % por producto")
                ms   = df.sort_values('Margen_Porcentaje', ascending=False)
                fig4 = px.bar(ms, x='Producto', y='Margen_Porcentaje',
                              color='Margen_Porcentaje', color_continuous_scale='RdYlGn',
                              text_auto='.1f',
                              labels={'Producto':'','Margen_Porcentaje':'Margen (%)'})
                fig4.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig4, use_container_width=True)

            with r3:
                st.subheader("🔵 Beneficio vs Coste total")
                df['Coste_Total'] = df['Coste_Unidad'] * df['Ventas_Mes_Unidades']
                fig5 = px.scatter(df, x='Coste_Total', y='Rentabilidad_Total',
                                  size='Ventas_Mes_Unidades', color='ROI_Porcentaje',
                                  color_continuous_scale='RdYlGn',
                                  hover_name='Producto',
                                  labels={'Coste_Total':'Coste total (€)',
                                          'Rentabilidad_Total':'Beneficio (€)',
                                          'ROI_Porcentaje':'ROI (%)'})
                fig5.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
                fig5.add_vline(x=df['Coste_Total'].median(), line_dash="dot",
                               line_color="gray", opacity=0.4)
                st.plotly_chart(fig5, use_container_width=True)

            # ── MAPA ESTRATÉGICO ──
            st.subheader("🗺️ Mapa de Rentabilidad Estratégica")
            st.caption("Tamaño = beneficio total · Color = ROI · Ideal: arriba a la derecha")
            roi_med2 = float(df['ROI_Porcentaje'].median())
            vol_med2 = float(df['Ventas_Mes_Unidades'].median())
            fig6 = px.scatter(df, x='Ventas_Mes_Unidades', y='ROI_Porcentaje',
                              size=df['Rentabilidad_Total'].abs().clip(lower=1),
                              color='ROI_Porcentaje',
                              color_continuous_scale='RdYlGn',
                              hover_name='Producto',
                              labels={'Ventas_Mes_Unidades':'Unidades vendidas',
                                      'ROI_Porcentaje':'ROI (%)'})
            fig6.add_vline(x=vol_med2, line_dash="dot", line_color="gray",  opacity=0.5)
            fig6.add_hline(y=roi_med2, line_dash="dot", line_color="gray",  opacity=0.5)
            fig6.add_hline(y=0,        line_dash="dash", line_color="red",   opacity=0.4)
            x_max = float(df['Ventas_Mes_Unidades'].max())
            y_max = float(df['ROI_Porcentaje'].max())
            fig6.add_annotation(x=x_max*0.85, y=y_max*0.92,
                                 text="⭐ Estrellas", showarrow=False,
                                 font=dict(color="#2e7d32", size=11))
            fig6.add_annotation(x=x_max*0.85, y=roi_med2*0.15,
                                 text="⚠️ Volumen sin margen", showarrow=False,
                                 font=dict(color="#e65100", size=11))
            st.plotly_chart(fig6, use_container_width=True)

            # ── DIAGNÓSTICO IA ──
            st.divider()
            st.header("🧠 Diagnóstico de Consultoría IA")

            comentarios, estrella_card, eficiente_card, bajo_card = \
                generar_comentarios(df, estrella, eficiente, bajo, total_neto, roi_medio)

            # Banner de salud
            colores_banner = {
                "excelente":"#1b5e20","bueno":"#2e7d32","ajustado":"#e65100","crítico":"#b71c1c"
            }
            bg_banner = colores_banner.get(comentarios['salud'],"#333")
            st.markdown(
                f"<div style='background:{bg_banner};color:white;padding:14px 20px;border-radius:10px;"
                f"font-size:15px;font-weight:bold;margin-bottom:16px;'>"
                f"Estado general del negocio: {comentarios['salud'].upper()} · "
                f"{comentarios['salud_detalle']}</div>",
                unsafe_allow_html=True
            )

            # Concentración y dispersión
            col_ia1, col_ia2 = st.columns(2)
            with col_ia1:
                st.markdown(
                    f"<div class='report-card'><h4>📊 Concentración de beneficio</h4>"
                    f"<p>{comentarios['txt_conc']}</p></div>",
                    unsafe_allow_html=True)
            with col_ia2:
                st.markdown(
                    f"<div class='report-card' style='border-left-color:#7b1fa2'>"
                    f"<h4 style='color:#7b1fa2'>📐 Dispersión de ROI</h4>"
                    f"<p>{comentarios['txt_spread']}<br><br>{comentarios['txt_neg']}</p></div>",
                    unsafe_allow_html=True)

            # Tarjetas individuales
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown(
                    f"<div class='report-card'><h4>{estrella_card['titulo']}</h4>"
                    f"<p>{estrella_card['cuerpo']}</p></div>",
                    unsafe_allow_html=True)
            with col_c2:
                st.markdown(
                    f"<div class='report-card' style='border-left-color:{eficiente_card['color']}'>"
                    f"<h4 style='color:{eficiente_card['color']}'>{eficiente_card['titulo']}</h4>"
                    f"<p>{eficiente_card['cuerpo']}</p></div>",
                    unsafe_allow_html=True)

            st.markdown(
                f"<div class='report-card' style='border-left-color:{bajo_card['color']}'>"
                f"<h4 style='color:{bajo_card['color']}'>{bajo_card['titulo']}</h4>"
                f"<p>{bajo_card['cuerpo']}</p></div>",
                unsafe_allow_html=True)

            # ── TABLA COMPLETA ──
            with st.expander("🗂️ Ver tabla completa de datos"):
                display_df = df[['Producto','Precio_Venta','Coste_Unidad',
                                  'Ventas_Mes_Unidades','Margen',
                                  'Rentabilidad_Total','ROI_Porcentaje','Margen_Porcentaje']].copy()
                display_df.columns = ['Producto','PVP (€)','Coste (€)',
                                       'Uds','Margen unit. (€)',
                                       'Beneficio total (€)','ROI (%)','Margen (%)']
                st.dataframe(display_df.sort_values('Beneficio total (€)', ascending=False),
                             use_container_width=True)

            # ── EXPORTACIÓN ──
            st.sidebar.divider()
            st.sidebar.subheader("📤 Exportar")

            if st.sidebar.button("📄 Generar informe PDF", type="primary"):
                with st.spinner("Generando PDF profesional..."):
                    pdf_bytes = generar_pdf(
                        df, estrella, eficiente, bajo,
                        total_neto, roi_medio, comentarios, tienda
                    )
                nombre = f"OptiMarket_{tienda}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.sidebar.download_button(
                    "⬇️ Descargar PDF", pdf_bytes, nombre,
                    "application/pdf", type="primary"
                )

            st.sidebar.download_button(
                "📊 Exportar CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"OptiMarket_datos_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            st.exception(e)

    else:
        st.info("👋 Bienvenido/a a OptiMarket Pro. Carga tu archivo de ventas en el panel lateral para iniciar el diagnóstico.")
