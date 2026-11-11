#!/usr/bin/env python3
"""İnci Laboratoriyaları — sayt generatoru.

Ortaq header/footer və bütün məzmun buradadır. Dəyişiklikdən sonra:
    python3 build.py
"""
import re
from pathlib import Path
from urllib.parse import quote, unquote
import hashlib

try:
    from i18n import TR
except ImportError:
    TR = {}

OUT = Path(__file__).parent

PHONE, PHONE_TEL = "(012) 464 89 20", "+994124648920"
HOTLINE = "1113"
WA, WA_TEL = "+994 51 229 49 80", "994512294980"
EMAIL = "info@incilab.az"
ADDRESS = "Əhməd Rəcəbli 19R, Bakı"

LINKS = dict(
    results="https://neticeler.origo.az",
    results_org="https://his.origo.az",
    booking="https://incilab.az/e-randevu/",
    tests="https://test.incilab.az",
    bulletin="https://e-bulleten.incilab.az",
    fb="https://facebook.com/incilaboratoriyalari",
    ig="https://instagram.com/incilaboratoriyalari",
    yt="https://youtube.com/channel/UCB-Ap8qWDk0yJvkpTc0sm5Q",
)

SERVICES = [
    ("biokimya", "Tibbi biokimya", "svc-biokimya.jpg", "Qan və digər bioloji mayelərdə qlükoza, lipidlər, fermentlər, qaraciyər və böyrək göstəriciləri kimi biokimyəvi parametrlərin təyini."),
    ("immunologiya", "İmmunologiya", "svc-immunologiya.jpg", "İmmun sistemin vəziyyətinin, autoimmun xəstəliklərin və infeksiyalara qarşı antitellərin müayinəsi."),
    ("patologiya", "Patologiya", "svc-patologiya.webp", "Toxuma və hüceyrə nümunələrinin histoloji və sitoloji müayinəsi ilə dəqiq diaqnoz."),
    ("hematologiya", "Hematologiya və hemostaz", "svc-hematologiya.jpg", "Ümumi qan analizi, qan hüceyrələrinin morfologiyası və qanın laxtalanma sisteminin qiymətləndirilməsi."),
    ("onkomarker", "Onkomarkerlər", "svc-onkomarker.jpg", "Şiş markerlərinin təyini ilə onkoloji xəstəliklərin erkən aşkarlanması və müalicənin izlənməsi."),
    ("allerqologiya", "Allerqologiya", "svc-allerqologiya.jpg", "Qida, tozcuq, ev tozu və digər allergenlərə qarşı həssaslığın laborator təyini."),
    ("toksikologiya", "Toksikologiya və dərman monitorinqi", "lab-4.jpg", "Qanda dərman səviyyələrinin izlənməsi və toksik maddələrin təyini ilə təhlükəsiz müalicə."),
    ("hamilelik", "Hamiləlik və neonatal skrininq", "svc-hamilelik.jpg", "Hamiləlik dövründə ana və döl sağlamlığının, yenidoğulmuşlarda isə anadangəlmə xəstəliklərin skrininqi."),
    ("mikrobiologiya", "Tibbi mikrobiologiya", "svc-mikrobiologiya.jpg", "Bakterial və göbələk infeksiyalarının əkmə üsulu ilə aşkarlanması və antibiotiklərə həssaslığın təyini."),
    ("molekulyar", "Molekulyar mikrobiologiya", "svc-molekulyar.jpg", "PZR və digər molekulyar üsullarla virus və bakteriyaların DNT/RNT səviyyəsində dəqiq təyini."),
]

TEST_GROUPS = ["Allergik testlər", "Biokimya", "İmmunologiya", "Daun paneli", "Dərman səviyyələri", "Hematologiya",
               "Genetik testlər", "Hormonlar", "Metabolik panel", "Mikrobiologiya", "Mikroskopik müayinələr",
               "Molekulyar testlər", "Serologiya", "Vitaminlər"]

INDIVIDUAL = [
    ("💬", "Test məsləhət xidməti", "Hansı analizi verməli olduğunuzu bilmirsiniz? Mütəxəssislərimiz sizə düzgün testi seçməyə kömək edir."),
    ("🏠", "Evdə / ünvanda nümunə alma", "Laboratoriyaya gəlməyə vaxtınız yoxdursa, nümunəni evinizdə və ya iş yerinizdə götürürük."),
    ("✨", "Sizə özəl check-up", "Yaşınıza, cinsinizə və sağlamlıq tarixçənizə uyğun fərdi müayinə proqramı."),
    ("📦", "Karqo ilə nümunə göndərmə", "Bakıdan kənarda olsanız belə, nümunənizi karqo ilə göndərib nəticəni onlayn ala bilərsiniz."),
]

CORPORATE = [
    ("🔬", "Kənar laboratoriyalara xidmət", "Digər laboratoriya və klinikalar üçün istinad laboratoriyası kimi geniş test bazası."),
    ("🤝", "Əməkdaşlıq etdiyimiz təşkilatlar", "Tibb müəssisələri və şirkətlərlə uzunmüddətli tərəfdaşlıq və onlayn nəticə sistemi."),
    ("🏭", "Peşə xəstəliklərinin skrininqi", "İş yerlərində aparılan müayinələr və işçilərin sağlamlığının mütəmadi nəzarəti."),
    ("🧬", "Daşıyıcı müayinəsi", "İrsi xəstəliklərin daşıyıcılığının laborator müayinəsi."),
]

CHECKUPS = [
    ("Kişilər üçün", "40 yaşadək kişilər üçün əsas sağlamlıq göstəricilərinin yoxlanışı.", "♂"),
    ("40+ kişilər üçün", "40 yaşdan yuxarı kişilər üçün genişləndirilmiş müayinə.", "♂"),
    ("Qadınlar üçün", "40 yaşadək qadınlar üçün əsas sağlamlıq göstəricilərinin yoxlanışı.", "♀"),
    ("40+ qadınlar üçün", "40 yaşdan yuxarı qadınlar üçün genişləndirilmiş müayinə.", "♀"),
    ("Uşaq check-up", "Uşaqların böyümə və inkişafına uyğun laborator müayinə.", "☺"),
    ("Kardioloji", "Ürək-damar sağlamlığı və risk faktorlarının qiymətləndirilməsi.", "♥"),
    ("Qadın onkoloji skrininq", "Qadınlarda onkoloji xəstəliklərin erkən aşkarlanması.", "◎"),
    ("Kişi onkoloji skrininq", "Kişilərdə onkoloji xəstəliklərin erkən aşkarlanması.", "◎"),
]

TIMELINE = [
    ("2017", "Bakıda, HB Güven Klinikasının daxilində ilk laboratoriya fəaliyyətə başladı."),
    ("2017", "Sentyabrda ikinci laboratoriya Gəncədə açıldı."),
    ("2018", "Payızda Tovuz laboratoriyası açıldı. İlin sonunda Bakıda Mərkəzi Laboratoriya istifadəyə verildi."),
    ("2019", "2002-ci ildən fəaliyyət göstərən Acıbadem Labmed laboratoriyası ilə əməkdaşlıq müqaviləsi imzalandı."),
    ("2020", "Sumqayıt laboratoriyası fəaliyyətə başladı."),
    ("2026", "Laboratoriya və patoloji xidmətləri Gəncədə istifadəyə verildi."),
]

BRANCHES = [
    ("Mərkəzi Laboratoriya", "Bakı", "Əhməd Rəcəbli 19R", True),
    ("Gənclik filialı", "Bakı", "HB Güven Klinikası", False),
    ("Gəncə filialı", "Gəncə", "Laboratoriya və patologiya xidmətləri", False),
    ("Tovuz filialı", "Tovuz", "İnci Clinic Tovuz", False),
    ("Zaqatala filialı", "Zaqatala", "", False),
]

NEWS = [
    ("29 sentyabr 2026", "Bakıda zülal elektroforezi və oliqoklonal zolaqların təyini: HYDRASYS 2 SCAN yeniliyi", "news-hydrasys.jpg",
     "İnci Laboratoriyalarında HYDRASYS 2 SCAN sistemi ilə zülal elektroforezi və oliqoklonal zolaqların təyini artıq mümkündür."),
    ("10 aprel 2026", "İnci Laboratoriyaları Beynəlxalq Konfransda", "news-konfrans.png",
     "Mütəxəssislərimiz beynəlxalq konfransda iştirak edərək laborator diaqnostika sahəsində təcrübələrini bölüşdülər."),
    ("15 mart 2026", "Laboratoriya və Patoloji Xidmətləri artıq Gəncədə", "news-gence.jpg",
     "İnci Laboratoriyalarının laboratoriya və patoloji xidmətləri artıq Gəncə şəhərində də əlçatandır."),
]

NAV = [
    ("index.html", "Ana səhifə"),
    ("haqqimizda.html", "Haqqımızda"),
    ("xidmetler.html", "Xidmətlər"),
    ("check-up.html", "Check-up"),
    ("filiallar.html", "Filiallar"),
    ("xeberler.html", "Xəbərlər"),
    ("elaqe.html", "Əlaqə"),
]

SERVICE_SUB = [("xidmetler.html", "Laborator istiqamətlər"), ("ferdi.html", "Fərdi xidmətlər"), ("korporativ.html", "Korporativ xidmətlər"), (LINKS["tests"], "Test bələdçisi ↗")]


ICON = dict(
    phone='<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>',
    fb='<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.25-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.3H8v3h2.5V21z"/></svg>',
    ig='<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 7.3a4.7 4.7 0 1 0 0 9.4 4.7 4.7 0 0 0 0-9.4zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm6-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM21 8.1c-.1-1.5-.4-2.8-1.5-3.9S17.1 2.8 15.6 2.7C14 2.6 10 2.6 8.4 2.7 6.9 2.8 5.6 3.1 4.5 4.2S3.1 6.6 3 8.1c-.1 1.6-.1 6.2 0 7.8.1 1.5.4 2.8 1.5 3.9s2.4 1.4 3.9 1.5c1.6.1 5.6.1 7.2 0 1.5-.1 2.8-.4 3.9-1.5s1.4-2.4 1.5-3.9c.1-1.6.1-6.2 0-7.8zm-2 9.5a3 3 0 0 1-1.7 1.7c-1.2.5-4 .4-5.3.4s-4.1.1-5.3-.4a3 3 0 0 1-1.7-1.7c-.5-1.2-.4-4-.4-5.3s-.1-4.1.4-5.3a3 3 0 0 1 1.7-1.7c1.2-.5 4-.4 5.3-.4s4.1-.1 5.3.4a3 3 0 0 1 1.7 1.7c.5 1.2.4 4 .4 5.3s.1 4.1-.4 5.3z"/></svg>',
    yt='<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8c1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3z"/></svg>',
)


def social_icons(cls="soc"):
    return "".join(f'<a href="{LINKS[k]}" target="_blank" rel="noopener" class="{cls} {cls}--{k}" aria-label="{n}">{ICON[k]}</a>'
                   for k, n in (("ig", "Instagram"), ("fb", "Facebook"), ("yt", "YouTube")))


# ---------------------------------------------------------------- i18n
# Saytın AZ versiyası şablonlardan yaranır, RU və EN versiyaları isə hazır
# HTML-dəki mətnlərin i18n.py lüğəti ilə əvəzlənməsi yolu ilə qurulur.
LANGS = ["az", "en"]
LANG_NAMES = {"az": "AZ", "ru": "RU", "en": "EN"}
MISSING = set()
HAS_WORD = re.compile(r"[A-Za-zƏəİıÖöÜüĞğŞşÇç]{2,}")
SKIP = re.compile(r"^(\S+@\S+|https?://\S+|[\d\s()+*.:–-]+)$")


def tr(text, lang):
    if lang == "az":
        return text
    if text in TR:
        return TR[text][0 if lang == "ru" else 1]
    if not HAS_WORD.search(text) or SKIP.match(text):
        return text
    if " — " in text:
        return " — ".join(tr(part, lang) for part in text.split(" — "))
    MISSING.add(text)
    return text


def tr_keep_space(seg, lang):
    core = seg.strip()
    if not core:
        return seg
    i = seg.index(core)
    return seg[:i] + tr(core, lang) + seg[i + len(core):]


def lang_links(lang, filename):
    def href(target):
        if target == lang:
            return filename
        base = "" if lang == "az" else "../"
        return base + ("" if target == "az" else target + "/") + filename
    return "".join(f'<a href="{href(l)}" hreflang="{l}"{" class=on" if l == lang else ""}>{LANG_NAMES[l]}</a>' for l in LANGS)


def localize(html, lang, filename):
    html = html.replace("@@LANGS@@", lang_links(lang, filename))
    if lang == "az":
        return html
    html = html.replace('<html lang="az">', f'<html lang="{lang}">')
    for a, b in (('href="assets/', 'href="../assets/'), ('src="assets/', 'src="../assets/'),
                 ('href="styles.css', 'href="../styles.css'), ('src="script.js', 'src="../script.js')):
        html = html.replace(a, b)

    def fix_tag(tag):
        def attr(m):
            name, val = m.group(1), m.group(2)
            if name == "content" and not tag.startswith('<meta name="description"'):
                return m.group(0)
            return f'{name}="{tr(val, lang)}"'
        tag = re.sub(r'\b(alt|title|aria-label|placeholder|content)="([^"]*)"', attr, tag)
        tag = re.sub(r'(wa\.me/\d+\?text=)([^"]+)', lambda m: m.group(1) + quote(tr(unquote(m.group(2)), lang)), tag)
        return tag

    parts = re.split(r"(<svg.*?</svg>|<[^>]+>)", html, flags=re.S)
    return "".join(fix_tag(p) if p.startswith("<") else tr_keep_space(p, lang) for p in parts)


# ---------------------------------------------------------------- helpers
def nav_html(active):
    out = []
    for href, label in NAV:
        cls = ' class="active"' if href == active or (href == "xidmetler.html" and active in ("ferdi.html", "korporativ.html")) else ""
        if href == "xidmetler.html":
            sub = "".join(f'<a href="{h}"{" target=_blank rel=noopener" if h.startswith("http") else ""}>{l}</a>' for h, l in SERVICE_SUB)
            out.append(f'<div class="dd"><a href="{href}"{cls}>{label}<i>▾</i></a><div class="dd__menu">{sub}</div></div>')
        else:
            out.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n          ".join(out)


def ext(url, text, cls=""):
    return f'<a href="{url}" target="_blank" rel="noopener" class="{cls}">{text}</a>'


def ver(name):
    """Fayl dəyişəndə URL də dəyişsin ki, brauzer və Cloudflare köhnə faylı göstərməsin."""
    return hashlib.md5((OUT / name).read_bytes()).hexdigest()[:8]


def page(filename, title, desc, body, dark_hero=True):
    full_title = "İnci Laboratoriyaları — Azərbaycanın bir incisi" if filename == "index.html" else f"{title} — İnci Laboratoriyaları"
    html = f"""<!DOCTYPE html>
<html lang="az">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{full_title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#fffcf2">
  <link rel="icon" href="assets/incilab-logo.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v={ver('styles.css')}">
</head>
<body>

  <header class="header" id="header">
    <div class="header__bar">
      <a href="index.html" class="logo"><img src="assets/incilab-logo.png" alt="İnci Laboratoriyaları"></a>
      <nav class="nav" id="nav">
          {nav_html(filename)}
          <div class="nav__soc">{social_icons()}</div>
      </nav>
      <div class="header__actions">
        <a href="tel:{HOTLINE}" class="hotline" aria-label="Qaynar xətt">{ICON["phone"]}<b>*{HOTLINE}</b></a>
        <div class="langs">@@LANGS@@</div>
        {ext(LINKS["results"], "Onlayn nəticə", "btn btn--pearl btn--sm")}
      </div>
      <div class="langs langs--m">@@LANGS@@</div>
      <button class="burger" id="burger" aria-label="Menyu"><span></span><span></span></button>
    </div>
  </header>

  <aside class="rail" aria-label="Sosial şəbəkələr">{social_icons()}<span>Bizi izləyin</span></aside>

{body}

  <footer class="footer">
    <div class="footer__glow"></div>
    <div class="container footer__top">
      <div class="footer__brand">
        <div class="footer__pearl"></div>
        <p class="footer__slogan">Sağlamlığınız üçün daim xidmətinizdəyik.</p>
      </div>
      <div>
        <h5>Menyu</h5>
        {"".join(f'<a href="{h}">{l}</a>' for h, l in NAV)}
      </div>
      <div>
        <h5>Onlayn</h5>
        {ext(LINKS["results"], "Fərdi nəticələr")}
        {ext(LINKS["results_org"], "Təşkilatlar üçün nəticələr")}
        {ext(LINKS["booking"], "E-randevu")}
        {ext(LINKS["tests"], "Test bələdçisi")}
        {ext(LINKS["bulletin"], "E-bülleten")}
      </div>
      <div>
        <h5>Əlaqə</h5>
        <a href="tel:{HOTLINE}" class="f-ic">{ICON["phone"]} *{HOTLINE}</a>
        <a href="tel:{PHONE_TEL}">{PHONE}</a>
        <a href="https://wa.me/{WA_TEL}" target="_blank" rel="noopener">WhatsApp: {WA}</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <p class="footer__hours">B.e.–C. 08:00–20:00<br>Şənbə 08:00–18:00<br>Bazar — istirahət</p>
      </div>
    </div>
    <div class="container footer__bottom">
      <span>© <span id="year"></span> İnci Laboratoriyaları. Müəllif haqları qorunur.</span>
      <span class="socials">{social_icons()}</span>
    </div>
  </footer>

  <a href="https://wa.me/{WA_TEL}" class="wa" target="_blank" rel="noopener" aria-label="WhatsApp">
    <svg viewBox="0 0 32 32" width="28" height="28" fill="#fff"><path d="M16 3C9 3 3.3 8.7 3.3 15.7c0 2.2.6 4.4 1.7 6.3L3 29l7.2-1.9c1.8 1 3.9 1.5 5.9 1.5 7 0 12.7-5.7 12.7-12.7S23 3 16 3zm0 23.3c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.3 1.1 1.1-4.2-.3-.4c-1.1-1.7-1.6-3.6-1.6-5.5C5.1 9.9 10 5.1 16 5.1s10.9 4.9 10.9 10.9S22 26.3 16 26.3zm6-8.2c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2-.2-.3 0-.5.1-.7l.5-.6c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.8 5 .8.4 1.4.6 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg>
  </a>

  <script src="script.js?v={ver('script.js')}"></script>
</body>
</html>
"""
    for lang in LANGS:
        out = localize(html, lang, filename)
        d = OUT if lang == "az" else OUT / lang
        d.mkdir(exist_ok=True)
        (d / filename).write_text(out, encoding="utf-8")
    print("✓", filename)


def page_hero(title, eyebrow, sub=""):
    return f"""  <section class="phero">
    <div class="phero__pearl"></div>
    <div class="container phero__inner">
      <span class="eyebrow eyebrow--light">{eyebrow}</span>
      <h1>{title}</h1>
      {f"<p>{sub}</p>" if sub else ""}
    </div>
  </section>"""


def quick_actions():
    items = [
        (LINKS["results"], "01", "Onlayn nəticə", "Analiz nəticənizi evdən yoxlayın"),
        (LINKS["booking"], "02", "E-randevu", "Növbə gözləmədən vaxt seçin"),
        (LINKS["tests"], "03", "Test bələdçisi", "4000+ test haqqında məlumat"),
        ("ferdi.html", "04", "Evdə nümunə", "Nümunəni ünvanınızda götürək"),
    ]
    out = []
    for href, n, t, d in items:
        tgt = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a href="{href}"{tgt} class="qa reveal"><span class="qa__n">{n}</span><b>{t}</b><small>{d}</small><i>→</i></a>')
    return "\n        ".join(out)


def services_bento(limit=None):
    out = []
    for i, (slug, title, img, desc) in enumerate(SERVICES[:limit] if limit else SERVICES):
        out.append(f"""        <a href="xidmetler.html#{slug}" class="svc reveal{' svc--wide' if i in (0, 5) else ''}">
          <img src="assets/{img}" alt="{title}" loading="lazy">
          <div class="svc__body"><span class="svc__n">{i + 1:02d}</span><h3>{title}</h3><p>{desc}</p></div>
        </a>""")
    return "\n".join(out)


def marquee():
    items = "".join(f"<span>{t}</span><i>◆</i>" for t in TEST_GROUPS)
    return f"""  <div class="marquee" aria-hidden="true"><div class="marquee__track">{items}{items}</div></div>"""


def cards(items, cls="card"):
    return "\n".join(f'<div class="{cls} reveal"><span class="{cls}__ic">{ic}</span><h3>{t}</h3><p>{d}</p></div>' for ic, t, d in items)


def checkup_cards():
    return "\n".join(f"""        <div class="cu reveal">
          <div class="cu__pearl"><span>{sym}</span></div>
          <h3>{name}</h3>
          <p>{d}</p>
          <a href="https://wa.me/{WA_TEL}?text={('Salam! ' + name + ('' if 'check-up' in name else ' check-up') + ' paketi haqqında məlumat almaq istəyirəm.').replace(' ', '%20')}" target="_blank" rel="noopener" class="cu__link">Məlumat al →</a>
        </div>""" for name, d, sym in CHECKUPS)


def branches_html():
    out = []
    for name, city, note, main in BRANCHES:
        out.append(f"""        <div class="br reveal{' br--main' if main else ''}">
          <span class="br__city">{city}</span>
          <h3>{name}</h3>
          {f'<p>{note}</p>' if note else ''}
          {f'<div class="br__map"><iframe loading="lazy" title="{name}" src="https://maps.google.com/maps?q=%C6%8Fhm%C9%99d+R%C9%99c%C9%99bli+19R,+Bak%C4%B1&output=embed"></iframe></div>' if main else ''}
          <a href="tel:{HOTLINE}" class="br__tel">*{HOTLINE}</a>
        </div>""")
    return "\n".join(out)


def news_html():
    return "\n".join(f"""        <article class="news reveal">
          <div class="news__img"><img src="assets/{img}" alt="" loading="lazy"></div>
          <time>{date}</time>
          <h3>{title}</h3>
          <p>{text}</p>
        </article>""" for date, title, img, text in NEWS)


def stats():
    return """      <div class="stats">
        <div class="stat reveal"><b data-count="4000">0</b><i>+</i><span>test</span></div>
        <div class="stat reveal"><b data-count="20">0</b><i>+</i><span>xidmət</span></div>
        <div class="stat reveal"><b data-count="5">0</b><i>+</i><span>filial</span></div>
        <div class="stat reveal"><b data-count="50">0</b><i>+</i><span>əməkdaş</span></div>
      </div>"""


def steps():
    s = [("Randevu", "E-randevu, *1113 və ya WhatsApp ilə vaxt seçin."),
         ("Nümunə", "Filialda və ya evinizdə nümunə götürülür."),
         ("Analiz", "Tam avtomatlaşdırılmış analizatorlarda, beynəlxalq standartlarla."),
         ("Nəticə", "Nəticə onlayn olaraq sizə təqdim edilir.")]
    return "\n".join(f'<li class="step reveal"><span>{i}</span><h4>{t}</h4><p>{d}</p></li>' for i, (t, d) in enumerate(s, 1))


CTA = f"""  <section class="cta">
    <div class="container cta__inner reveal">
      <div class="cta__pearl"></div>
      <div>
        <h2>Sağlamlığınıza bu gün diqqət edin.</h2>
        <p>Randevu, məsləhət və ya check-up üçün bizimlə əlaqə saxlayın.</p>
      </div>
      <div class="cta__actions">
        {ext(LINKS["booking"], "E-randevu", "btn btn--pearl")}
        <a href="tel:{HOTLINE}" class="btn btn--line">*{HOTLINE}</a>
      </div>
    </div>
  </section>"""


# ---------------------------------------------------------------- pages
def build_home():
    body = f"""  <section class="hero">
    <div class="hero__grid"></div>
    <div class="container hero__inner">
      <div class="hero__text">
        <span class="eyebrow eyebrow--light reveal">Klinik laborator diaqnostika · 2017-ci ildən</span>
        <h1 class="reveal">Azərbaycanın bir incisi.</h1>
        <p class="reveal">Klinik laborator diaqnostikanın bütün sahələrində keyfiyyətli və dəqiq xidmət — tam avtomatlaşdırılmış analizatorlar, beynəlxalq standartlar və 4000+ testlik geniş baza.</p>
        <div class="hero__btns reveal">
          {ext(LINKS["results"], "Onlayn nəticə", "btn btn--pearl")}
          {ext(LINKS["booking"], "E-randevu", "btn btn--line")}
        </div>
        <div class="hero__social reveal"><span>Bizi izləyin</span>{social_icons()}</div>
      </div>
      <div class="hero__visual" id="pearlScene">
        <div class="orbit orbit--1"><span></span></div>
        <div class="orbit orbit--2"><span></span></div>
        <div class="orbit orbit--3"><span></span></div>
        <div class="pearl" id="pearl"><div class="pearl__shine"></div></div>
        <div class="chip chip--a"><b>ISO 15189</b><small>standartlarına uyğunlaşma</small></div>
        <div class="chip chip--b"><b>4000+</b><small>test</small></div>
        <div class="chip chip--c"><b>Acıbadem Labmed</b><small>əməkdaşlıq</small></div>
      </div>
    </div>
    <div class="container qas">
        {quick_actions()}
    </div>
  </section>

{marquee()}

  <section class="section">
    <div class="container">
      <div class="head reveal">
        <div><span class="eyebrow">Xidmət sahələri</span><h2>Bir damladan dəqiq cavaba.</h2></div>
        <p>Tibbi biokimyadan molekulyar mikrobiologiyaya qədər — 10 laborator istiqamət bir ünvanda.</p>
      </div>
      <div class="bento">
{services_bento()}
      </div>
    </div>
  </section>

  <section class="section section--ink">
    <div class="container">
      <div class="head head--center reveal">
        <span class="eyebrow eyebrow--light">Necə işləyir</span>
        <h2>Dörd addımda nəticə.</h2>
      </div>
      <ol class="steps">
{steps()}
      </ol>
{stats()}
    </div>
  </section>

  <section class="section">
    <div class="container split">
      <div class="split__col reveal">
        <span class="eyebrow">Fərdi</span>
        <h2>Sizin üçün</h2>
        <div class="mini-list">{"".join(f'<a href="ferdi.html" class="mini"><span>{ic}</span><div><b>{t}</b><small>{d}</small></div></a>' for ic, t, d in INDIVIDUAL)}</div>
      </div>
      <div class="split__col split__col--alt reveal">
        <span class="eyebrow">Korporativ</span>
        <h2>Təşkilatlar üçün</h2>
        <div class="mini-list">{"".join(f'<a href="korporativ.html" class="mini"><span>{ic}</span><div><b>{t}</b><small>{d}</small></div></a>' for ic, t, d in CORPORATE)}</div>
      </div>
    </div>
  </section>

  <section class="section section--nacre">
    <div class="container">
      <div class="head reveal">
        <div><span class="eyebrow">Check-up</span><h2>Sağlamlığınızın incilərini qoruyun.</h2></div>
        <p>Yaşa, cinsə və ehtiyaca uyğun 8 check-up paketi. Hansının sizə uyğun olduğunu birlikdə seçək.</p>
      </div>
      <div class="cus">
{checkup_cards()}
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container about-home">
      <div class="about-home__img reveal"><img src="assets/lab-1.jpg" alt="İnci Laboratoriyalarında analiz"><div class="badge-round"><b>2017</b><span>ildən</span></div></div>
      <div class="reveal">
        <span class="eyebrow">Biz kimik</span>
        <h2>Daim inkişaf edən laboratoriya.</h2>
        <p>İnci Laboratoriyaları biokimya, mikrobiologiya, immunologiya və molekulyar genetika sahələrində tam avtomatlaşdırılmış analizatorlarla xidmət göstərir. EUCAST, CLSI və ISO kimi müstəqil qurumların keyfiyyət standartları əsas götürülür.</p>
        <ul class="ticks">
          <li>Tibbi mikrobiologiya və biokimya mütəxəssisləri</li>
          <li>Ən son texnologiyalar</li>
          <li>Geniş test bazası</li>
        </ul>
        <a href="haqqimizda.html" class="btn btn--wine">Haqqımızda ətraflı</a>
      </div>
    </div>
  </section>

  <section class="section section--soft">
    <div class="container">
      <div class="head reveal">
        <div><span class="eyebrow">Xəbərlər</span><h2>Son yeniliklər.</h2></div>
        <a href="xeberler.html" class="link-arrow">Bütün xəbərlər →</a>
      </div>
      <div class="newsgrid">
{news_html()}
      </div>
    </div>
  </section>

{CTA}"""
    page("index.html", "Ana səhifə", "İnci Laboratoriyaları — klinik laborator diaqnostikanın bütün sahələrində keyfiyyətli və dəqiq xidmət. 4000+ test, onlayn nəticə, evdə nümunə alma.", body)


def build_about():
    tl = "\n".join(f'<li class="tl reveal"><b>{y}</b><p>{t}</p></li>' for y, t in TIMELINE)
    body = f"""{page_hero("Biz kimik?", "Haqqımızda", "2017-ci ildən klinik laborator diaqnostikanın bütün sahələrində xidmətinizdəyik.")}

  <section class="section">
    <div class="container about-home">
      <div class="about-home__img reveal"><img src="assets/lab-4.jpg" alt="Mikroskop"><div class="badge-round"><b>4000+</b><span>test</span></div></div>
      <div class="reveal">
        <span class="eyebrow">İnci Laboratoriyaları</span>
        <h2>Bütün sahələrdə keyfiyyət və dəqiqlik.</h2>
        <p>İnci Laboratoriyaları klinik laborator diaqnostikanın bütün sahələrində — biokimya, mikrobiologiya, immunologiya və molekulyar genetika üzrə xidmət göstərir. Laboratoriyamızda tam avtomatlaşdırılmış biokimyəvi, mikrobioloji, immunoloji və genetik analizatorlardan istifadə olunur.</p>
        <p>Xidmətlərimizdə EUCAST, CLSI və ISO kimi müstəqil qurumların keyfiyyət standartları əsas istiqamət götürülür. Laboratoriyamız fəaliyyətini ISO 15189 akkreditasiyasının tələblərinə uyğunlaşdırır.</p>
      </div>
    </div>
  </section>

  <section class="section section--ink">
    <div class="container vm">
      <div class="vm__card reveal">
        <span class="eyebrow eyebrow--light">Baxışımız</span>
        <p>Qabaqcıl klinik laboratoriya xidmətləri göstərərək tərəfdaş səhiyyə müəssisələrində xəstə baxımı və təhlükəsizliyində mükəmməlliyi təmin etməyə töhfə vermək və pasiyentlərin etimadını qazanmaq.</p>
      </div>
      <div class="vm__card reveal">
        <span class="eyebrow eyebrow--light">Missiyamız</span>
        <p>Yüksək keyfiyyətli və etibarlı laboratoriya xidmətləri əsasında Azərbaycanda və regionda ən çox seçilən istinad klinik laboratoriyası olmaq.</p>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="head head--center reveal"><span class="eyebrow">Tariximiz</span><h2>İlk laboratoriyadan şəbəkəyə.</h2></div>
      <ol class="timeline">
{tl}
      </ol>
    </div>
  </section>

  <section class="section section--nacre">
    <div class="container">
      <div class="head head--center reveal"><span class="eyebrow">Keyfiyyət</span><h2>Etibar edilən standartlar.</h2></div>
      <div class="quality">
        <div class="q reveal"><b>ISO 15189</b><span>Tibbi laboratoriyalar üçün akkreditasiya tələblərinə uyğunlaşma</span></div>
        <div class="q reveal"><b>EUCAST</b><span>Antimikrob həssaslıq testləri üzrə Avropa standartları</span></div>
        <div class="q reveal"><b>CLSI</b><span>Klinik və laborator standartlar institutu</span></div>
        <div class="q reveal"><b>Acıbadem Labmed</b><span>2019-cu ildən əməkdaşlıq</span></div>
      </div>
{stats()}
    </div>
  </section>

{CTA}"""
    page("haqqimizda.html", "Haqqımızda", "İnci Laboratoriyaları haqqında: tariximiz, baxışımız və missiyamız, keyfiyyət standartları.", body)


def build_services():
    rows = "\n".join(f"""      <article class="srow reveal" id="{slug}">
        <div class="srow__img"><img src="assets/{img}" alt="{title}" loading="lazy"></div>
        <div class="srow__body"><span class="svc__n">{i:02d}</span><h3>{title}</h3><p>{desc}</p>
          {ext(LINKS["tests"], "Testlərə bax →", "link-arrow")}</div>
      </article>""" for i, (slug, title, img, desc) in enumerate(SERVICES, 1))
    groups = "".join(f"<span>{g}</span>" for g in TEST_GROUPS)
    body = f"""{page_hero("Xidmət sahələri", "Xidmətlər", "Klinik laborator diaqnostikanın 10 istiqaməti və 4000+ test.")}

  <section class="section">
    <div class="container srows">
{rows}
    </div>
  </section>

  <section class="section section--nacre">
    <div class="container">
      <div class="head reveal">
        <div><span class="eyebrow">Test bələdçisi</span><h2>Test qrupları.</h2></div>
        {ext(LINKS["tests"], "Test bələdçisini aç ↗", "btn btn--wine")}
      </div>
      <div class="tags reveal">{groups}</div>
    </div>
  </section>

{CTA}"""
    page("xidmetler.html", "Xidmətlər", "İnci Laboratoriyalarının xidmət sahələri: biokimya, immunologiya, patologiya, hematologiya, onkomarkerlər, allerqologiya, mikrobiologiya və s.", body)


def build_individual():
    body = f"""{page_hero("Fərdi xidmətlər", "Xidmətlər", "Rahatlığınız üçün düşünülmüş xidmətlər.")}

  <section class="section">
    <div class="container">
      <div class="cards">
{cards(INDIVIDUAL)}
      </div>
    </div>
  </section>

  <section class="section section--ink">
    <div class="container">
      <div class="head head--center reveal"><span class="eyebrow eyebrow--light">Necə işləyir</span><h2>Dörd addımda nəticə.</h2></div>
      <ol class="steps">
{steps()}
      </ol>
    </div>
  </section>

{CTA}"""
    page("ferdi.html", "Fərdi xidmətlər", "Test məsləhəti, evdə nümunə alma, fərdi check-up və karqo ilə nümunə göndərmə.", body)


def build_corporate():
    body = f"""{page_hero("Korporativ xidmətlər", "Xidmətlər", "Tibb müəssisələri, laboratoriyalar və şirkətlər üçün etibarlı tərəfdaş.")}

  <section class="section">
    <div class="container">
      <div class="cards">
{cards(CORPORATE)}
      </div>
      <div class="org-box reveal">
        <div><h3>Təşkilatlar üçün onlayn nəticə</h3><p>Tərəfdaş səhiyyə müəssisələri nəticələri xüsusi portal vasitəsilə əldə edir.</p></div>
        {ext(LINKS["results_org"], "Portala daxil ol ↗", "btn btn--wine")}
      </div>
    </div>
  </section>

{CTA}"""
    page("korporativ.html", "Korporativ xidmətlər", "Kənar laboratoriyalara xidmət, peşə xəstəliklərinin skrininqi, daşıyıcı müayinəsi.", body)


def build_checkup():
    body = f"""{page_hero("Check-up paketləri", "Check-up", "Xəstəliyi gözləməyin — sağlamlığınızı vaxtında yoxlayın.")}

  <section class="section">
    <div class="container">
      <div class="cus">
{checkup_cards()}
      </div>
      <div class="org-box reveal">
        <div><h3>Sizə özəl check-up</h3><p>Hazır paketlər uyğun deyilsə, yaşınıza və sağlamlıq tarixçənizə uyğun fərdi proqram hazırlayaq.</p></div>
        <a href="https://wa.me/{WA_TEL}" target="_blank" rel="noopener" class="btn btn--wine">WhatsApp ilə yaz</a>
      </div>
    </div>
  </section>

{CTA}"""
    page("check-up.html", "Check-up", "İnci Laboratoriyalarının check-up paketləri: kişilər, qadınlar, uşaqlar, kardioloji və onkoloji skrininq.", body)


def build_branches():
    body = f"""{page_hero("Filiallarımız", "Filiallar", "Bakı, Gəncə, Tovuz və Zaqatalada xidmətinizdəyik.")}

  <section class="section">
    <div class="container brs">
{branches_html()}
    </div>
  </section>

{CTA}"""
    page("filiallar.html", "Filiallar", "İnci Laboratoriyalarının filialları: Mərkəzi Laboratoriya, Gənclik, Gəncə, Tovuz, Zaqatala.", body)


def build_news():
    body = f"""{page_hero("Xəbərlər", "Media", "Yeniliklər, kampaniyalar və elmi fəaliyyət.")}

  <section class="section">
    <div class="container">
      <div class="newsgrid">
{news_html()}
      </div>
      <div class="org-box reveal">
        <div><h3>E-bülleten</h3><p>Laborator diaqnostika üzrə elmi məlumatlar və yeniliklər.</p></div>
        {ext(LINKS["bulletin"], "E-bülleteni oxu ↗", "btn btn--wine")}
      </div>
    </div>
  </section>"""
    page("xeberler.html", "Xəbərlər", "İnci Laboratoriyalarının xəbərləri.", body)


def build_contact():
    body = f"""{page_hero("Bizimlə əlaqə", "Əlaqə", "Sualınız və ya təklifiniz var? Məmnuniyyətlə cavablandırarıq.")}

  <section class="section">
    <div class="container contact">
      <div class="contact__info reveal">
        <a href="tel:{HOTLINE}" class="ci ci--big"><small class="f-ic">{ICON["phone"]}</small><b>*{HOTLINE}</b></a>
        <a href="tel:{PHONE_TEL}" class="ci"><small>Telefon</small><b>{PHONE}</b></a>
        <a href="https://wa.me/{WA_TEL}" target="_blank" rel="noopener" class="ci"><small>WhatsApp</small><b>{WA}</b></a>
        <a href="mailto:{EMAIL}" class="ci"><small>E-poçt</small><b>{EMAIL}</b></a>
        <div class="ci"><small>Mərkəzi Laboratoriya</small><b>{ADDRESS}</b></div>
        <div class="ci"><small>İş saatları</small><b>B.e.–C. 08:00–20:00 · Ş. 08:00–18:00</b></div>
      </div>
      <form class="form reveal" id="form">
        <h3>Mesaj göndərin</h3>
        <label>Ad, soyad<input name="name" required></label>
        <label>Telefon<input name="phone" type="tel" required placeholder="+994"></label>
        <label>Mövzu<select name="topic"><option>Randevu</option><option>Test məsləhəti</option><option>Evdə nümunə alma</option><option>Check-up</option><option>Korporativ əməkdaşlıq</option><option>Digər</option></select></label>
        <label>Mesaj<textarea name="message" rows="4"></textarea></label>
        <button class="btn btn--wine btn--full">WhatsApp ilə göndər</button>
      </form>
    </div>
    <div class="container"><div class="map reveal"><iframe loading="lazy" title="Mərkəzi Laboratoriya" src="https://maps.google.com/maps?q=%C6%8Fhm%C9%99d+R%C9%99c%C9%99bli+19R,+Bak%C4%B1&output=embed"></iframe></div></div>
  </section>"""
    page("elaqe.html", "Əlaqə", "İnci Laboratoriyaları ilə əlaqə: *1113, (012) 464 89 20, info@incilab.az.", body)


if __name__ == "__main__":
    build_home(); build_about(); build_services(); build_individual(); build_corporate()
    build_checkup(); build_branches(); build_news(); build_contact()
    if MISSING:
        Path(OUT / "i18n_missing.txt").write_text("\n".join(sorted(MISSING)), encoding="utf-8")
        print(f"! {len(MISSING)} tərcüməsiz mətn — i18n_missing.txt")
