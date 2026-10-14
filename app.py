import os, re, io, csv, sqlite3, subprocess, uuid, datetime
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory, Response, g, flash
from PIL import Image
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DATA_DIR", BASE)
UP = os.path.join(DATA, "uploads"); TH = os.path.join(DATA, "thumbs")
for d in (UP, TH): os.makedirs(d, exist_ok=True)
DB = os.path.join(DATA, "receipts.db")
CATS = ["meals","travel","transport","lodging","supplies","other"]
STATUSES = ["to submit","submitted","reimbursed"]
import json, datetime as _dt
from werkzeug.security import check_password_hash
from flask import session
_cf = os.path.join(BASE, "config.json")
CFG = json.load(open(_cf)) if os.path.exists(_cf) else {}
CFG["password_hash"] = os.environ.get("PASSWORD_HASH") or CFG.get("password_hash")
CFG["secret_key"] = os.environ.get("SECRET_KEY") or CFG.get("secret_key")
if not CFG["password_hash"] or not CFG["secret_key"]:
    raise SystemExit("Set PASSWORD_HASH and SECRET_KEY env vars (or provide config.json)")
app = Flask(__name__); app.secret_key = CFG["secret_key"]
app.config.update(MAX_CONTENT_LENGTH=25*1024*1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") == "1",
                  PERMANENT_SESSION_LIFETIME=_dt.timedelta(days=30))
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
FAILS = {}
@app.before_request
def require_login():
    if request.endpoint in ("login", "static", "healthz") or session.get("ok"): return
    return redirect(url_for("login"))
@app.errorhandler(413)
def too_big(e): return "File too large (max 25 MB). <a href='/'>Back</a>", 413

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS receipts(id INTEGER PRIMARY KEY, date TEXT, merchant TEXT,
          amount REAL, currency TEXT DEFAULT 'EUR', category TEXT DEFAULT 'other', notes TEXT DEFAULT '',
          status TEXT DEFAULT 'to submit', file TEXT, preview TEXT, ocr_text TEXT, created TEXT)""")
    return g.db
@app.teardown_appcontext
def close(e):
    d = g.pop("db", None)
    if d: d.commit(); d.close()

def make_preview(path):
    """Return filename of a PNG preview (thumbnail dir) for image or PDF."""
    name = uuid.uuid4().hex
    if path.lower().endswith(".pdf"):
        out = os.path.join(TH, name)
        subprocess.run(["pdftoppm","-png","-r","120","-f","1","-l","1","-singlefile",path,out], check=False)
        src = out + ".png"
        if not os.path.exists(src): return None
        img = Image.open(src)
    else:
        img = Image.open(path)
    img = img.convert("RGB"); img.thumbnail((1400,1400))
    fn = name + "_p.jpg"; img.save(os.path.join(TH, fn), quality=85)
    return fn

def ocr(preview):
    try:
        import pytesseract
        return pytesseract.image_to_string(Image.open(os.path.join(TH, preview)))
    except Exception: return ""

def parse(text):
    r = {}
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 2]
    if lines: r["merchant"] = lines[0][:60]
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", text)
    if m: r["date"] = "%s-%02d-%02d" % (m[1], int(m[2]), int(m[3]))
    else:
        m = re.search(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})", text)
        if m:
            y = int(m[3]); y = y + 2000 if y < 100 else y
            try: r["date"] = datetime.date(y, int(m[2]), int(m[1])).isoformat()
            except ValueError: pass
    amt = None
    for l in text.splitlines():
        if re.search(r"total|amount|importe|sum", l, re.I) and not re.search(r"sub", l, re.I):
            n = re.findall(r"\d+[.,]\d{2}", l)
            if n: amt = n[-1]
    if not amt:
        n = re.findall(r"\d+[.,]\d{2}", text)
        if n: amt = max(n, key=lambda x: float(x.replace(",", ".")))
    if amt: r["amount"] = float(amt.replace(",", "."))
    for cur, pat in [("EUR", r"€|EUR"), ("USD", r"\$|USD"), ("GBP", r"£|GBP")]:
        if re.search(pat, text): r["currency"] = cur; break
    low = text.lower()
    for cat, kws in [("meals",["restaurant","cafe","coffee","lunch","dinner","food"]),("lodging",["hotel","inn","night"]),
                     ("travel",["airline","flight","train","rail"]),("transport",["taxi","uber","fuel","parking","metro"]),
                     ("supplies",["office","paper","staples","printer"])]:
        if any(k in low for k in kws): r["category"] = cat; break
    return r

def add_receipt(path, fields=None):
    prev = make_preview(path)
    text = ocr(prev) if prev else ""
    f = parse(text); f.update(fields or {})
    cur = db().execute("INSERT INTO receipts(date,merchant,amount,currency,category,notes,status,file,preview,ocr_text,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (f.get("date", datetime.date.today().isoformat()), f.get("merchant",""), f.get("amount",0) or 0, f.get("currency","EUR"),
         f.get("category","other"), f.get("notes",""), f.get("status","to submit"), os.path.basename(path), prev, text, datetime.datetime.now().isoformat()))
    return cur.lastrowid

def query(args):
    sql, p = "SELECT * FROM receipts WHERE 1=1", []
    if args.get("status"): sql += " AND status=?"; p.append(args["status"])
    if args.get("start"): sql += " AND date>=?"; p.append(args["start"])
    if args.get("end"): sql += " AND date<=?"; p.append(args["end"])
    return db().execute(sql + " ORDER BY date DESC, id DESC", p).fetchall()

def selected(form):
    ids = [int(i) for i in form.getlist("ids")]
    if ids: return db().execute("SELECT * FROM receipts WHERE id IN (%s) ORDER BY date" % ",".join("?"*len(ids)), ids).fetchall()
    return list(reversed(query(form)))

CSS = """<meta name=viewport content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box}body{font-family:system-ui,sans-serif;margin:0;background:#f4f6f8;color:#222}
header{background:#1f6feb;color:#fff;padding:14px 18px}header a{color:#fff;text-decoration:none;font-weight:600;font-size:20px}
main{max-width:1000px;margin:auto;padding:14px}.card{background:#fff;border-radius:10px;padding:14px;margin-bottom:14px;box-shadow:0 1px 3px #0002}
input,select,textarea,button{font:inherit;padding:8px;border:1px solid #ccc;border-radius:6px}button{background:#1f6feb;color:#fff;border:0;cursor:pointer}
button.sec{background:#6e7781}.row{display:flex;flex-wrap:wrap;gap:8px;align-items:end}.row label{display:flex;flex-direction:column;font-size:13px;gap:3px}
.tot{display:flex;gap:10px;flex-wrap:wrap}.tot div{flex:1;min-width:140px;background:#fff;border-radius:10px;padding:12px;box-shadow:0 1px 3px #0002}
.tot b{display:block;font-size:20px}.item{display:flex;gap:12px;align-items:center;padding:10px 0;border-bottom:1px solid #eee}
.item img{width:64px;height:64px;object-fit:cover;border-radius:6px;background:#ddd}.grow{flex:1}.amt{font-weight:600;white-space:nowrap}
.badge{font-size:12px;padding:2px 8px;border-radius:10px;background:#eee}.b-to{background:#fff3cd}.b-submitted{background:#cfe2ff}.b-reimbursed{background:#d1e7dd}
.flash{background:#d1e7dd;padding:10px;border-radius:8px;margin-bottom:10px}a{color:#1f6feb}
</style>"""
INDEX = CSS + """<title>Receipts</title><header><a href="/">🧾 My Receipts</a></header><main>
<div style="text-align:right"><a href="/logout">Log out</a></div>{% for m in get_flashed_messages() %}<div class=flash>{{m}}</div>{% endfor %}
<div class=card><form method=post action="/upload" enctype=multipart/form-data class=row>
<label>Add receipt (photo or PDF)<input type=file name=file accept="image/*,application/pdf" capture="environment" required multiple></label>
<button>Upload &amp; auto-fill</button></form></div>
<div class=tot>{% for s in statuses %}<div>{{s|capitalize}}<b>{% for c,v in totals[s].items() %}{{"%.2f"|format(v)}} {{c}}<br>{% else %}0.00{% endfor %}</b><small>{{counts[s]}} receipt(s)</small></div>{% endfor %}</div><br>
<div class=card><form method=get class=row>
<label>Status<select name=status><option value="">All</option>{% for s in statuses %}<option {{'selected' if a.status==s}}>{{s}}</option>{% endfor %}</select></label>
<label>From<input type=date name=start value="{{a.start or ''}}"></label><label>To<input type=date name=end value="{{a.end or ''}}"></label>
<button>Filter</button><a href="/">Clear</a></form></div>
<form method=post class=card>
<input type=hidden name=status value="{{a.status or ''}}"><input type=hidden name=start value="{{a.start or ''}}"><input type=hidden name=end value="{{a.end or ''}}">
<div class=row><label style="flex-direction:row;align-items:center"><input type=checkbox onclick="document.querySelectorAll('.ck').forEach(c=>c.checked=this.checked)"> Select all</label>
<button formaction="/bulk?to=submitted">Mark submitted</button><button formaction="/bulk?to=reimbursed">Mark reimbursed</button>
<button class=sec formaction="/export.csv">Export CSV</button><button class=sec formaction="/export.pdf">Export PDF report</button></div>
<small>Exports use the selected receipts, or all filtered ones if none are selected.</small>
{% for r in rows %}<div class=item><input type=checkbox class=ck name=ids value={{r.id}}>
<a href="/edit/{{r.id}}"><img src="/thumbs/{{r.preview}}" alt=""></a>
<div class=grow><a href="/edit/{{r.id}}"><b>{{r.merchant or '(no merchant)'}}</b></a><br><small>{{r.date}} · {{r.category}}</small>
 <span class="badge b-{{r.status.split()[0]}}">{{r.status}}</span></div><div class=amt>{{"%.2f"|format(r.amount)}} {{r.currency}}</div></div>
{% else %}<p>No receipts yet.</p>{% endfor %}</form></main>"""
EDIT = CSS + """<title>Edit receipt</title><header><a href="/">🧾 My Receipts</a></header><main><div class=card>
<a href="/uploads/{{r.file}}" target=_blank><img src="/thumbs/{{r.preview}}" style="max-width:100%;max-height:420px;border-radius:8px"></a>
<form method=post class=row style="margin-top:10px">
<label>Date<input type=date name=date value="{{r.date}}"></label><label>Merchant<input name=merchant value="{{r.merchant}}"></label>
<label>Amount<input type=number step=0.01 name=amount value="{{r.amount}}"></label><label>Currency<input name=currency value="{{r.currency}}" size=4></label>
<label>Category<select name=category>{% for c in cats %}<option {{'selected' if r.category==c}}>{{c}}</option>{% endfor %}</select></label>
<label>Status<select name=status>{% for s in statuses %}<option {{'selected' if r.status==s}}>{{s}}</option>{% endfor %}</select></label>
<label style="flex-basis:100%">Notes<textarea name=notes rows=2>{{r.notes}}</textarea></label>
<button>Save</button><button class=sec formaction="/delete/{{r.id}}" onclick="return confirm('Delete this receipt?')">Delete</button></form>
{% if r.ocr_text %}<details><summary>OCR text</summary><pre style="white-space:pre-wrap">{{r.ocr_text}}</pre></details>{% endif %}</div></main>"""

LOGIN = CSS + """<title>Login</title><header><a href="/">🧾 My Receipts</a></header><main><div class=card>
{% if err %}<div class=flash style="background:#f8d7da">{{err}}</div>{% endif %}
<form method=post class=row><label>Password<input type=password name=password autofocus required></label><button>Log in</button></form></div></main>"""
@app.route("/login", methods=["GET","POST"])
def login():
    err = None
    if request.method == "POST":
        ip = request.remote_addr
        n, t = FAILS.get(ip, (0, 0))
        import time
        if n >= 5 and time.time() - t < 300: err = "Too many attempts, wait 5 minutes."
        elif check_password_hash(CFG["password_hash"], request.form.get("password","")):
            FAILS.pop(ip, None); session.clear(); session["ok"] = True; session.permanent = True; return redirect("/")
        else: FAILS[ip] = (n+1, time.time()); err = "Wrong password."
    return render_template_string(LOGIN, err=err)
@app.get("/healthz")
def healthz(): return "ok"

@app.get("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/")
def index():
    rows = query(request.args)
    totals = {s:{} for s in STATUSES}; counts = {s:0 for s in STATUSES}
    for r in rows:
        if r["status"] in totals:
            totals[r["status"]][r["currency"]] = totals[r["status"]].get(r["currency"],0) + r["amount"]; counts[r["status"]] += 1
    return render_template_string(INDEX, rows=rows, totals=totals, counts=counts, statuses=STATUSES, a=request.args)

@app.post("/upload")
def upload():
    last = None
    for f in request.files.getlist("file"):
        if not f.filename: continue
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        path = os.path.join(UP, uuid.uuid4().hex + ext); f.save(path)
        last = add_receipt(path)
    if last: flash("Uploaded. Check the auto-filled fields."); return redirect(url_for("edit", rid=last))
    return redirect("/")

@app.route("/edit/<int:rid>", methods=["GET","POST"])
def edit(rid):
    if request.method == "POST":
        f = request.form
        db().execute("UPDATE receipts SET date=?,merchant=?,amount=?,currency=?,category=?,notes=?,status=? WHERE id=?",
            (f["date"], f["merchant"], float(f["amount"] or 0), f["currency"].upper(), f["category"], f["notes"], f["status"], rid))
        flash("Saved."); return redirect("/")
    r = db().execute("SELECT * FROM receipts WHERE id=?", (rid,)).fetchone()
    return render_template_string(EDIT, r=r, cats=CATS, statuses=STATUSES) if r else ("Not found", 404)

@app.post("/delete/<int:rid>")
def delete(rid):
    db().execute("DELETE FROM receipts WHERE id=?", (rid,)); flash("Deleted."); return redirect("/")

@app.post("/bulk")
def bulk():
    to = request.args.get("to"); ids = [int(i) for i in request.form.getlist("ids")]
    if to in STATUSES and ids:
        db().execute("UPDATE receipts SET status=? WHERE id IN (%s)" % ",".join("?"*len(ids)), [to]+ids)
        flash(f"Marked {len(ids)} receipt(s) as {to}.")
    else: flash("Select at least one receipt.")
    return redirect("/")

@app.post("/export.csv")
def export_csv():
    out = io.StringIO(); w = csv.writer(out)
    w.writerow(["id","date","merchant","amount","currency","category","status","notes","file"])
    for r in selected(request.form):
        w.writerow([r["id"],r["date"],r["merchant"],"%.2f"%r["amount"],r["currency"],r["category"],r["status"],r["notes"],r["file"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=receipts.csv"})

@app.post("/export.pdf")
def export_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    rows = selected(request.form); ss = getSampleStyleSheet(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Expense report")
    el = [Paragraph("Expense claim report", ss["Title"]), Paragraph("Generated " + datetime.date.today().isoformat(), ss["Normal"]), Spacer(1,12)]
    data = [["#","Date","Merchant","Category","Status","Amount"]]; tot = {}
    for i, r in enumerate(rows, 1):
        data.append([i, r["date"], (r["merchant"] or "")[:30], r["category"], r["status"], "%.2f %s" % (r["amount"], r["currency"])])
        tot[r["currency"]] = tot.get(r["currency"],0) + r["amount"]
    for c, v in tot.items(): data.append(["","","","","Total", "%.2f %s" % (v, c)])
    t = Table(data, repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f6feb")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),("ALIGN",(-1,0),(-1,-1),"RIGHT"),("FONTSIZE",(0,0),(-1,-1),9)]))
    el.append(t)
    for i, r in enumerate(rows, 1):
        el += [PageBreak(), Paragraph(f"#{i} – {r['merchant']} – {r['date']} – {r['amount']:.2f} {r['currency']} ({r['category']})", ss["Heading3"])]
        if r["notes"]: el.append(Paragraph("Notes: " + r["notes"], ss["Normal"]))
        if r["preview"]:
            p = os.path.join(TH, r["preview"]); w, h = Image.open(p).size; s = min(480/w, 640/h)
            el.append(RLImage(p, w*s, h*s))
    doc.build(el)
    return Response(buf.getvalue(), mimetype="application/pdf", headers={"Content-Disposition":"attachment; filename=expense_report.pdf"})

@app.route("/uploads/<path:f>")
def uploads(f): return send_from_directory(UP, f)
@app.route("/thumbs/<path:f>")
def thumbs(f): return send_from_directory(TH, f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
