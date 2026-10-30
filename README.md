# Mlivo AI – Website (mlivo-ai.at)

Statische Website, gehostet über **GitHub Pages** (Push auf `main` → automatisch live, Workflow `.github/workflows/deploy-pages.yml`). Domain bei World4You, DNS zeigt auf GitHub Pages.

## Aufbau (seit Umbau 29.10.2026)
| Seite | Datei |
|---|---|
| Startseite DE | `index.html` |
| Architekten & Planer DE | `architekten/index.html` |
| Startseite EN | `en/index.html` *(generiert)* |
| Architects EN | `en/architects/index.html` *(generiert)* |
| Datenschutz | `datenschutz/index.html` |
| Gemeinsames Design / Script | `assets/site.css`, `assets/site.js` |

## Texte ändern
1. **Nur die deutschen Seiten bearbeiten.** Jeder Text trägt seine englische Fassung im Attribut `data-en="…"` (bzw. `data-en-html`, `data-en-alt`, `data-en-href` …).
2. Danach `python3 tools/build.py` ausführen – das erzeugt die EN-Seiten und die Google-Strukturdaten (JSON-LD, inkl. FAQ) neu.
3. Committen und pushen.

Bei Änderungen an CSS/JS die Versionsnummer `?v=…` in den `<link>`/`<script>`-Tags erhöhen (Browser-Cache).

Alte Sprungmarken (`/#cad`, `/#vierd`, `/#start` …) werden in `assets/site.js` auf die neuen Ziele umgeleitet.
