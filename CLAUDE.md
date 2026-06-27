# StreetSmart — Contesto Progetto per Claude Code

## Cos'è
Database B2B delle strade di Roma classificate per pericolosità ciclistica.
Vendibile a operatori di micromobilità (Lime, Dott, Tier), Comuni, app di navigazione.
Sviluppato da Nikolai.

## Sistema di Classificazione
| Colore | Score | Significato |
|--------|-------|-------------|
| nero | 5 | Multicarreggiata ad alta velocità, pericolosissimo |
| rosso | 4 | Strada trafficata senza ciclabile |
| giallo | 3 | Strada urbana tranquilla senza ciclabile |
| verde | 1 | Pista ciclabile presente |
| blu | 2 | ZTL / pedonale / alto flusso pedoni |

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
- Ultimo ID usato: SS-ROM-15789
- Import bulk: `python scripts/import_osm_bulk.py`
- Build veloce: `python scripts/build_fast.py` (batch da 40, ~40 min per rebuild completo)

## PWA
- **File principale**: `index.html` (root) — PWA con 3 tab: Mappa, Segnala, Sentinelle
- **Tab Mappa**: Leaflet.js con strade colorate per classificazione, filtri, sidebar con lista strade, popup con dettagli e bottoni "Segnala" e "Condividi"
- **Tab Segnala**: mappa pulita (senza strade colorate), click per piazzare pin rosso, reverse geocoding Nominatim per auto-compilare strada/quartiere, form con 5 colori (nero, rosso, giallo, verde, blu). Coordinate lat/lng inviate col form. Dopo invio: bottone "Segnala un'altra strada" per reset immediato
- **Tab Sentinelle**: form iscrizione comunità (obiettivo 100 sentinelle)
- **Navigazione**: top tab nav con aria-labels, deep linking via hash (#mappa, #segnala, #sentinelle)
- **PWA installabile**: manifest.json + sw.js (cache `streetsmart-v15`)
- **Dark mode**: automatico via prefers-color-scheme, mappa CARTO dark, UI completa
- **Ricerca**: barra di ricerca strade su desktop (sidebar) e mobile (toolbar) con contatore risultati
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
- **GeoJSON**: `streetsmart_roma.geojson` — 15.090 strade con geometria
- **Build**: `python scripts/build_fast.py` — batch Overpass → GeoJSON (con cache incrementale)
- **Pagina B2B**: `api.html` — landing page per API/database con pricing (Explorer/Business/Enterprise)

## Regole GeoJSON
- **Solo LineString/MultiLineString** nel GeoJSON — niente Point, niente strade senza geometria
- Se Overpass non trova la geometria, la strada non va nel GeoJSON

## Social
- Instagram: @streetsmart.nav

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0574
3. Eseguire `python scripts/build.py` per rigenerare il GeoJSON
4. Rimuovere Point e strade senza geometria dal GeoJSON
5. Committare e pushare su main per deploy GitHub Pages
