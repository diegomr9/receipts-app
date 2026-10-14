"""Currency detection from OCR text: explicit symbols/codes first, then scored country clues."""
import re

EXPLICIT = [  # (currency, regex, label)
    ("MYR", r"\bRM\s?\d", "RM"), ("MYR", r"(?<![A-Z])MYR(?![A-Z])", "MYR"),
    ("SGD", r"S\$", "S$"), ("SGD", r"(?<![A-Z])SGD(?![A-Z])", "SGD"),
    ("USD", r"US\$", "US$"), ("USD", r"(?<![A-Z])USD(?![A-Z])", "USD"),
    ("EUR", r"€", "€"), ("EUR", r"(?<![A-Z])EUR(?![A-Z])", "EUR"),
    ("GBP", r"£", "£"), ("GBP", r"(?<![A-Z])GBP(?![A-Z])", "GBP"),
    ("HKD", r"HK\$", "HK$"), ("AUD", r"\bA\$|(?<![A-Z])AUD(?![A-Z])", "A$/AUD"), ("CAD", r"\bC\$|(?<![A-Z])CAD(?![A-Z])", "C$/CAD"),
    ("NZD", r"NZ\$|(?<![A-Z])NZD(?![A-Z])", "NZ$"), ("THB", r"฿|(?<![A-Z])THB(?![A-Z])", "฿/THB"),
    ("IDR", r"\bRp\.?\s?\d|(?<![A-Z])IDR(?![A-Z])", "Rp/IDR"), ("PHP", r"₱|(?<![A-Z])PHP(?![A-Z])", "₱/PHP"),
    ("VND", r"₫|(?<![A-Z])VND(?![A-Z])", "₫/VND"), ("KRW", r"₩|(?<![A-Z])KRW(?![A-Z])", "₩/KRW"),
    ("INR", r"₹|(?<![A-Z])INR(?![A-Z])", "₹/INR"), ("JPY", r"(?<![A-Z])JPY(?![A-Z])|円", "JPY/円"),
    ("CNY", r"(?<![A-Z])(CNY|RMB)(?![A-Z])|元", "CNY"), ("CHF", r"(?<![A-Z])CHF(?![A-Z])", "CHF"),
    ("AED", r"(?<![A-Z])AED(?![A-Z])", "AED"), ("MXN", r"MX\$|(?<![A-Z])MXN(?![A-Z])", "MXN"),
    ("ARS", r"AR\$|(?<![A-Z])ARS(?![A-Z])", "ARS"), ("BRL", r"R\$|(?<![A-Z])BRL(?![A-Z])", "R$"),
]

EU = {"Spain": ["spain", "españa", "madrid", "barcelona", "valencia", "sevilla", "málaga|malaga", r"\+34", r"\b(NIF|CIF)\b", r"\bIVA\b"],
      "France": ["france", "paris", "lyon", "marseille", "nice", r"\+33", r"\bTVA\b", r"\bSIRET\b|\bSIREN\b"],
      "Germany": ["germany", "deutschland", "berlin", "münchen|munich", "hamburg", "frankfurt", r"\+49", r"\bMwSt\b|\bUSt\b", r"\bGmbH\b"],
      "Italy": ["italy", "italia", "roma|rome", "milano|milan", "firenze|florence", r"\+39", r"\bP\.? ?IVA\b"],
      "Portugal": ["portugal", "lisboa|lisbon", "porto", r"\+351", r"\bNIF\b"],
      "Netherlands": ["netherlands", "nederland", "amsterdam", "rotterdam", r"\+31", r"\bBTW\b"],
      "Belgium": ["belgium", "belgique", "brussels|bruxelles", r"\+32"], "Ireland": ["ireland", "dublin", r"\+353"],
      "Austria": ["austria", "österreich", "wien|vienna", r"\+43"], "Greece": ["greece", "athens", r"\+30"],
      "Finland": ["finland", "helsinki", r"\+358"]}

COUNTRIES = {  # country: (currency, [(regex, weight, label)])
    "Malaysia": ("MYR", [(r"malaysia", 3, "Malaysia"), (r"kuala lumpur|\bKL\b|petaling jaya|selangor|penang|pulau pinang|johor|melaka|malacca|ipoh|kota kinabalu|kuching|putrajaya|cyberjaya|shah alam|subang|klang", 2, "Malaysian city/state"),
                         (r"\bSST\b", 2, "SST"), (r"\+?60[\s-]?1?\d[\s-]?\d{3,4}[\s-]?\d{4}", 2, "phone +60"), (r"\bSdn\.? ?Bhd\b|\bBhd\b", 3, "Sdn Bhd"),
                         (r"\bSSM\b|\(\d{6,7}-[A-Z]\)|\b20\d{10}\b", 2, "SSM reg."), (r"\b[0-9]{5}\s+(kuala lumpur|selangor|penang|johor|melaka|perak|sabah|sarawak|kedah|pahang)", 2, "MY postcode")]),
    "Singapore": ("SGD", [(r"singapore", 3, "Singapore"), (r"\+65[\s-]?\d{4}[\s-]?\d{4}", 2, "phone +65"), (r"\bUEN\b|\b(19|20)\d{7}[A-Z]\b", 3, "UEN"),
                          (r"\bPte\.? ?Ltd\b", 3, "Pte Ltd"), (r"\bGST\b", 1, "GST"), (r"\bS\(?\d{6}\)?|singapore\s+\d{6}", 2, "SG postcode"),
                          (r"orchard|jurong|tampines|changi|marina bay|raffles", 2, "Singapore area")]),
    "United States": ("USD", [(r"united states|\bUSA\b|\bU\.S\.A?\.?\b", 3, "USA"), (r"\+1[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}|\(\d{3}\)\s?\d{3}-\d{4}", 2, "US phone"),
                              (r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s+\d{5}(-\d{4})?\b", 3, "US state + ZIP"),
                              (r"new york|los angeles|san francisco|chicago|seattle|boston|miami|las vegas", 2, "US city"), (r"sales tax", 1, "sales tax")]),
    "United Kingdom": ("GBP", [(r"united kingdom|\bUK\b|england|scotland|wales", 3, "UK"), (r"\+44", 2, "phone +44"), (r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", 2, "UK postcode"),
                               (r"london|manchester|edinburgh|birmingham|glasgow", 2, "UK city"), (r"\bVAT\s?(reg|no|number)", 2, "VAT reg."), (r"\bVAT\b", 1, "VAT")]),
    "Thailand": ("THB", [(r"thailand", 3, "Thailand"), (r"bangkok|phuket|chiang mai|pattaya", 2, "Thai city"), (r"\+66", 2, "phone +66"), (r"ภาษี|บาท", 3, "Thai script")]),
    "Indonesia": ("IDR", [(r"indonesia", 3, "Indonesia"), (r"jakarta|bali|denpasar|surabaya|bandung|ubud", 2, "Indonesian city"), (r"\+62", 2, "phone +62"), (r"\bNPWP\b|\bPPN\b", 3, "NPWP/PPN")]),
    "Australia": ("AUD", [(r"australia", 3, "Australia"), (r"sydney|melbourne|brisbane|perth|adelaide|canberra", 2, "Australian city"), (r"\+61", 2, "phone +61"),
                          (r"\bABN\b", 3, "ABN"), (r"\b(NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s+\d{4}\b", 3, "AU state + postcode"), (r"\bGST\b", 1, "GST")]),
    "Japan": ("JPY", [(r"japan|日本", 3, "Japan"), (r"tokyo|osaka|kyoto|東京|大阪|京都", 2, "Japanese city"), (r"\+81", 2, "phone +81"), (r"〒\s?\d{3}-\d{4}", 3, "JP postcode"), (r"税込|消費税", 3, "consumption tax")]),
    "Argentina": ("ARS", [(r"argentina", 3, "Argentina"), (r"buenos aires|córdoba|cordoba|rosario|mendoza|bariloche", 2, "Argentine city"), (r"\+54", 2, "phone +54"), (r"\bCUIT\b", 3, "CUIT"), (r"\bIVA\b", 1, "IVA")]),
}
for c, pats in EU.items():
    lst = [(pats[0], 3, c)]
    for p in pats[1:]:
        if p.startswith(r"\+"): lst.append((p, 2, "phone " + p[1:]))
        elif p.startswith(r"\b"): lst.append((p, 1 if p in (r"\bIVA\b", r"\bNIF\b") else 2, re.sub(r"\\b|\\.|\?|\(|\)| ", "", p).replace("|", "/")))
        else: lst.append((p, 2, c + " city"))
    COUNTRIES[c] = ("EUR", lst)
COUNTRIES["Spain"][1].append((r"\bVAT\b", 1, "VAT"))

def detect(text):
    """Returns dict(currency, confident, note) or None."""
    if not text: return None
    found = {}
    for cur, pat, lbl in EXPLICIT:
        if re.search(pat, text): found.setdefault(cur, lbl)
    if len(found) == 1:
        cur, lbl = next(iter(found.items()))
        return {"currency": cur, "confident": True, "note": f"Detected: “{lbl}” on receipt → {cur}"}
    scores = {}
    for country, (cur, pats) in COUNTRIES.items():
        s, why = 0, []
        for pat, w, lbl in pats:
            if re.search(pat, text, re.I if not pat.startswith(r"\b(") and "[A-Z]" not in pat else 0):
                s += w; why.append(lbl)
        if s: scores[country] = (s, cur, why)
    if not scores:
        return {"currency": None, "confident": False, "note": "Ambiguous symbols: " + ", ".join(found.values())} if found else None
    bycur = {}
    for country, (s, cur, why) in scores.items(): bycur[cur] = bycur.get(cur, 0) + s
    ranked = sorted(scores.items(), key=lambda kv: -kv[1][0])
    country, (s, cur, why) = ranked[0]
    curscores = sorted(bycur.values(), reverse=True)
    margin = curscores[0] - (curscores[1] if len(curscores) > 1 else 0)
    if found and cur not in found: margin = 0  # explicit symbols disagree with country clues
    confident = s >= 4 and margin >= 3
    note = f"Detected: {country} → {cur} ({', '.join(dict.fromkeys(why))})"
    if not confident: note = f"Possible: {country} → {cur} ({', '.join(dict.fromkeys(why))}) · not confident, kept your choice"
    return {"currency": cur, "confident": confident, "note": note}
