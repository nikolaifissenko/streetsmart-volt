# StreetSmart — Contesto Progetto

## Cos'è
Database B2B delle strade di Roma classificate per pericolosità ciclistica.
Prodotto: layer di pericolosità (un colore per strada) vendibile con licenza commerciale a app di navigazione, operatori micromobilità (Lime, Dott, Tier), Comuni.
Sviluppato da Nikolai.

## Classificazione
| Colore | Score | Significato |
|--------|-------|-------------|
| nero | 5 | Multicarreggiata ad alta velocità |
| rosso | 4 | Arteria trafficata senza ciclabile |
| giallo | 3 | Strada urbana senza ciclabile |
| blu | 2 | ZTL / pedonale |
| verde | 1 | Pista ciclabile presente |

Regola: arterie note e strade con 3+ corsie senza ciclabile → rosso, non giallo.

## Database
- **15.789 strade** (574 manuali + 15.215 da OSM), **15.090 con geometria**
- **Source of truth**: `data/master/streetsmart_roma_completo.csv`
- **Schema**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio, data_segnalazione
- **ID formato**: SS-ROM-XXXX (ultimo: SS-ROM-15789)
- **Build GeoJSON**: `python scripts/build_fast.py`
- **Import OSM**: `python scripts/import_osm_bulk.py`
- **Parse segnalazioni**: `python scripts/parse_segnalazioni.py`

## PWA
- **URL**: https://nikolaifissenko.github.io/streetsmart-volt/
- **File**: `index.html` — 3 tab (Mappa, Segnala, Sentinelle) + bottone "Per aziende" nell'header
- **Mappa**: Leaflet.js, strade colorate, filtri, ricerca 15k strade, sidebar, geolocalizzazione
- **Selettore città**: dropdown "Roma ▾" sotto il logo (`CITIES` in index.html). Cambia
  città = ricarica tile/stats/sidebar da zero; nasconde "Per municipio" e disabilita
  Segnala/Sentinelle per città senza quelle feature (vedi sezione Altre città)
- **Brand**: palette travertino (#EDE8DF), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **PWA**: manifest.json + sw.js (cache `streetsmart-v16`, bump ad ogni cambio
  significativo di struttura file, altrimenti utenti che tornano sul sito
  vedono asset/tile vecchi), dark mode automatico
- **Caricamento tile**: ogni tile fetcha con retry (3 tentativi). Se un tile fallisce
  dopo i retry la mappa carica comunque il resto e mostra un toast — non un errore
  bloccante (regressione reale introdotta dal passaggio a tile paralleli, poi corretta)

## Monetizzazione
- **Landing B2B**: `api.html` — posizionamento: "Il layer di pericolosità ciclistica per la tua app"
- **Pricing**: Mappa gratuita (uso personale) / Licenza commerciale €199/mese / Multi-città custom
- **Lead capture**: form Formspree (endpoint `xlgookeg`) su api.html → redirect `grazie.html`
- **Form segnalazioni**: Formspree endpoint `mrernnwd`
- **Instagram**: @streetsmart.nav (533 follower)
- **API commerciale**: `worker/` (Cloudflare Worker), doc in `API.md`. Fa da
  gateway con API key sopra gli stessi tile pubblici — nessun database
  proprio, quindi i dati restano sempre sincronizzati con la mappa. Chiavi
  gestite a mano via `wrangler secret put API_KEYS`.

## Altre città
- **Stato**: Roma è in produzione con dati curati (PWA + API commerciale). Napoli è
  collegata alla PWA tramite il selettore città, ma è **solo classificazione
  automatica OSM, senza revisione manuale/testimonianze** — qualità inferiore
  a Roma finché non c'è un giro di revisione umano. L'API commerciale (`worker/`)
  serve solo i tile di Roma, non ancora estesa alle altre città.
- **Build**: `python scripts/build_city.py "<NomeCitta>" <PREFISSO>` (es. `"Napoli" NAP`)
  — fetcha OSM in bulk e classifica automaticamente con le stesse regole di Roma.
- **Output**: `cities/<slug>/streetsmart_<slug>.csv` + `cities/<slug>/tiles/zona-*.geojson`
  (raggruppate per griglia geografica generata dinamicamente, non per municipio
  reale — non esiste una mappatura amministrativa per città non-Roma).
- **Aggiungere una città al selettore PWA**: dopo aver girato `build_city.py`,
  aggiungere una entry a `CITIES` in `index.html` (tilesBase, tilePrefix,
  zoneLabel, hasZoneStats: false, communityFeatures: false) e un `<option>`
  nel `#city-select`.
- **Anteprima standalone**: `cities/<slug>/preview.html`, pagina Leaflet
  indipendente, utile per guardare i dati prima di collegarli alla PWA.

## Regole GeoJSON
- Solo LineString/MultiLineString — niente Point, niente strade senza geometria
- Niente file unico col database intero servito in una richiesta sola (era scaricabile
  con un solo URL). La PWA fetcha `tiles/index.json` (elenco slug municipio) poi i
  tile `tiles/municipio-<slug>.geojson` in parallelo. `scripts/tiles.py` genera i
  tile da `dist/streetsmart_roma.geojson` (non pubblicato, gitignored) — chiamato
  automaticamente da `build_fast.py`/`build.py` a fine build.

## Struttura File
```
index.html              — PWA principale
api.html                — Landing B2B con form lead capture
grazie.html             — Thank-you page post-lead
404.html                — Redirect PWA
manifest.json / sw.js   — PWA
tiles/index.json        — elenco slug municipio
tiles/municipio-*.geojson — GeoJSON per municipio, servito dalla PWA
data/master/            — CSV source of truth + cache
scripts/build_fast.py   — Build GeoJSON (batch, principale)
scripts/tiles.py        — Divide il GeoJSON in tile per municipio
scripts/build_city.py   — Build automatico OSM per altre città (vedi Altre città)
scripts/import_osm_bulk.py — Import strade da OSM
scripts/parse_segnalazioni.py — Parse segnalazioni
cities/<slug>/           — Dataset altre città (es. cities/napoli/), vedi Altre città
worker/                 — API commerciale (Cloudflare Worker), vedi API.md
API.md                  — Doc dell'API commerciale
```
