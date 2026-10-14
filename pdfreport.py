import io, os, datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from ui import STATUS_ES, CAT_ES, fecha, money

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
try:
    pdfmetrics.registerFont(TTFont("Inter", os.path.join(F, "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-SB", os.path.join(F, "Inter-SemiBold.ttf")))
    R, B = "Inter", "Inter-SB"
except Exception:
    R, B = "Helvetica", "Helvetica-Bold"
TEXT, TEXT2, MUTED = colors.HexColor("#101828"), colors.HexColor("#475467"), colors.HexColor("#667085")
BORDER, SUBTLE, ACCENT = colors.HexColor("#e4e7ec"), colors.HexColor("#f6f7f9"), colors.HexColor("#3538cd")
PILL = {"to submit": "#b54708", "submitted": "#175cd3", "reimbursed": "#067647"}

def st(name, parent=None, **kw):
    if parent is not None: return ParagraphStyle(name, parent=parent, **kw)
    base = dict(fontName=R, fontSize=9, leading=13, textColor=TEXT); base.update(kw); return ParagraphStyle(name, **base)
SMALL = st("s", fontSize=7.5, leading=10, textColor=MUTED)
CELL = st("c", fontSize=8.5, leading=11.5)
CELLB = st("cb", fontName=B, fontSize=8.5, leading=11.5)
HDR = st("h", fontName=B, fontSize=7, leading=9, textColor=MUTED)

def _page(c, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(ACCENT); c.rect(0, h - 4, w, 4, stroke=0, fill=1)
    c.setFillColor(TEXT); c.setFont(B, 9.5); c.drawString(18*mm, h - 14*mm, "Receipts")
    c.setFillColor(MUTED); c.setFont(R, 8); c.drawRightString(w - 18*mm, h - 14*mm, "Expense report")
    c.setStrokeColor(BORDER); c.setLineWidth(0.6); c.line(18*mm, h - 17*mm, w - 18*mm, h - 17*mm)
    c.line(18*mm, 14*mm, w - 18*mm, 14*mm)
    c.setFont(R, 7.5); c.drawString(18*mm, 9.5*mm, f"Generated {fecha(datetime.date.today().isoformat())}")
    c.drawRightString(w - 18*mm, 9.5*mm, f"Page {doc.page}")
    c.restoreState()

def _card(content, width, pad=10):
    t = Table([[content]], colWidths=[width])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), pad), ("RIGHTPADDING", (0, 0), (-1, -1), pad), ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad)]))
    return t

def build_pdf(rows, thumbs_dir):
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, title="Expense report", author="Receipts", leftMargin=18*mm, rightMargin=18*mm, topMargin=24*mm, bottomMargin=20*mm)
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=_page)])
    W = doc.width
    tot, bys = {}, {}
    for r in rows:
        tot[r["currency"]] = tot.get(r["currency"], 0) + r["amount"]
        bys.setdefault(r["status"], {}).setdefault(r["currency"], 0); bys[r["status"]][r["currency"]] += r["amount"]
    dates = sorted(r["date"] for r in rows if r["date"])
    period = f"{fecha(dates[0])} – {fecha(dates[-1])}" if dates else "—"
    el = [Paragraph("Expense report", st("t", fontName=B, fontSize=20, leading=24)), Spacer(1, 2*mm),
          Paragraph(f"Reimbursement claim · {len(rows)} {'receipt' if len(rows)==1 else 'receipts'} · {period}", st("sub", fontSize=9.5, textColor=TEXT2)), Spacer(1, 7*mm)]
    # summary cards
    def amt_lines(d): return "<br/>".join(f"<font name='{B}' size='13'>{money(v)}</font> <font size='8' color='#667085'>{c}</font>" for c, v in d.items()) or f"<font name='{B}' size='13'>0.00</font>"
    cells = [[Paragraph("TOTAL CLAIMED", HDR), Paragraph("TO SUBMIT", HDR), Paragraph("SUBMITTED", HDR), Paragraph("REIMBURSED", HDR)],
             [Paragraph(amt_lines(tot), st("v", leading=17)), Paragraph(amt_lines(bys.get("to submit", {})), st("v1", leading=17)),
              Paragraph(amt_lines(bys.get("submitted", {})), st("v2", leading=17)), Paragraph(amt_lines(bys.get("reimbursed", {})), st("v3", leading=17))]]
    sc = Table(cells, colWidths=[W/4]*4)
    sc.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("LINEAFTER", (0, 0), (-2, -1), 0.6, BORDER), ("BACKGROUND", (0, 0), (-1, -1), SUBTLE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef0ff")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, -1), (-1, -1), 10)]))
    el += [sc, Spacer(1, 8*mm), Paragraph("Receipts", st("h2", fontName=B, fontSize=11, leading=14)), Spacer(1, 3*mm)]
    data = [[Paragraph(x, HDR if x != "AMOUNT" else st("hr", parent=HDR, alignment=TA_RIGHT)) for x in ["#", "DATE", "DESCRIPTION", "CATEGORY", "STATUS", "AMOUNT"]]]
    for i, r in enumerate(rows, 1):
        desc = f"<font name='{B}'>{r['title'] or r['merchant'] or '—'}</font>" + (f"<br/><font size='7.5' color='#667085'>{r['merchant']}</font>" if r["title"] and r["merchant"] else "")
        data.append([Paragraph(str(i), st("n", fontSize=8.5, textColor=MUTED)), Paragraph(fecha(r["date"]), CELL), Paragraph(desc, CELL),
                     Paragraph(CAT_ES.get(r["category"], r["category"]), CELL),
                     Paragraph(f"<font color='{PILL.get(r['status'], '#475467')}'>● </font>{STATUS_ES.get(r['status'], r['status'])}", CELL),
                     Paragraph(f"{money(r['amount'])} <font size='7.5' color='#667085'>{r['currency']}</font>", st("a", parent=CELLB, alignment=TA_RIGHT))])
    for c, v in tot.items():
        data.append(["", "", Paragraph("Total", CELLB), "", "", Paragraph(f"{money(v)} <font size='7.5' color='#667085'>{c}</font>", st("ta", parent=CELLB, alignment=TA_RIGHT))])
    n = len(rows)
    t = Table(data, colWidths=[8*mm, 24*mm, W - 8*mm - 24*mm - 24*mm - 26*mm - 32*mm, 24*mm, 26*mm, 32*mm], repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), SUBTLE), ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER), ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
             ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if tot: style += [("BACKGROUND", (0, n + 1), (-1, -1), colors.HexColor("#eef0ff")), ("LINEABOVE", (0, n + 1), (-1, n + 1), 0.8, ACCENT)]
    t.setStyle(TableStyle(style)); el.append(t)
    el += [Spacer(1, 5*mm), Paragraph("Each receipt is attached on the following pages. Amounts are shown in their original currency; no conversion applied.", SMALL)]
    for i, r in enumerate(rows, 1):
        el.append(PageBreak())
        el.append(Paragraph(f"RECEIPT {i} OF {n}", HDR)); el.append(Spacer(1, 2*mm))
        el.append(Paragraph(r["title"] or r["merchant"] or "—", st("rt", fontName=B, fontSize=15, leading=19))); el.append(Spacer(1, 4*mm))
        meta = [[Paragraph("MERCHANT", HDR), Paragraph("DATE", HDR), Paragraph("CATEGORY", HDR), Paragraph("STATUS", HDR), Paragraph("AMOUNT", st("hr2", parent=HDR, alignment=TA_RIGHT))],
                [Paragraph(r["merchant"] or "—", CELL), Paragraph(fecha(r["date"]), CELL), Paragraph(CAT_ES.get(r["category"], r["category"]), CELL),
                 Paragraph(STATUS_ES.get(r["status"], r["status"]), CELL), Paragraph(f"{money(r['amount'])} {r['currency']}", st("ma", parent=CELLB, fontSize=11, alignment=TA_RIGHT))]]
        mt = Table(meta, colWidths=[W*0.30, W*0.17, W*0.17, W*0.16, W*0.20])
        mt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("BACKGROUND", (0, 0), (-1, 0), SUBTLE), ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        el.append(mt)
        if r["notes"]: el += [Spacer(1, 3*mm), Paragraph(f"<font name='{B}'>Notes</font> &nbsp;{r['notes']}", st("nt", textColor=TEXT2))]
        el.append(Spacer(1, 5*mm))
        if r["preview"]:
            p = os.path.join(thumbs_dir, r["preview"])
            if os.path.exists(p):
                iw, ih = Image.open(p).size; s = min((W - 20) / iw, 165*mm / ih)
                el.append(_card(RLImage(p, iw*s, ih*s), W))
    doc.build(el)
    return buf.getvalue()
