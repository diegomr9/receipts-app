import io, os, datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, KeepTogether
from ui import STATUS_ES, CAT_ES, fecha, money

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
for n, f in [("Serif", "Cormorant-Regular.ttf"), ("SerifLight", "Cormorant-Light.ttf"), ("Sans", "Jost-Regular.ttf"), ("SansMed", "Jost-Medium.ttf")]:
    try: pdfmetrics.registerFont(TTFont(n, os.path.join(F, f)))
    except Exception: pass
OK = "Serif" in pdfmetrics.getRegisteredFontNames()
SERIF, LIGHT, SANS = ("Serif", "SerifLight", "Sans") if OK else ("Times-Roman", "Times-Roman", "Helvetica")
INK, STONE, LINE, SAND = colors.HexColor("#313131"), colors.HexColor("#82847f"), colors.HexColor("#d5d1c8"), colors.HexColor("#f3eee7")

def sp(text, n=1.8):  # simulated letter-spacing for small caps labels
    return text.upper()

LBL = ParagraphStyle("lbl", fontName=SANS, fontSize=7.5, textColor=STONE, leading=11, alignment=TA_CENTER)
TITLE = ParagraphStyle("t", fontName=LIGHT, fontSize=40, leading=46, textColor=INK, alignment=TA_CENTER)
BODY = ParagraphStyle("b", fontName=SANS, fontSize=9, leading=14, textColor=INK)
H = ParagraphStyle("h", fontName=SERIF, fontSize=22, leading=26, textColor=INK)
CELL = ParagraphStyle("c", fontName=SANS, fontSize=8.5, leading=12, textColor=INK)
CELLS = ParagraphStyle("cs", fontName=SERIF, fontSize=12, leading=14, textColor=INK)

def _page(c, doc):
    w, h = A4
    c.saveState(); c.setFillColor(SAND); c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line(20*mm, h-18*mm, w-20*mm, h-18*mm); c.line(20*mm, 16*mm, w-20*mm, 16*mm)
    c.setFillColor(INK); c.setFont(SERIF, 11); c.drawCentredString(w/2, h-14*mm, "R E C E I P T S")
    c.setFillColor(STONE); c.setFont(SANS, 7)
    c.drawString(20*mm, 11*mm, "EXPENSE REPORT"); c.drawRightString(w-20*mm, 11*mm, f"PAGE {doc.page}")
    c.restoreState()

def build_pdf(rows, thumbs_dir):
    buf = io.BytesIO(); w, h = A4
    doc = BaseDocTemplate(buf, pagesize=A4, title="Expense report", leftMargin=20*mm, rightMargin=20*mm, topMargin=28*mm, bottomMargin=24*mm)
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=_page)])
    tot = {}
    for r in rows: tot[r["currency"]] = tot.get(r["currency"], 0) + r["amount"]
    dates = sorted(r["date"] for r in rows if r["date"])
    hoy = fecha(datetime.date.today().isoformat())
    el = [Spacer(1, 18*mm), Paragraph("WORK EXPENSES &nbsp;·&nbsp; REIMBURSEMENT CLAIM", LBL), Spacer(1, 6*mm),
          Paragraph("Expense report", TITLE), Spacer(1, 5*mm),
          Paragraph(f"{len(rows)} {'receipt' if len(rows)==1 else 'receipts'}" + (f" &nbsp;·&nbsp; {fecha(dates[0])} – {fecha(dates[-1])}" if dates else "") + f" &nbsp;·&nbsp; issued {hoy}", LBL),
          Spacer(1, 12*mm)]
    totline = " &nbsp;&nbsp; ".join(f"{money(v)} <font name='{SANS}' size='8' color='#82847f'>{c}</font>" for c, v in tot.items()) or "0,00"
    el += [Paragraph("TOTAL", LBL), Spacer(1, 2*mm), Paragraph(totline, ParagraphStyle("tt", parent=TITLE, fontSize=30, leading=36)), Spacer(1, 14*mm)]
    hdr = [Paragraph(x, ParagraphStyle("hh", parent=LBL, alignment=a)) for x, a in
           [("NO.", 0), ("DATE", 0), ("DESCRIPTION", 0), ("CATEGORY", 0), ("STATUS", 0), ("AMOUNT", TA_RIGHT)]]
    data = [hdr]
    for i, r in enumerate(rows, 1):
        data.append([Paragraph(str(i), CELL), Paragraph(fecha(r["date"]), CELL), Paragraph((r["title"] or r["merchant"] or "—") + (f"<br/><font name='{SANS}' size='7' color='#82847f'>{r['merchant']}</font>" if r["title"] and r["merchant"] else ""), CELLS),
                     Paragraph(CAT_ES.get(r["category"], r["category"]), CELL), Paragraph(STATUS_ES.get(r["status"], r["status"]), CELL),
                     Paragraph(f"{money(r['amount'])} <font size='7' color='#82847f'>{r['currency']}</font>", ParagraphStyle("a", parent=CELLS, alignment=TA_RIGHT))])
    t = Table(data, colWidths=[10*mm, 26*mm, 52*mm, 26*mm, 26*mm, 30*mm], repeatRows=1)
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("LINEABOVE", (0, 0), (-1, 0), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
    el.append(t)
    for i, r in enumerate(rows, 1):
        block = [Paragraph(f"RECEIPT {i} OF {len(rows)} &nbsp;·&nbsp; {CAT_ES.get(r['category'], r['category']).upper()} &nbsp;·&nbsp; {STATUS_ES.get(r['status'], r['status']).upper()}", ParagraphStyle("l2", parent=LBL, alignment=0)),
                 Spacer(1, 3*mm), Paragraph(r["title"] or r["merchant"] or "—", H), Spacer(1, 1*mm),
                 Paragraph((f"{r['merchant']} &nbsp;·&nbsp; " if r["title"] and r["merchant"] else "") + f"{fecha(r['date'])} &nbsp;·&nbsp; <font name='{SERIF}' size='14'>{money(r['amount'])}</font> {r['currency']}", BODY)]
        if r["notes"]: block += [Spacer(1, 2*mm), Paragraph(f"<font color='#82847f'>Notes:</font> {r['notes']}", BODY)]
        el += [PageBreak()] + block + [Spacer(1, 7*mm)]
        if r["preview"]:
            p = os.path.join(thumbs_dir, r["preview"])
            if os.path.exists(p):
                iw, ih = Image.open(p).size; s = min(doc.width/iw, 175*mm/ih)
                img = RLImage(p, iw*s, ih*s)
                fr = Table([[img]], style=[("BOX", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#faf8f4")),
                           ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)])
                el.append(fr)
    doc.build(el)
    return buf.getvalue()
