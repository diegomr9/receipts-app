import os, re, io, csv, sqlite3, subprocess, uuid, datetime
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory, Response, g, flash
from PIL import Image
try:
    from pillow_heif import register_heif_opener; register_heif_opener()  # iPhone HEIC/HEIF photos
except ImportError: pass
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
        cols = [c[1] for c in g.db.execute("PRAGMA table_info(receipts)")]
        if "title" not in cols: g.db.execute("ALTER TABLE receipts ADD COLUMN title TEXT DEFAULT ''")
        if "ocr_note" not in cols: g.db.execute("ALTER TABLE receipts ADD COLUMN ocr_note TEXT DEFAULT ''")
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
        from PIL import ImageOps
        img = ImageOps.exif_transpose(Image.open(path))  # respect phone rotation
    img = img.convert("RGB"); img.thumbnail((1400,1400))
    fn = name + "_p.jpg"; img.save(os.path.join(TH, fn), quality=85)
    return fn

def ocr(preview):
    try:
        import pytesseract
        return pytesseract.image_to_string(Image.open(os.path.join(TH, preview)))
    except Exception: return ""

def extract_text(path, prev):
    """OCR text. PDFs: use the text layer of all pages if present, otherwise OCR every page (max 10)."""
    if path.lower().endswith(".pdf"):
        try:
            t = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=60).stdout
            if len(t.strip()) > 20: return t
            import tempfile, glob, pytesseract
            with tempfile.TemporaryDirectory() as d:
                subprocess.run(["pdftoppm", "-png", "-r", "200", "-l", "10", path, os.path.join(d, "p")], timeout=120)
                return "\n".join(pytesseract.image_to_string(Image.open(p)) for p in sorted(glob.glob(os.path.join(d, "p*.png"))))
        except Exception: return ""
    return ocr(prev) if prev else ""

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
    from currency import detect
    d = detect(text)
    if d:
        r["ocr_note"] = d["note"]
        if d["confident"]: r["currency"] = d["currency"]
    low = text.lower()
    for cat, kws in [("meals",["restaurant","cafe","coffee","lunch","dinner","food"]),("lodging",["hotel","inn","night"]),
                     ("travel",["airline","flight","train","rail"]),("transport",["taxi","uber","fuel","parking","metro"]),
                     ("supplies",["office","paper","staples","printer"])]:
        if any(k in low for k in kws): r["category"] = cat; break
    return r

def add_receipt(path, fields=None):
    prev = make_preview(path)
    text = extract_text(path, prev)
    detected = parse(text); f = dict(detected); f.update({k: v for k, v in (fields or {}).items() if v})
    if detected.get("currency"): f["currency"] = detected["currency"]  # only set when confident
    cur = db().execute("INSERT INTO receipts(ocr_note,title,date,merchant,amount,currency,category,notes,status,file,preview,ocr_text,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (f.get("ocr_note",""), f.get("title",""), f.get("date", datetime.date.today().isoformat()), f.get("merchant",""), f.get("amount",0) or 0, f.get("currency","EUR"),
         f.get("category","other"), f.get("notes",""), f.get("status","to submit"), os.path.basename(path), prev, text, datetime.datetime.now().isoformat()))
    return cur.lastrowid

def query(args):
    sql, p = "SELECT * FROM receipts WHERE 1=1", []
    if args.get("status"): sql += " AND status=?"; p.append(args["status"])
    if args.get("start"): sql += " AND date>=?"; p.append(args["start"])
    if args.get("end"): sql += " AND date<=?"; p.append(args["end"])
    if args.get("currency"): sql += " AND currency=?"; p.append(args["currency"])
    return db().execute(sql + " ORDER BY date DESC, id DESC", p).fetchall()

def selected(form):
    ids = [int(i) for i in form.getlist("ids")]
    if ids: return db().execute("SELECT * FROM receipts WHERE id IN (%s) ORDER BY date" % ",".join("?"*len(ids)), ids).fetchall()
    return list(reversed(query(form)))

from ui import INDEX, EDIT, LOGIN, STATUS_ES, CAT_ES, fecha, money, CUR_MAIN, CUR_OTHER, CUR_INFO
CODES = list(CUR_INFO)
app.jinja_env.globals.update(ST=STATUS_ES, CAT=CAT_ES, fecha=fecha, money=money, CUR_MAIN=CUR_MAIN, CUR_OTHER=CUR_OTHER, CUR_INFO=CUR_INFO)
@app.route("/login", methods=["GET","POST"])
def login():
    err = None
    if request.method == "POST":
        ip = request.remote_addr
        n, t = FAILS.get(ip, (0, 0))
        import time
        if n >= 5 and time.time() - t < 300: err = "Too many attempts. Please wait five minutes."
        elif check_password_hash(CFG["password_hash"], request.form.get("password","")):
            FAILS.pop(ip, None); session.clear(); session["ok"] = True; session.permanent = True; return redirect("/")
        else: FAILS[ip] = (n+1, time.time()); err = "Incorrect password."
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
    return render_template_string(INDEX, rows=rows, totals=totals, counts=counts, statuses=STATUSES, a=request.args, last_cur=session.get("cur", "EUR"),
        used=[x[0] for x in db().execute("SELECT DISTINCT currency FROM receipts ORDER BY currency")])

@app.post("/upload")
def upload():
    last = None
    cur = (request.form.get("currency") or "EUR").upper()[:3]; session["cur"] = cur
    for f in request.files.getlist("file"):
        if not f.filename: continue
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        path = os.path.join(UP, uuid.uuid4().hex + ext); f.save(path)
        last = add_receipt(path, {"title": request.form.get("title","").strip()[:200], "currency": cur})
    if last: flash("Receipt added · please review the details"); return redirect(url_for("edit", rid=last))
    return redirect("/")

@app.route("/edit/<int:rid>", methods=["GET","POST"])
def edit(rid):
    if request.method == "POST":
        f = request.form
        db().execute("UPDATE receipts SET title=?,date=?,merchant=?,amount=?,currency=?,category=?,notes=?,status=? WHERE id=?",
            (f.get("title","").strip()[:200], f["date"], f["merchant"], float(f["amount"] or 0), f["currency"].upper()[:3], f["category"], f["notes"], f["status"], rid))
        flash("Changes saved"); return redirect("/")
    r = db().execute("SELECT * FROM receipts WHERE id=?", (rid,)).fetchone()
    return render_template_string(EDIT, r=r, cats=CATS, statuses=STATUSES) if r else ("Not found", 404)

@app.post("/delete/<int:rid>")
def delete(rid):
    db().execute("DELETE FROM receipts WHERE id=?", (rid,)); flash("Receipt deleted"); return redirect("/")

@app.post("/bulk")
def bulk():
    to = request.args.get("to"); ids = [int(i) for i in request.form.getlist("ids")]
    if to in STATUSES and ids:
        db().execute("UPDATE receipts SET status=? WHERE id IN (%s)" % ",".join("?"*len(ids)), [to]+ids)
        flash(f"{len(ids)} marked as {STATUS_ES[to].lower()}")
    else: flash("Select at least one receipt")
    return redirect("/")

@app.post("/export.csv")
def export_csv():
    out = io.StringIO(); out.write("\ufeff"); w = csv.writer(out)
    w.writerow(["id","date","title","merchant","amount","currency","category","status","notes","file"])
    for r in selected(request.form):
        w.writerow([r["id"],r["date"],r["title"] or "",r["merchant"],"%.2f"%r["amount"],r["currency"],CAT_ES.get(r["category"],r["category"]),STATUS_ES.get(r["status"],r["status"]),r["notes"],r["file"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=receipts.csv"})

@app.post("/export.pdf")
def export_pdf():
    from pdfreport import build_pdf
    return Response(build_pdf(selected(request.form), TH), mimetype="application/pdf",
                    headers={"Content-Disposition":"attachment; filename=expense_report.pdf"})

@app.route("/uploads/<path:f>")
def uploads(f): return send_from_directory(UP, f)
@app.route("/thumbs/<path:f>")
def thumbs(f): return send_from_directory(TH, f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
