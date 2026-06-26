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
- **ID formato**: SS-ROM-XXXX (ultimo usato: SS-ROM-0574)
- **Hosting**: GitHub Pages — nikolaifissenko/streetsmart-volt
- **PWA live**: https://nikolaifissenko.github.io/streetsmart-volt/
- **Form backend**: Formspree endpoint `xlgookeg` (sentinelle), `mrernnwd` (segnalazioni)
- **404.html**: redirect automatico alla PWA (fix per link da Instagram)

## File Master
`data/master/streetsmart_roma_completo.csv` — source of truth.

## Stato Database
- **574 strade** nel CSV, **549 con geometria LineString** sulla mappa
- Ultimo ID usato: SS-ROM-0574

## PWA
- **File principale**: `index.html` (root) — PWA con 3 tab: Mappa, Segnala, Sentinelle
- **Tab Mappa**: Leaflet.js con strade colorate per classificazione, filtri, sidebar con lista strade, popup con dettagli e bottone "Segnala questa strada"
- **Tab Segnala**: mappa pulita (senza strade colorate), click per piazzare pin rosso, reverse geocoding Nominatim per auto-compilare strada/quartiere, form con 5 colori (nero, rosso, giallo, verde, blu). Dopo invio: bottone "Segnala un'altra strada" per reset immediato
- **Tab Sentinelle**: form iscrizione con perks (nome nel DB, classifica, impatto), leaderboard top 5, barra obiettivo community 574/1.000, campo quartiere + impegno mensile, CTA post-iscrizione diretta a tab Segnala
- **Navigazione**: top tab nav, deep linking via hash (#mappa, #segnala, #sentinelle)
- **PWA installabile**: manifest.json + sw.js (cache `streetsmart-v12`)
- **Brand**: palette travertino (#EDE8DF), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **GeoJSON**: `streetsmart_roma.geojson` — generato da `scripts/build.py`
- **Build**: `python scripts/build.py` — batch Overpass → GeoJSON

## Regole GeoJSON
- **Solo LineString/MultiLineString** nel GeoJSON — niente Point, niente strade senza geometria
- Se Overpass non trova la geometria, la strada non va nel GeoJSON

## API
- **Cloudflare Worker**: `api/` — API REST per monetizzazione B2B
  - `GET /v1/score?lat=X&lon=Y` — danger score strada più vicina
  - `GET /v1/route?from=lat,lon&to=lat,lon` — score medio percorso
  - `GET /v1/route` — statistiche database
- **Build dati API**: `node api/scripts/build-streets.js` — rigenera `api/src/streets-data.js` dal GeoJSON
- **Deploy**: `cd api && npx wrangler login && npx wrangler deploy` (Cloudflare Workers, gratis 100k req/giorno)
- **Landing page B2B**: `api.html` — pagina commerciale con docs, use cases, CTA mailto
- **API Playground**: `api-playground.html` — demo interattiva client-side (funziona su GitHub Pages senza server)

## Social
- Instagram: @streetsmart.nav

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0574
3. Eseguire `python scripts/build.py` per rigenerare il GeoJSON
4. Rimuovere Point e strade senza geometria dal GeoJSON
5. Committare e pushare su main per deploy GitHub Pages
6. Eseguire `node api/scripts/build-streets.js` per aggiornare i dati API

## Prossimi Passi
- Deploy API su Cloudflare Workers (da terminale personale)
- Merge branch `claude/clever-sagan-s7vdju` su main per pubblicare landing + playground
- Contattare country manager Lime/Dott/Tier su LinkedIn con link api.html
- Push Instagram per reclutamento sentinelle (leaderboard come hook)
- Scalare DB: obiettivo 1.000 strade tramite sentinelle
