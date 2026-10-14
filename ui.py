# Presentation layer: Spanish labels + templates. Style inspired by quiet luxury hospitality sites
# (warm sand palette, thin serif display type, spaced uppercase labels, hairlines, slow transitions).
STATUS_ES = {"to submit": "To submit", "submitted": "Submitted", "reimbursed": "Reimbursed"}
CAT_ES = {"meals": "Meals", "travel": "Travel", "transport": "Transport", "lodging": "Lodging",
          "supplies": "Supplies", "other": "Other"}
MESES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CUR_INFO = {  # code: (symbol, name)
 "EUR": ("€", "Euro"), "USD": ("$", "US Dollar"), "MYR": ("RM", "Malaysian Ringgit"), "SGD": ("S$", "Singapore Dollar"),
 "GBP": ("£", "British Pound"), "CHF": ("Fr", "Swiss Franc"), "JPY": ("¥", "Japanese Yen"), "CNY": ("¥", "Chinese Yuan"),
 "HKD": ("HK$", "Hong Kong Dollar"), "AUD": ("A$", "Australian Dollar"), "CAD": ("C$", "Canadian Dollar"),
 "NZD": ("NZ$", "New Zealand Dollar"), "THB": ("฿", "Thai Baht"), "IDR": ("Rp", "Indonesian Rupiah"),
 "PHP": ("₱", "Philippine Peso"), "VND": ("₫", "Vietnamese Dong"), "KRW": ("₩", "South Korean Won"),
 "INR": ("₹", "Indian Rupee"), "AED": ("AED", "UAE Dirham"), "MXN": ("MX$", "Mexican Peso"),
 "ARS": ("AR$", "Argentine Peso"), "BRL": ("R$", "Brazilian Real")}
CUR_MAIN = ["EUR", "USD", "MYR", "SGD"]
CUR_OTHER = [c for c in CUR_INFO if c not in CUR_MAIN]

def fecha(d):
    try: y, m, dd = d.split("-"); return f"{int(dd)} {MESES[int(m)-1]} {y}"
    except Exception: return d or ""

def money(v):
    return f"{v:,.2f}"

HEAD = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name=theme-color content="#ffffff">
<link rel=preconnect href="https://fonts.googleapis.com"><link rel=preconnect href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel=stylesheet>
<style>
:root{--bg:#f6f7f9;--surface:#fff;--subtle:#f1f3f6;--border:#e4e7ec;--border2:#d0d5dd;--text:#101828;--text2:#475467;--muted:#667085;
--accent:#3538cd;--accent-h:#2d31a6;--accent-bg:#eef0ff;--radius:10px;--shadow:0 1px 2px rgba(16,24,40,.05);--shadow2:0 1px 3px rgba(16,24,40,.08),0 1px 2px rgba(16,24,40,.04);
--font:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:400 14px/1.5 var(--font);-webkit-font-smoothing:antialiased;font-feature-settings:"cv11","ss01"}
a{color:inherit;text-decoration:none}
.num-t{font-variant-numeric:tabular-nums}
/* app bar */
.bar{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.9);backdrop-filter:saturate(1.6) blur(8px);border-bottom:1px solid var(--border)}
.bar-in{max-width:1240px;margin:0 auto;padding:0 24px;height:60px;display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;font-size:15px;letter-spacing:-.01em}
.logo{width:28px;height:28px;border-radius:8px;background:var(--accent);display:grid;place-items:center;color:#fff}
.bar nav{display:flex;gap:4px}
.bar nav a{padding:7px 12px;border-radius:8px;color:var(--text2);font-weight:500;font-size:13.5px;transition:background .15s,color .15s}
.bar nav a:hover{background:var(--subtle);color:var(--text)}
main{max-width:1240px;margin:0 auto;padding:28px 24px 80px}
/* page header */
.ph{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:22px}
.ph h1{font-size:24px;font-weight:600;letter-spacing:-.02em;margin:0}
.ph p{margin:4px 0 0;color:var(--muted)}
.crumb{font-size:13px;color:var(--muted);margin-bottom:6px}.crumb a:hover{color:var(--text)}
/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:38px;padding:0 14px;border-radius:8px;border:1px solid var(--accent);
 background:var(--accent);color:#fff;font:600 13.5px var(--font);cursor:pointer;white-space:nowrap;box-shadow:var(--shadow);transition:background .15s,border-color .15s,box-shadow .15s}
.btn:hover{background:var(--accent-h);border-color:var(--accent-h)}
.btn:focus-visible,input:focus-visible,select:focus-visible{outline:none;box-shadow:0 0 0 4px rgba(53,56,205,.15)}
.btn.sec{background:var(--surface);color:var(--text);border-color:var(--border2)}
.btn.sec:hover{background:var(--subtle)}
.btn.ghost{background:transparent;border-color:transparent;color:var(--text2);box-shadow:none}.btn.ghost:hover{background:var(--subtle);color:var(--text)}
.btn.danger{background:var(--surface);color:#b42318;border-color:#fecdca}.btn.danger:hover{background:#fef3f2}
.btn svg{width:16px;height:16px}
/* cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow)}
.card-h{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 18px;border-bottom:1px solid var(--border)}
.card-h h2{font-size:15px;font-weight:600;margin:0;letter-spacing:-.01em}
.card-h .sub{color:var(--muted);font-size:13px}
.card-b{padding:18px}
/* stats */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px}
.stat{padding:16px 18px;transition:box-shadow .15s,border-color .15s}
.stat:hover{box-shadow:var(--shadow2);border-color:var(--border2)}
.stat .k{display:flex;align-items:center;gap:8px;color:var(--text2);font-weight:500;font-size:13px}
.stat .v{font-size:22px;font-weight:600;letter-spacing:-.02em;margin-top:8px;line-height:1.25;font-variant-numeric:tabular-nums}
.stat .v small{font-size:12px;font-weight:500;color:var(--muted);margin-left:4px;letter-spacing:0}
.stat .v.more{font-size:15px;margin-top:2px}
.stat .f{margin-top:8px;font-size:12.5px;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.d-to{background:#f79009}.d-submitted{background:#2e90fa}.d-reimbursed{background:#12b76a}.d-all{background:var(--accent)}
/* layout */
.grid{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:18px;align-items:start}
.side{position:sticky;top:78px;display:flex;flex-direction:column;gap:18px}
/* forms */
.field{display:flex;flex-direction:column;gap:6px;min-width:0}
.field>span{font-size:13px;font-weight:500;color:var(--text2)}
input,select,textarea{font:400 14px var(--font);color:var(--text);background:var(--surface);border:1px solid var(--border2);border-radius:8px;
 height:38px;padding:0 12px;width:100%;box-shadow:var(--shadow);transition:border-color .15s,box-shadow .15s;-webkit-appearance:none;appearance:none}
textarea{height:auto;padding:10px 12px;resize:vertical;line-height:1.5}
select{background:var(--surface) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%23667085' stroke-width='1.5'/%3E%3C/svg%3E") right 12px center no-repeat;padding-right:32px}
input:focus,select:focus,textarea:focus{border-color:#a4a7f0;box-shadow:0 0 0 4px rgba(53,56,205,.12);outline:none}
input[type=checkbox]{width:16px;height:16px;padding:0;border-radius:4px;box-shadow:none;cursor:pointer;flex:none;position:relative}
input[type=checkbox]:checked{background:var(--accent);border-color:var(--accent)}
input[type=checkbox]:checked:after{content:"";position:absolute;left:4.5px;top:1.5px;width:4px;height:8px;border:solid #fff;border-width:0 2px 2px 0;transform:rotate(45deg)}
/* upload */
.drop{position:relative;border:1.5px dashed var(--border2);border-radius:10px;background:var(--subtle);padding:22px 16px;text-align:center;cursor:pointer;transition:border-color .15s,background .15s}
.drop:hover,.drop.over{border-color:var(--accent);background:var(--accent-bg)}
.drop input[type=file]{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.drop .ic{width:40px;height:40px;border-radius:10px;background:var(--surface);border:1px solid var(--border);display:grid;place-items:center;margin:0 auto 10px;color:var(--accent);box-shadow:var(--shadow)}
.drop .t{font-weight:600}.drop .t b{color:var(--accent)}
.drop .h{color:var(--muted);font-size:12.5px;margin-top:2px}
.pick{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
.files{margin-top:10px;font-size:12.5px;color:var(--accent);font-weight:500;word-break:break-all}
.files.err{color:#b42318}
.up-f{display:flex;flex-direction:column;gap:12px;margin-top:14px}
/* filter bar */
.fbar{display:flex;flex-wrap:wrap;gap:10px;align-items:end;padding:14px 18px;border-bottom:1px solid var(--border);background:#fcfcfd}
.fbar .field{width:150px}.fbar .field>span{font-size:12px}
.fbar input,.fbar select{height:34px;font-size:13px}
.fbar .btn{height:34px}
.abar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;padding:10px 18px;border-bottom:1px solid var(--border)}
.abar .l{display:flex;align-items:center;gap:10px;color:var(--text2);font-size:13px}
.abar .r{display:flex;flex-wrap:wrap;gap:8px}.abar .btn{height:32px;font-size:13px;padding:0 12px}
/* table */
.thead,.row{display:grid;grid-template-columns:20px 44px minmax(0,2.2fr) 110px 110px 120px 130px;gap:14px;align-items:center;padding:0 18px}
.thead{height:38px;background:var(--subtle);border-bottom:1px solid var(--border);font-size:12px;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.thead .ra,.row .amt{text-align:right}
.row{min-height:64px;padding-top:10px;padding-bottom:10px;border-bottom:1px solid var(--border);transition:background .12s}
.row:last-child{border-bottom:0}.row:hover{background:#fafbfc}
.thumb{width:44px;height:44px;border-radius:8px;overflow:hidden;background:var(--subtle);border:1px solid var(--border);display:block}
.thumb img{width:100%;height:100%;object-fit:cover}
.ttl{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ttl:hover{color:var(--accent)}
.mer{color:var(--muted);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.date{color:var(--text2);font-variant-numeric:tabular-nums}
.chip{display:inline-flex;align-items:center;height:24px;padding:0 9px;border-radius:6px;background:var(--subtle);border:1px solid var(--border);font-size:12px;font-weight:500;color:var(--text2)}
.pill{display:inline-flex;align-items:center;gap:6px;height:24px;padding:0 10px;border-radius:999px;font-size:12px;font-weight:500}
.p-to{background:#fffaeb;color:#b54708}.p-submitted{background:#eff8ff;color:#175cd3}.p-reimbursed{background:#ecfdf3;color:#067647}
.pill:before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.amt{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}.amt small{font-weight:500;color:var(--muted);font-size:12px;margin-left:4px}
.empty{padding:56px 20px;text-align:center;color:var(--muted)}
.empty .ic{width:44px;height:44px;border-radius:10px;background:var(--subtle);display:grid;place-items:center;margin:0 auto 12px;color:var(--muted)}
.empty b{display:block;color:var(--text);font-size:15px;margin-bottom:2px}
.foot{padding:12px 18px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--border);background:#fcfcfd;border-radius:0 0 12px 12px}
/* toast */
.flash{position:fixed;right:20px;bottom:20px;z-index:20;background:#101828;color:#fff;padding:12px 16px;border-radius:10px;box-shadow:0 12px 24px -6px rgba(16,24,40,.25);
 font-weight:500;display:flex;gap:10px;align-items:center;animation:toast 4.5s ease forwards;max-width:calc(100vw - 40px)}
.flash:before{content:"";width:8px;height:8px;border-radius:50%;background:#12b76a;flex:none}
@keyframes toast{0%{opacity:0;transform:translateY(8px)}6%,88%{opacity:1;transform:none}100%{opacity:0;visibility:hidden}}
/* edit */
.edit{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:18px;align-items:start}
.preview{padding:14px;position:sticky;top:78px}
.preview img{width:100%;max-height:70vh;object-fit:contain;border-radius:8px;background:var(--subtle);display:block}
.preview .pf{display:flex;justify-content:space-between;align-items:center;margin-top:12px;color:var(--muted);font-size:13px}
.preview .pf a{color:var(--accent);font-weight:500}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:16px}.fg .full{grid-column:1/-1}
.detect{display:flex;gap:6px;align-items:flex-start;font-size:12.5px;color:#175cd3;background:#eff8ff;border:1px solid #d1e9ff;border-radius:8px;padding:7px 10px;margin-top:4px;line-height:1.4}
.detect.weak{color:var(--text2);background:var(--subtle);border-color:var(--border)}
.acts{display:flex;gap:8px;flex-wrap:wrap;padding:14px 18px;border-top:1px solid var(--border);background:#fcfcfd;border-radius:0 0 12px 12px}
details.ocr summary{cursor:pointer;padding:14px 18px;font-weight:500;color:var(--text2);list-style:none}details.ocr summary::-webkit-details-marker{display:none}
details.ocr summary:after{content:" ›";color:var(--muted)}details.ocr[open] summary:after{content:" ⌄"}
details.ocr pre{margin:0;padding:0 18px 18px;white-space:pre-wrap;font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text2)}
/* login */
.login{min-height:100vh;min-height:100svh;display:grid;place-items:center;padding:24px;background:radial-gradient(1200px 500px at 50% -10%,#e9ebff 0,transparent 60%),var(--bg)}
.login .card{width:100%;max-width:400px;padding:32px}
.login .logo{width:40px;height:40px;border-radius:10px;margin-bottom:20px}
.login h1{font-size:22px;font-weight:600;letter-spacing:-.02em;margin:0}
.login p{color:var(--muted);margin:4px 0 24px}
.login .btn{width:100%;height:40px;margin-top:18px}
.login .err{display:flex;gap:8px;align-items:center;color:#b42318;background:#fef3f2;border:1px solid #fecdca;border-radius:8px;padding:8px 12px;margin-top:12px;font-size:13px}
.login .lf{margin-top:22px;text-align:center;color:var(--muted);font-size:12.5px}
@media (max-width:1080px){.grid{grid-template-columns:1fr}.side{position:static;order:-1}.stats{grid-template-columns:repeat(2,1fr)}}
@media (max-width:760px){
 main{padding:18px 14px 70px}.bar-in{padding:0 14px}
 .ph h1{font-size:21px}.ph .btn{display:none}
 .stats{gap:10px}.stat{padding:13px 14px}.stat .v{font-size:18px}
 .fbar{padding:12px 14px}.fbar .field{width:calc(50% - 5px)}.fbar .btns{width:100%;display:flex;gap:8px}.fbar .btns .btn{flex:1}
 .abar{padding:10px 14px}.abar .r{width:100%}.abar .r .btn{flex:1}
 .thead{display:none}
 .row{grid-template-columns:20px 48px minmax(0,1fr) auto;grid-template-areas:"c t m a" "c t s s";row-gap:6px;column-gap:12px;padding:12px 14px}
 .row .ck-w{grid-area:c;align-self:start;margin-top:4px}.row .thumb{grid-area:t;width:48px;height:48px;align-self:start}
 .row .main{grid-area:m}.row .amt{grid-area:a;align-self:start}
 .row .meta-m{grid-area:s;display:flex!important;gap:6px;align-items:center;flex-wrap:wrap}
 .row .date,.row .cat-c,.row .st-c{display:none}
 .edit{grid-template-columns:1fr}.preview{position:static}.fg{grid-template-columns:1fr 1fr;gap:12px}
}
@media (max-width:400px){.fg{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>"""

ICON_UP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="20" height="20"><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/><path d="M12 4v12"/><path d="m7 9 5-5 5 5"/></svg>'
ICON_DOC = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>'
ICON_CAM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M3 8a2 2 0 0 1 2-2h2l2-2h6l2 2h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="12" cy="13" r="3.5"/></svg>'
ICON_LOGO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/></svg>'
ICON_PLUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'

TOP = """{% macro curopts(sel, extra=None) %}{% for c in CUR_MAIN %}<option value="{{c}}" {{'selected' if sel==c}}>{{c}} · {{CUR_INFO[c][0]}} · {{CUR_INFO[c][1]}}</option>{% endfor %}
<option disabled>──────────</option>{% for c in CUR_OTHER %}<option value="{{c}}" {{'selected' if sel==c}}>{{c}} · {{CUR_INFO[c][0]}} · {{CUR_INFO[c][1]}}</option>{% endfor %}
{% if sel and sel not in CUR_INFO %}<option value="{{sel}}" selected>{{sel}}</option>{% endif %}{% endmacro %}
<header class=bar><div class=bar-in><a href="/" class=brand><span class=logo>""" + ICON_LOGO + """</span>Receipts</a>
<nav><a href="/">Expenses</a><a href="/#add">Add</a><a href="/logout">Sign out</a></nav></div></header>
{% for m in get_flashed_messages() %}<div class=flash>{{m}}</div>{% endfor %}"""

INDEX = HEAD + """<title>Expenses · Receipts</title></head><body>""" + TOP + """<main>
<div class=ph><div><h1>Expenses</h1><p>Track receipts from upload to reimbursement.</p></div>
<a href="#add" class=btn>""" + ICON_PLUS + """ New receipt</a></div>
<section class=stats>{% for s in statuses %}<div class="card stat"><div class=k><span class="dot d-{{s.split()[0]}}"></span>{{ST[s]}}</div>
{% for c,v in totals[s].items() %}<div class="v{{' more' if not loop.first}}">{{money(v)}}<small>{{c}}</small></div>{% else %}<div class=v>0.00</div>{% endfor %}
<div class=f>{{counts[s]}} {{'receipt' if counts[s]==1 else 'receipts'}}</div></div>{% endfor %}
<div class="card stat"><div class=k><span class="dot d-all"></span>All receipts</div><div class=v>{{rows|length}}</div>
<div class=f>{{used|length}} {{'currency' if used|length==1 else 'currencies'}}{% if used %} · {{used|join(', ')}}{% endif %}</div></div></section>

<div class=grid>
<section class="card" style="overflow:hidden">
<div class=card-h><div><h2>All receipts</h2><div class=sub>{{rows|length}} shown</div></div></div>
<form method=get class=fbar>
<label class=field><span>Status</span><select name=status><option value="">All statuses</option>{% for s in statuses %}<option value="{{s}}" {{'selected' if a.status==s}}>{{ST[s]}}</option>{% endfor %}</select></label>
<label class=field><span>From</span><input type=date name=start value="{{a.start or ''}}"></label>
<label class=field><span>To</span><input type=date name=end value="{{a.end or ''}}"></label>
<label class=field><span>Currency</span><select name=currency><option value="">All currencies</option>{% for c in used %}<option value="{{c}}" {{'selected' if a.currency==c}}>{{c}} · {{CUR_INFO.get(c,(c,))[0]}}</option>{% endfor %}</select></label>
<div class=btns style="display:flex;gap:8px"><button class="btn sec">Apply</button>{% if a.status or a.start or a.end or a.currency %}<a href="/" class="btn ghost">Clear</a>{% endif %}</div></form>
<form method=post>
<input type=hidden name=status value="{{a.status or ''}}"><input type=hidden name=start value="{{a.start or ''}}"><input type=hidden name=end value="{{a.end or ''}}"><input type=hidden name=currency value="{{a.currency or ''}}">
<div class=abar><label class=l><input type=checkbox id=all> <span id=selcount>Select all</span></label>
<div class=r><button class="btn sec" formaction="/bulk?to=submitted">Mark submitted</button><button class="btn sec" formaction="/bulk?to=reimbursed">Mark reimbursed</button>
<button class="btn sec" formaction="/export.csv">""" + ICON_DOC + """ CSV</button><button class=btn formaction="/export.pdf">""" + ICON_DOC + """ PDF report</button></div></div>
<div class=thead><span></span><span></span><span>Receipt</span><span>Date</span><span>Category</span><span>Status</span><span class=ra>Amount</span></div>
{% for r in rows %}<div class=row>
<span class=ck-w><input type=checkbox class=ck name=ids value={{r.id}} aria-label="Select"></span>
<a class=thumb href="/edit/{{r.id}}">{% if r.preview %}<img src="/thumbs/{{r.preview}}" alt="" loading=lazy>{% endif %}</a>
<div class=main><a href="/edit/{{r.id}}" class=ttl style="display:block">{{r.title or r.merchant or 'Untitled'}}</a><div class=mer>{{r.merchant or 'Unknown merchant'}}</div></div>
<span class=date>{{fecha(r.date)}}</span>
<span class=cat-c><span class=chip>{{CAT.get(r.category, r.category)}}</span></span>
<span class=st-c><span class="pill p-{{r.status.split()[0]}}">{{ST.get(r.status, r.status)}}</span></span>
<span class=amt>{{money(r.amount)}}<small>{{r.currency}}</small></span>
<div class=meta-m style="display:none"><span class=date style="display:inline;font-size:12.5px">{{fecha(r.date)}}</span><span class=chip>{{CAT.get(r.category, r.category)}}</span><span class="pill p-{{r.status.split()[0]}}">{{ST.get(r.status, r.status)}}</span></div>
</div>{% else %}<div class=empty><div class=ic>""" + ICON_DOC + """</div><b>No receipts yet</b>Upload your first receipt to get started.</div>{% endfor %}
<div class=foot>Exports include the selected receipts, or all filtered receipts if none are selected.</div></form></section>

<aside class=side><section class=card id=add><div class=card-h><div><h2>Add receipt</h2><div class=sub>Photo, screenshot or PDF</div></div></div>
<form method=post action="/upload" enctype=multipart/form-data id=up class=card-b>
<div class=drop id=drop><input type=file name=file accept="image/*,application/pdf,.heic,.heif" multiple id=file>
<input type=file name=file accept="image/*,.heic,.heif" capture=environment id=cam>
<div class=ic>""" + ICON_UP + """</div><div class=t><b>Click to upload</b> or drag and drop</div><div class=h>JPG, PNG, HEIC or PDF · up to 25 MB</div></div>
<div class=pick><label for=file class="btn sec">""" + ICON_DOC + """ Choose file</label><label for=cam class="btn sec">""" + ICON_CAM + """ Take photo</label></div>
<div class=files id=files></div>
<div class=up-f><label class=field><span>Title / description</span><input name=title placeholder="e.g. Aquapark for Argentina" maxlength=200></label>
<label class=field><span>Currency</span><select name=currency>{{curopts(last_cur)}}</select></label>
<button class=btn style="width:100%">Upload receipt</button>
<div style="color:var(--muted);font-size:12.5px">Date, merchant, amount and currency are read automatically. You can review them afterwards.</div></div></form></section></aside>
</div></main>
<script>
const all=document.getElementById('all'),sc=document.getElementById('selcount');
const upd=()=>{const n=document.querySelectorAll('.ck:checked').length;sc.textContent=n?n+' selected':'Select all'};
all&&all.addEventListener('change',()=>{document.querySelectorAll('.ck').forEach(c=>c.checked=all.checked);upd()});
document.querySelectorAll('.ck').forEach(c=>c.addEventListener('change',upd));
const f=document.getElementById('file'),cam=document.getElementById('cam'),d=document.getElementById('drop'),o=document.getElementById('files');
const show=()=>{o.classList.remove('err');o.textContent=[...f.files,...cam.files].map(x=>x.name).join(' · ')};
f.addEventListener('change',show);cam.addEventListener('change',show);
d.addEventListener('click',ev=>{if(!ev.target.closest('label,input'))f.click()});
['dragover','dragenter'].forEach(e=>d.addEventListener(e,ev=>{ev.preventDefault();d.classList.add('over')}));
['dragleave','drop'].forEach(e=>d.addEventListener(e,ev=>{ev.preventDefault();d.classList.remove('over')}));
d.addEventListener('drop',ev=>{f.files=ev.dataTransfer.files;show()});
document.getElementById('up').addEventListener('submit',ev=>{if(!f.files.length&&!cam.files.length){ev.preventDefault();o.classList.add('err');o.textContent='Please choose a file or take a photo first.'}});
</script></body></html>"""

EDIT = HEAD + """<title>{{r.title or r.merchant or 'Receipt'}} · Receipts</title></head><body>""" + TOP + """<main>
<div class=ph><div><div class=crumb><a href="/">Expenses</a> / Receipt #{{r.id}}</div><h1>{{r.title or r.merchant or 'Untitled'}}</h1>
<p>{{r.merchant or 'Unknown merchant'}} · {{fecha(r.date)}} · <span class="pill p-{{r.status.split()[0]}}" style="vertical-align:1px">{{ST.get(r.status, r.status)}}</span></p></div></div>
<div class=edit>
<div class="card preview">{% if r.preview %}<a href="/uploads/{{r.file}}" target=_blank><img src="/thumbs/{{r.preview}}" alt="Receipt"></a>{% endif %}
<div class=pf><span>{{r.file.rsplit('.',1)[-1]|upper}} file</span><a href="/uploads/{{r.file}}" target=_blank>View original ↗</a></div></div>
<div><form method=post class=card><div class=card-h><h2>Details</h2></div><div class="card-b fg">
<label class="field full"><span>Title / description</span><input name=title value="{{r.title or ''}}" placeholder="e.g. Aquapark for Argentina" maxlength=200></label>
<label class="field full"><span>Merchant</span><input name=merchant value="{{r.merchant}}"></label>
<label class=field><span>Date</span><input type=date name=date value="{{r.date}}"></label>
<label class=field><span>Category</span><select name=category>{% for c in cats %}<option value="{{c}}" {{'selected' if r.category==c}}>{{CAT[c]}}</option>{% endfor %}</select></label>
<label class=field><span>Amount</span><input type=number step=0.01 inputmode=decimal name=amount value="{{'%.2f'|format(r.amount)}}" class=num-t></label>
<label class=field><span>Currency</span><select name=currency>{{curopts(r.currency)}}</select></label>
{% if r.ocr_note %}<div class="full detect{{' weak' if r.ocr_note.startswith('Possible') or r.ocr_note.startswith('Ambiguous')}}">ⓘ {{r.ocr_note}}</div>{% endif %}
<label class="field full"><span>Status</span><select name=status>{% for s in statuses %}<option value="{{s}}" {{'selected' if r.status==s}}>{{ST[s]}}</option>{% endfor %}</select></label>
<label class="field full"><span>Notes</span><textarea name=notes rows=3>{{r.notes}}</textarea></label></div>
<div class=acts><button class=btn>Save changes</button><a href="/" class="btn sec">Cancel</a>
<button class="btn danger" formaction="/delete/{{r.id}}" onclick="return confirm('Delete this receipt?')" style="margin-left:auto">Delete</button></div></form>
{% if r.ocr_text %}<details class="card ocr" style="margin-top:18px"><summary>Recognised text (OCR)</summary><pre>{{r.ocr_text}}</pre></details>{% endif %}
</div></div></main></body></html>"""

LOGIN = HEAD + """<title>Sign in · Receipts</title></head><body><div class=login><div class=card>
<div class=logo>""" + ICON_LOGO + """</div><h1>Sign in to Receipts</h1><p>Enter your password to manage your expenses.</p>
<form method=post><label class=field><span>Password</span><input type=password name=password autocomplete=current-password autofocus required></label>
{% if err %}<div class=err>{{err}}</div>{% endif %}<button class=btn>Sign in</button></form>
<div class=lf>Private workspace · Work expenses</div></div></div></body></html>"""
