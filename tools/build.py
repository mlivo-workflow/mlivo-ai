#!/usr/bin/env python3
"""
Mlivo AI – Website-Build
========================
Quelle sind die deutschen Seiten (index.html, architekten/index.html).
Jeder sichtbare Text trägt seine englische Fassung als Attribut:

  data-en="…"        -> ersetzt den Text des Elements
  data-en-html="…"   -> ersetzt den Inhalt (mit HTML)
  data-en-ph / -content / -href / -alt / -aria / -class / -value / -badge
                     -> ersetzt placeholder / content / href / alt / aria-label / class / value / data-badge

Das Skript
  1. schreibt die strukturierten Daten (JSON-LD) in alle Seiten,
  2. erzeugt daraus /en/index.html und /en/architects/index.html.

Aufruf (im Repo-Ordner):  python3 tools/build.py
Benötigt: beautifulsoup4  (pip install beautifulsoup4)
"""
import json, os, re, sys
from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [  # (Quelle DE, Ziel EN, Schlüssel für JSON-LD)
    ("index.html", "en/index.html", "home"),
    ("architekten/index.html", "en/architects/index.html", "arch"),
]

BUSINESS = {
    "@type": "ProfessionalService",
    "@id": "https://mlivo-ai.at/#business",
    "name": "Mlivo AI",
    "url": "https://mlivo-ai.at/",
    "telephone": "+436604038996",
    "email": "kontakt@mlivo-ai.at",
    "image": "https://mlivo-ai.at/stadtturm-enns.jpg",
    "logo": "https://mlivo-ai.at/favicon.svg",
    "priceRange": "€ 590 – € 7.090",
    "address": {"@type": "PostalAddress", "streetAddress": "Gerstmayrgutstraße 1", "postalCode": "4470",
                "addressLocality": "Enns", "addressRegion": "Oberösterreich", "addressCountry": "AT"},
    "areaServed": ["Linz", "Linz-Land", "Enns", "Oberösterreich"],
    "founder": {"@type": "Person", "name": "Alen Mlivo", "honorificPrefix": "Ing."},
}
DESC = {
    "de": "KI-Partner für kleine und mittlere Betriebe im Raum Linz und Enns: KI-Workshops, KI-Assessment, Begleitung bei der Umsetzung, KI-Agenten sowie KI für Architekten (CAD per MCP, 4D-Bauablauf).",
    "en": "AI partner for small and medium-sized businesses in the Linz and Enns region: AI workshops, AI assessment, implementation support, AI agents and AI for architects (CAD via MCP, 4D construction schedules).",
}
KNOWS = {
    "de": ["KI-Schulung", "KI-Assessment", "KI-Agenten", "Automatisierung", "n8n", "Make.com", "MCP-Connectoren", "FreeCAD", "KI für Architekten", "4D-Bauablaufvisualisierung"],
    "en": ["AI training", "AI assessment", "AI agents", "Automation", "n8n", "Make.com", "MCP connectors", "FreeCAD", "AI for architects", "4D construction scheduling"],
}


def faq_from(soup):
    out = []
    for d in soup.select("#faq details"):
        q, a = d.find("summary"), d.find("p")
        out.append({"@type": "Question", "name": q.get_text(" ", strip=True),
                    "acceptedAnswer": {"@type": "Answer", "text": a.get_text(" ", strip=True)}})
    return out


def ld_json(soup, lang, key):
    biz = dict(BUSINESS, description=DESC[lang], knowsAbout=KNOWS[lang])
    graph = [biz]
    if key == "home":
        faq = faq_from(soup)
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": faq})
    else:
        graph.append({"@type": "Service", "name": "KI für Architekten & Planer" if lang == "de" else "AI for architects & planners",
                      "provider": {"@id": "https://mlivo-ai.at/#business"},
                      "areaServed": "Oberösterreich",
                      "serviceType": ["MCP-Connector für FreeCAD", "4D-Bauablaufvisualisierung"] if lang == "de"
                      else ["MCP connector for FreeCAD", "4D construction-schedule visualisation"]})
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<!--ld:start--><script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n</script><!--ld:end-->'


def put_ld(html, block):
    return re.sub(r"<!--ld:start-->.*?<!--ld:end-->", lambda m: block, html, flags=re.S)


ATTR_MAP = {"data-en-ph": "placeholder", "data-en-content": "content", "data-en-href": "href",
            "data-en-alt": "alt", "data-en-aria": "aria-label", "data-en-class": "class",
            "data-en-value": "value", "data-en-badge": "data-badge"}


def to_english(html):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("html")
    root["lang"] = "en"
    root.attrs.pop("data-en-lang", None)
    missing = []
    for el in soup.find_all(attrs={"data-en": True}):
        el.clear(); el.append(el["data-en"]); del el["data-en"]
    for el in soup.find_all(attrs={"data-en-html": True}):
        frag = BeautifulSoup(el["data-en-html"], "html.parser")
        el.clear()
        for c in list(frag.contents):
            el.append(c)
        del el["data-en-html"]
    for src, dst in ATTR_MAP.items():
        for el in soup.find_all(attrs={src: True}):
            el[dst] = el[src]; del el[src]
    # Warnung: sichtbarer Text mit Umlauten ohne Übersetzung
    for t in soup.find_all(string=re.compile("[äöüÄÖÜß]")):
        if not isinstance(t, Comment) and t.parent.name not in ("script", "style") and not any(k in t for k in ("Gerstmayrgutstraße", "UStG", "WKO OÖ")):
            missing.append(t.strip()[:70])
    return str(soup), missing


def nbsp_fix(html):
    """Unsichtbare Sonderzeichen als HTML-Entities schreiben (eindeutig im Quelltext)."""
    html = html.replace("\u00a0", "&nbsp;").replace("\ufe0f", "&#xFE0F;").replace("\u2212", "&minus;")
    return "\n".join(l.rstrip() for l in html.split("\n"))


def main():
    for src, dst, key in PAGES:
        p = os.path.join(ROOT, src)
        html = open(p, encoding="utf-8").read()
        soup = BeautifulSoup(html, "html.parser")
        html = put_ld(html, ld_json(soup, "de", key))
        open(p, "w", encoding="utf-8").write(nbsp_fix(html))

        en, missing = to_english(html)
        en = put_ld(en, ld_json(BeautifulSoup(en, "html.parser"), "en", key))
        out = os.path.join(ROOT, dst)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(nbsp_fix(en))
        print(f"✓ {src} -> {dst}")
        for m in missing:
            print(f"  ! evtl. unübersetzt: {m}")


if __name__ == "__main__":
    sys.exit(main())
