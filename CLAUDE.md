# StreetSmart — Contesto Progetto per Claude Code

## Cos'è
Database B2B delle strade di Roma classificate per pericolosità ciclistica.
Vendibile a operatori di micromobilità (Lime, Dott, Tier), Comuni, app di navigazione.
Sviluppato da Nikolai.

## Sistema di Classificazione
| Colore | Score | Significato |
|--------|-------|-------------|
| nero | 5 | Multicarreggiata ad alta velocità, pericolosissimo |
| rosso | 4 | Arteria trafficata / multicorsia senza ciclabile |
| giallo | 3 | Strada urbana tranquilla senza ciclabile |
| verde | 1 | Pista ciclabile presente |
| blu | 2 | ZTL / pedonale / alto flusso pedoni |

Regola automatica: arterie note e strade con 3+ corsie senza ciclabile vanno classificate rosso, non giallo.

## Stack Tecnico
- **Database**: CSV → GeoJSON
- **Schema colonne**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio, data_segnalazione
- **ID formato**: SS-ROM-XXXX (ultimo usato: SS-ROM-15789)
- **Hosting**: GitHub Pages — nikolaifissenko/streetsmart-volt
- **PWA live**: https://nikolaifissenko.github.io/streetsmart-volt/
- **Form backend**: Formspree endpoint `xlgookeg` (sentinelle), `mrernnwd` (segnalazioni)
- **404.html**: redirect automatico alla PWA (fix per link da Instagram)

## File Master
`data/master/streetsmart_roma_completo.csv` — source of truth.

## Stato Database
- **15.789 strade** nel CSV (574 manuali + 15.215 importate da OSM)
- **15.090 strade** con geometria nel GeoJSON
- Ultimo ID usato: SS-ROM-15789
- Import bulk: `python scripts/import_osm_bulk.py`
- Build GeoJSON: `python scripts/build_fast.py` (batch Overpass da 40, cache incrementale)
- Parse segnalazioni: `python scripts/parse_segnalazioni.py`

## PWA
- **File principale**: `index.html` (root) — PWA con 3 tab: Mappa, Segnala, Sentinelle
- **Tab Mappa**: Leaflet.js con strade colorate per classificazione, filtri, sidebar con lista strade, popup con dettagli e bottoni "Segnala" e "Condividi"
- **Tab Segnala**: mappa pulita (senza strade colorate), click per piazzare pin rosso, reverse geocoding Nominatim per auto-compilare strada/quartiere, form con 5 colori. Dopo invio: bottone "Segnala un'altra strada" per reset immediato (pin, coordinate, campi, hint)
- **Tab Sentinelle**: form iscrizione comunità (obiettivo 100 sentinelle)
- **Navigazione**: top tab nav con aria-labels, deep linking via hash (#mappa, #segnala, #sentinelle)
- **PWA installabile**: manifest.json + sw.js (cache `streetsmart-v15`)
- **Dark mode**: automatico via prefers-color-scheme, mappa CARTO dark, UI completa
- **Ricerca**: cerca su tutte le 15k strade (filtra dataset e ricostruisce lista), barra su desktop (sidebar) e mobile (toolbar)
- **Linee mappa**: spessore scala col zoom (0.8px → 3px), opacità 75% per non coprire i nomi delle vie
- **Filtri mobile**: toggle per aprire sidebar a schermo intero con filtri e lista
- **Ordinamento**: lista strade ordinabile A-Z, pericolose prima, sicure prima
- **Statistiche municipio**: barre colorate per municipio nella sidebar
- **Strade vicine**: dopo geolocalizzazione, alert con conteggio pericolose/sicure nel raggio 1 km
- **Condivisione**: Web Share API su mobile, clipboard su desktop
- **Toast**: notifiche animate al posto di alert()
- **Loader**: spinner animato durante caricamento GeoJSON
- **Open Graph**: meta tag OG e Twitter Card per condivisione social
- **Brand**: palette travertino (#EDE8DF), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **GeoJSON**: `streetsmart_roma.geojson` (root, servito da GitHub Pages)
- **Pagina B2B**: `api.html` — landing page per API/database con pricing (Explorer/Business/Enterprise)

## Regole GeoJSON
- **Solo LineString/MultiLineString** nel GeoJSON — niente Point, niente strade senza geometria
- Se Overpass non trova la geometria, la strada non va nel GeoJSON

## Social
- Instagram: @streetsmart.nav

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-15789
3. Eseguire `python scripts/build_fast.py` per rigenerare il GeoJSON
4. Committare e pushare su main per deploy GitHub Pages

## Struttura File
```
index.html              — PWA principale
api.html                — Landing page B2B
404.html                — Redirect PWA
manifest.json           — PWA manifest
sw.js                   — Service worker
streetsmart_roma.geojson — GeoJSON servito dalla PWA
data/master/            — CSV source of truth + cache geocoding
dist/                   — Copia GeoJSON per distribuzione
scripts/build.py        — Build GeoJSON (singolo)
scripts/build_fast.py   — Build GeoJSON (batch, principale)
scripts/import_osm_bulk.py — Import strade da OSM
scripts/parse_segnalazioni.py — Parse segnalazioni Formspree
```
