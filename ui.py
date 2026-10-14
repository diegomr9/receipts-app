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
<meta name=theme-color content="#f3eee7">
<link rel=preconnect href="https://fonts.googleapis.com"><link rel=preconnect href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Jost:wght@300;400;500&display=swap" rel=stylesheet>
<style>
:root{--sand:#f3eee7;--sand2:#ebe6de;--paper:#faf8f4;--stone:#82847f;--line:#dad9d7;--line2:#c9c4ba;
--ink:#313131;--ink2:#585858;--accent:#8a7a63;--serif:"Cormorant Garamond","Times New Roman",serif;--sans:"Jost",system-ui,sans-serif;
--ease:cubic-bezier(.22,.61,.36,1)}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--sand);color:var(--ink);font:300 15px/1.65 var(--sans);letter-spacing:.01em;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.label{font:400 11px/1.4 var(--sans);letter-spacing:.22em;text-transform:uppercase;color:var(--stone)}
h1,h2,.serif{font-family:var(--serif);font-weight:300;letter-spacing:.04em;margin:0}
h1{font-size:clamp(40px,7vw,64px);line-height:1.05}
h2{font-size:28px}
/* header */
.top{display:flex;align-items:center;justify-content:space-between;padding:26px clamp(20px,5vw,64px);border-bottom:1px solid var(--line)}
.brand{font:300 20px var(--serif);letter-spacing:.42em;text-transform:uppercase}
.top nav{display:flex;gap:28px}
.top nav a{font:400 11px var(--sans);letter-spacing:.22em;text-transform:uppercase;color:var(--ink2);position:relative;padding:4px 0}
a.u:after,.top nav a:after{content:"";position:absolute;left:0;right:100%;bottom:0;height:1px;background:currentColor;transition:right .6s var(--ease)}
a.u:hover:after,.top nav a:hover:after{right:0}
main{max-width:1180px;margin:0 auto;padding:0 clamp(20px,5vw,64px) 120px}
.hero{padding:clamp(48px,9vw,110px) 0 clamp(36px,6vw,64px);text-align:center}
.hero .label{margin-bottom:18px}
.hero p{max-width:520px;margin:18px auto 0;color:var(--ink2)}
.rule{width:56px;height:1px;background:var(--line2);margin:28px auto 0;border:0}
/* totals */
.totals{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.totals>div{padding:34px 20px;text-align:center}
.totals>div+div{border-left:1px solid var(--line)}
.totals .num{font:300 clamp(30px,4vw,44px)/1.1 var(--serif);margin:12px 0 6px;letter-spacing:.02em}
.totals .num small{font:400 11px var(--sans);letter-spacing:.2em;margin-left:6px;color:var(--stone)}
.totals .sub{font-size:13px;color:var(--stone)}
/* sections */
.section{margin-top:clamp(48px,7vw,80px)}
.section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap;margin-bottom:22px}
/* upload */
.drop{display:block;border:1px solid var(--line2);background:var(--paper);padding:44px 20px;text-align:center;cursor:pointer;
 transition:background .5s var(--ease),border-color .5s var(--ease)}
.drop:hover,.drop.over{background:#fff;border-color:var(--ink2)}
.drop input{position:absolute;opacity:0;width:1px;height:1px}
.drop .serif{font-size:26px;margin:10px 0 4px}
.drop .hint{font-size:13px;color:var(--stone)}
.upbar{display:flex;gap:24px;align-items:end;margin-top:22px}.upbar .field{flex:1}.upbar .cur{flex:0 0 250px}
.drop .files{margin-top:10px;font-size:13px;color:var(--ink2)}
/* fields */
.field{display:flex;flex-direction:column;gap:6px;min-width:0}
input,select,textarea{font:300 15px var(--sans);color:var(--ink);background:transparent;border:0;border-bottom:1px solid var(--line2);
 border-radius:0;padding:10px 0;outline:none;transition:border-color .4s;-webkit-appearance:none;appearance:none;width:100%}
select{background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='%23585858'/%3E%3C/svg%3E") right 2px center no-repeat;padding-right:18px}
input:focus,select:focus,textarea:focus{border-color:var(--ink)}
textarea{resize:vertical;line-height:1.5}
.filters{display:grid;grid-template-columns:1.1fr 1fr 1fr 1fr auto;gap:24px;align-items:end}
/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;font:400 11px var(--sans);letter-spacing:.22em;text-transform:uppercase;
 padding:15px 28px;border:1px solid var(--ink);background:var(--ink);color:var(--sand);cursor:pointer;border-radius:0;
 transition:background .5s var(--ease),color .5s var(--ease),border-color .5s var(--ease)}
.btn:hover{background:transparent;color:var(--ink)}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--line2)}
.btn.ghost:hover{border-color:var(--ink)}
.btn.link{border:0;background:none;color:var(--ink2);padding:15px 4px;position:relative}
.btn.danger{background:transparent;color:#8b3a2e;border-color:#d9b8ae}
.btn.danger:hover{border-color:#8b3a2e}
/* list */
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;padding:16px 0;border-bottom:1px solid var(--line)}
.toolbar .group{display:flex;flex-wrap:wrap;gap:10px}
.check{display:inline-flex;align-items:center;gap:12px;cursor:pointer}
.check input{width:16px;height:16px;border:1px solid var(--line2);padding:0;background:var(--paper);position:relative;flex:none;cursor:pointer}
.check input:checked{background:var(--ink);border-color:var(--ink)}
.check input:checked:after{content:"";position:absolute;left:5px;top:1px;width:4px;height:9px;border:solid var(--sand);border-width:0 1px 1px 0;transform:rotate(45deg)}
.rows{list-style:none;margin:0;padding:0}
.r{display:grid;grid-template-columns:28px 76px 1.6fr 1fr 1fr auto;gap:22px;align-items:center;padding:20px 0;border-bottom:1px solid var(--line);
 opacity:0;transform:translateY(8px);animation:rise .9s var(--ease) forwards}
.r .thumb{width:76px;height:96px;overflow:hidden;background:var(--sand2);display:block}
.r .thumb img{width:100%;height:100%;object-fit:cover;transition:transform 1.2s var(--ease),filter .8s;filter:saturate(.85)}
.r:hover .thumb img{transform:scale(1.05);filter:saturate(1)}
.r .m{font:400 23px/1.2 var(--serif);letter-spacing:.02em}
.r .meta{font-size:13px;color:var(--stone);margin-top:4px}
.r .amt{font:300 26px var(--serif);text-align:right;white-space:nowrap}
.r .amt small{font:400 10px var(--sans);letter-spacing:.2em;color:var(--stone);margin-left:6px}
.status{display:inline-flex;align-items:center;gap:8px;font:400 10.5px var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--ink2)}
.status:before{content:"";width:6px;height:6px;border-radius:50%;background:var(--line2)}
.status.s-submitted:before{background:#a8987d}.status.s-reimbursed:before{background:#6f7d64}
.empty{padding:70px 0;text-align:center;color:var(--stone)}
.empty .serif{font-size:30px;color:var(--ink);margin-bottom:6px}
.note{font-size:12.5px;color:var(--stone);margin-top:12px}
/* flash */
.flash{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:var(--ink);color:var(--sand);padding:14px 26px;
 font:400 11px var(--sans);letter-spacing:.2em;text-transform:uppercase;z-index:9;animation:toast 5s var(--ease) forwards;max-width:92vw;text-align:center}
/* edit */
.edit{display:grid;grid-template-columns:1fr 1fr;gap:clamp(30px,6vw,80px);align-items:start;padding-top:clamp(36px,6vw,70px)}
.edit figure{margin:0;background:var(--paper);border:1px solid var(--line);padding:18px;position:sticky;top:20px}
.edit figure img{width:100%;max-height:72vh;object-fit:contain;display:block}
.edit figcaption{margin-top:14px;text-align:center}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px 26px;margin-top:34px}
.form-grid .full{grid-column:1/-1}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:40px;align-items:center}
details{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}
summary{cursor:pointer;list-style:none}summary::-webkit-details-marker{display:none}
details pre{white-space:pre-wrap;font:300 13px/1.6 var(--sans);color:var(--ink2);margin-top:14px}
/* login */
.login{min-height:100vh;min-height:100svh;display:grid;place-items:center;padding:30px}
.login .box{width:100%;max-width:380px;text-align:center;animation:rise 1.4s var(--ease) both}
.login .brand{display:block;margin-bottom:60px}
.login h1{font-size:44px;margin:14px 0 46px}
.login .btn{width:100%;margin-top:34px}
.login .err{color:#8b3a2e;font-size:13px;margin-top:16px}
.login footer{margin-top:70px}
@keyframes rise{to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes toast{0%{opacity:0;transform:translate(-50%,10px)}8%,85%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;visibility:hidden}}
.fade{animation:fade 1.2s var(--ease) both}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.r{opacity:1;transform:none}}
@media (max-width:820px){
 .top nav{gap:18px}.brand{font-size:16px;letter-spacing:.34em}
 .totals{grid-template-columns:1fr}.totals>div+div{border-left:0;border-top:1px solid var(--line)}.totals>div{padding:24px 10px}
 .filters{grid-template-columns:1fr 1fr}.filters .field:first-child{grid-column:1/-1}.upbar .cur{flex:none}.filters>div{grid-column:1/-1}.filters>div .btn.ghost{flex:1}
 .r{grid-template-columns:22px 64px 1fr auto;gap:14px;row-gap:4px}
 .r .thumb{width:64px;height:80px;grid-row:span 2}
 .r .cat{display:none}.r .st{grid-column:3}.r .amt{font-size:22px;grid-row:1;grid-column:4}
 .r .m{font-size:20px}
 .edit{grid-template-columns:1fr}.edit figure{position:static}
 .form-grid{grid-template-columns:1fr 1fr;gap:22px 18px}
 .upbar{flex-direction:column;align-items:stretch}
 .toolbar .group .btn{padding:13px 16px}
}
@media (max-width:420px){.top nav a.hide-s{display:none}.form-grid{grid-template-columns:1fr}}
</style>"""

TOP = """{% macro curopts(sel, extra=None) %}{% for c in CUR_MAIN %}<option value="{{c}}" {{'selected' if sel==c}}>{{c}} · {{CUR_INFO[c][0]}} · {{CUR_INFO[c][1]}}</option>{% endfor %}
<option disabled>──────────</option>{% for c in CUR_OTHER %}<option value="{{c}}" {{'selected' if sel==c}}>{{c}} · {{CUR_INFO[c][0]}} · {{CUR_INFO[c][1]}}</option>{% endfor %}
{% if sel and sel not in CUR_INFO %}<option value="{{sel}}" selected>{{sel}}</option>{% endif %}{% endmacro %}<header class="top fade"><a href="/" class=brand>Receipts</a><nav><a href="/#add" class=hide-s>Add</a><a href="/logout">Sign out</a></nav></header>
{% for m in get_flashed_messages() %}<div class=flash>{{m}}</div>{% endfor %}"""

INDEX = HEAD + """<title>Receipts · Expenses to claim</title></head><body>""" + TOP + """<main>
<section class="hero fade"><div class=label>Work expenses</div><h1>My receipts</h1>
<p>A quiet record of every expense, from receipt to reimbursement.</p><hr class=rule></section>
<section class="totals fade">{% for s in statuses %}<div><div class=label>{{ST[s]}}</div>
<div class=num>{% for c,v in totals[s].items() %}{{money(v)}}<small>{{c}}</small>{% if not loop.last %}<br>{% endif %}{% else %}0.00{% endfor %}</div>
<div class=sub>{{counts[s]}} {{'receipt' if counts[s]==1 else 'receipts'}}</div></div>{% endfor %}</section>

<section class=section id=add><div class=section-head><div><div class=label>New</div><h2>Add a receipt</h2></div></div>
<form method=post action="/upload" enctype=multipart/form-data id=up>
<label class=drop id=drop><input type=file name=file accept="image/*,application/pdf" capture=environment multiple required id=file>
<div class=label>Photo, screenshot or PDF</div><div class=serif>Tap to take a photo or choose a file</div>
<div class=hint>Details are filled in automatically; you can review them afterwards.</div><div class=files id=files></div></label>
<div class=upbar><label class="field cur"><span class=label>Currency</span><select name=currency>{{curopts(last_cur)}}</select></label><label class=field><span class=label>Title / description</span><input name=title placeholder="e.g. Aquapark for Argentina" maxlength=200></label><button class=btn>Upload receipt</button></div></form></section>

<section class=section><div class=section-head><div><div class=label>Archive</div><h2>All receipts</h2></div></div>
<form method=get class=filters>
<label class=field><span class=label>Status</span><select name=status><option value="">All</option>{% for s in statuses %}<option value="{{s}}" {{'selected' if a.status==s}}>{{ST[s]}}</option>{% endfor %}</select></label>
<label class=field><span class=label>From</span><input type=date name=start value="{{a.start or ''}}"></label>
<label class=field><span class=label>To</span><input type=date name=end value="{{a.end or ''}}"></label>
<label class=field><span class=label>Currency</span><select name=currency><option value="">All</option>{% for c in used %}<option value="{{c}}" {{'selected' if a.currency==c}}>{{c}} · {{CUR_INFO.get(c,(c,))[0]}}</option>{% endfor %}</select></label>
<div style="display:flex;gap:6px"><button class="btn ghost">Filter</button>{% if a.status or a.start or a.end or a.currency %}<a href="/" class="btn link">Clear</a>{% endif %}</div></form>

<form method=post style="margin-top:34px">
<input type=hidden name=status value="{{a.status or ''}}"><input type=hidden name=start value="{{a.start or ''}}"><input type=hidden name=end value="{{a.end or ''}}"><input type=hidden name=currency value="{{a.currency or ''}}">
<div class=toolbar><label class="check label"><input type=checkbox id=all> Select all</label>
<div class=group><button class="btn ghost" formaction="/bulk?to=submitted">Mark submitted</button><button class="btn ghost" formaction="/bulk?to=reimbursed">Mark reimbursed</button>
<button class="btn" formaction="/export.csv">CSV</button><button class="btn" formaction="/export.pdf">PDF report</button></div></div>
<ul class=rows>{% for r in rows %}<li class=r style="animation-delay:{{loop.index0*70}}ms">
<label class=check><input type=checkbox class=ck name=ids value={{r.id}} aria-label="Select"></label>
<a class=thumb href="/edit/{{r.id}}">{% if r.preview %}<img src="/thumbs/{{r.preview}}" alt="" loading=lazy>{% endif %}</a>
<a href="/edit/{{r.id}}"><div class=m>{{r.title or r.merchant or 'Untitled'}}</div><div class=meta>{% if r.title %}{{r.merchant or 'Unknown merchant'}} · {% endif %}{{fecha(r.date)}}</div></a>
<div class="cat label">{{CAT.get(r.category, r.category)}}</div>
<div class=st><span class="status s-{{r.status.split()[0]}}">{{ST.get(r.status, r.status)}}</span></div>
<div class=amt>{{money(r.amount)}}<small>{{r.currency}}</small></div></li>
{% else %}<li class=empty><div class=serif>No receipts yet</div>Add your first one above.</li>{% endfor %}</ul>
<p class=note>Exports include the selected receipts or, if none are selected, all filtered ones.</p></form></section></main>
<script>
const all=document.getElementById('all');all&&all.addEventListener('change',()=>document.querySelectorAll('.ck').forEach(c=>c.checked=all.checked));
const f=document.getElementById('file'),d=document.getElementById('drop'),o=document.getElementById('files');
f.addEventListener('change',()=>{o.textContent=[...f.files].map(x=>x.name).join(' · ')});
['dragover','dragenter'].forEach(e=>d.addEventListener(e,ev=>{ev.preventDefault();d.classList.add('over')}));
['dragleave','drop'].forEach(e=>d.addEventListener(e,ev=>{ev.preventDefault();d.classList.remove('over')}));
d.addEventListener('drop',ev=>{f.files=ev.dataTransfer.files;f.dispatchEvent(new Event('change'))});
</script></body></html>"""

EDIT = HEAD + """<title>Receipt · {{r.title or r.merchant}}</title></head><body>""" + TOP + """<main><div class=edit>
<figure class=fade>{% if r.preview %}<a href="/uploads/{{r.file}}" target=_blank><img src="/thumbs/{{r.preview}}" alt="Receipt"></a>{% endif %}
<figcaption><a href="/uploads/{{r.file}}" target=_blank class="label u" style="position:relative">View original</a></figcaption></figure>
<div class=fade><div class=label>Receipt no. {{r.id}}</div><h1 style="font-size:clamp(36px,5vw,52px);margin-top:10px">{{r.title or r.merchant or 'Untitled'}}</h1>
<form method=post><div class=form-grid>
<label class="field full"><span class=label>Title / description</span><input name=title value="{{r.title or ''}}" placeholder="e.g. Aquapark for Argentina" maxlength=200></label>
<label class="field full"><span class=label>Merchant</span><input name=merchant value="{{r.merchant}}"></label>
<label class=field><span class=label>Date</span><input type=date name=date value="{{r.date}}"></label>
<label class=field><span class=label>Category</span><select name=category>{% for c in cats %}<option value="{{c}}" {{'selected' if r.category==c}}>{{CAT[c]}}</option>{% endfor %}</select></label>
<label class=field><span class=label>Amount</span><input type=number step=0.01 inputmode=decimal name=amount value="{{'%.2f'|format(r.amount)}}"></label>
<label class=field><span class=label>Currency</span><select name=currency>{{curopts(r.currency)}}</select></label>
<label class="field full"><span class=label>Status</span><select name=status>{% for s in statuses %}<option value="{{s}}" {{'selected' if r.status==s}}>{{ST[s]}}</option>{% endfor %}</select></label>
<label class="field full"><span class=label>Notes</span><textarea name=notes rows=3>{{r.notes}}</textarea></label></div>
<div class=actions><button class=btn>Save</button><a href="/" class="btn ghost">Back</a>
<button class="btn danger" formaction="/delete/{{r.id}}" onclick="return confirm('Delete this receipt?')" style="margin-left:auto">Delete</button></div></form>
{% if r.ocr_text %}<details><summary class=label>Recognised text (OCR)</summary><pre>{{r.ocr_text}}</pre></details>{% endif %}
</div></div></main></body></html>"""

LOGIN = HEAD + """<title>Receipts · Sign in</title></head><body><div class=login><div class=box>
<span class=brand>Receipts</span><div class=label>Private access</div><h1>Welcome</h1>
<form method=post><label class=field style="text-align:left"><span class=label>Password</span>
<input type=password name=password autocomplete=current-password autofocus required></label>
{% if err %}<div class=err>{{err}}</div>{% endif %}<button class=btn>Sign in</button></form>
<footer class=label>Work expenses</footer></div></div></body></html>"""
