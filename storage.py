"""Data layer: Postgres (DATABASE_URL, e.g. Neon) or local SQLite. Files are stored in the DB as blobs."""
import os, io, sqlite3, subprocess, tempfile, glob, uuid, datetime, threading
from PIL import Image, ImageOps

URL = os.environ.get("DATABASE_URL", "").strip()
PG = URL.startswith(("postgres://", "postgresql://"))
SQLITE_PATH = os.path.join(os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__))), "receipts.db")
MAX_PDF = 5 * 1024 * 1024
_ready = False; _lock = threading.Lock()

class DB:
    def __init__(self):
        if PG:
            import psycopg
            from psycopg.rows import dict_row
            for i in range(3):  # Neon may be waking from auto-suspend
                try: self.c = psycopg.connect(URL, row_factory=dict_row, connect_timeout=10); break
                except psycopg.OperationalError:
                    if i == 2: raise
                    import time; time.sleep(1 + i)
        else:
            self.c = sqlite3.connect(SQLITE_PATH); self.c.row_factory = sqlite3.Row
        _init(self)
    def execute(self, sql, params=()):
        if PG: sql = sql.replace("?", "%s")
        return self.c.execute(sql, tuple(params))
    def insert(self, sql, params=()):
        if PG: return self.execute(sql + " RETURNING id", params).fetchone()["id"]
        return self.execute(sql, params).lastrowid
    def close(self, commit=True):
        try:
            if commit: self.c.commit()
            else: self.c.rollback()
        finally: self.c.close()

def _init(db):
    global _ready
    if _ready: return
    with _lock:
        if _ready: return
        idt, real, blob = ("SERIAL PRIMARY KEY", "DOUBLE PRECISION", "BYTEA") if PG else ("INTEGER PRIMARY KEY", "REAL", "BLOB")
        db.execute(f"""CREATE TABLE IF NOT EXISTS receipts(id {idt}, title TEXT DEFAULT '', date TEXT, merchant TEXT DEFAULT '',
            amount {real} DEFAULT 0, currency TEXT DEFAULT 'EUR', category TEXT DEFAULT 'other', notes TEXT DEFAULT '',
            status TEXT DEFAULT 'to submit', file TEXT, preview TEXT, thumb TEXT, ocr_text TEXT DEFAULT '', ocr_note TEXT DEFAULT '', created TEXT)""")
        db.execute(f"CREATE TABLE IF NOT EXISTS blobs(name TEXT PRIMARY KEY, mime TEXT, data {blob}, created TEXT)")
        if PG:
            for col in ("title", "thumb", "ocr_note"): db.execute(f"ALTER TABLE receipts ADD COLUMN IF NOT EXISTS {col} TEXT DEFAULT ''")
        else:
            cols = [r[1] for r in db.execute("PRAGMA table_info(receipts)")]
            for col in ("title", "thumb", "ocr_note"):
                if col not in cols: db.execute(f"ALTER TABLE receipts ADD COLUMN {col} TEXT DEFAULT ''")
        db.c.commit(); _ready = True

# ---------- blobs ----------
def put_blob(db, name, mime, data):
    db.execute("INSERT INTO blobs(name,mime,data,created) VALUES(?,?,?,?)", (name, mime, data, datetime.datetime.now().isoformat()))
    return name
def get_blob(db, name):
    r = db.execute("SELECT mime,data FROM blobs WHERE name=?", (name,)).fetchone()
    return (r["mime"], bytes(r["data"])) if r else None
def delete_blobs(db, *names):
    for n in names:
        if n: db.execute("DELETE FROM blobs WHERE name=?", (n,))

def _jpeg(img, maxpx, q):
    im = img.convert("RGB"); im.thumbnail((maxpx, maxpx), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True, progressive=True); return b.getvalue()

def _ocr(img):
    try:
        import pytesseract; return pytesseract.image_to_string(img)
    except Exception: return ""

def ingest(db, data, filename):
    """Process an uploaded file. Stores compressed file + preview + thumb as blobs. Returns (file, preview, thumb, text)."""
    key = uuid.uuid4().hex
    is_pdf = filename.lower().endswith(".pdf") or data[:5] == b"%PDF-"
    with tempfile.TemporaryDirectory() as d:
        if is_pdf:
            src = os.path.join(d, "in.pdf"); open(src, "wb").write(data)
            text = ""
            try: text = subprocess.run(["pdftotext", "-layout", src, "-"], capture_output=True, text=True, timeout=60).stdout
            except Exception: pass
            subprocess.run(["pdftoppm", "-jpeg", "-r", "150", "-l", "20", src, os.path.join(d, "p")], timeout=180, check=False)
            pages = [Image.open(p) for p in sorted(glob.glob(os.path.join(d, "p*.jpg")))]
            if len(text.strip()) <= 20: text = "\n".join(_ocr(p) for p in pages[:10])
            if not pages: return None, None, None, text
            if len(data) <= MAX_PDF: fdata = data
            else:  # too big: rebuild as a lighter PDF of page images
                small = [Image.open(io.BytesIO(_jpeg(p, 1600, 75))) for p in pages]
                b = io.BytesIO(); small[0].save(b, "PDF", save_all=True, append_images=small[1:], resolution=110); fdata = b.getvalue()
            file = put_blob(db, key + ".pdf", "application/pdf", fdata)
            first = pages[0]
            preview = put_blob(db, key + "_p.jpg", "image/jpeg", _jpeg(first, 1600, 80))
        else:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))  # HEIC via pillow-heif; respect phone rotation
            j = _jpeg(img, 1600, 80)
            file = preview = put_blob(db, key + ".jpg", "image/jpeg", j)
            first = Image.open(io.BytesIO(j)); text = _ocr(first)
        thumb = put_blob(db, key + "_t.jpg", "image/jpeg", _jpeg(first, 240, 75))
    return file, preview, thumb, text
