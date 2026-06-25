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
- **ID formato**: SS-ROM-XXXX (ultimo usato: SS-ROM-0609)
- **Hosting**: GitHub Pages — nikolaifissenko/streetsmart-volt
- **PWA live**: https://nikolaifissenko.github.io/streetsmart-volt/
- **Form backend**: Formspree endpoint `xlgookeg` (sentinelle), `mrernnwd` (segnalazioni)
- **404.html**: redirect automatico alla PWA (fix per link da Instagram)

## File Master
`data/master/streetsmart_roma_completo.csv` — source of truth.

## Stato Database
- **609 strade** nel CSV
- Ultimo ID usato: SS-ROM-0609

## PWA
- **File principale**: `index.html` (root) — PWA con 3 tab: Mappa, Segnala, Sentinelle
- **Tab Mappa**: Leaflet.js con strade colorate per classificazione, filtri, sidebar con lista strade, popup con dettagli e bottone "Segnala questa strada"
- **Tab Segnala**: mappa pulita (senza strade colorate), click per piazzare pin rosso, reverse geocoding Nominatim per auto-compilare strada/quartiere, form con 5 colori (nero, rosso, giallo, verde, blu). Dopo invio: bottone "Segnala un'altra strada" per reset immediato
- **Tab Sentinelle**: form iscrizione comunità (obiettivo 100 sentinelle)
- **Navigazione**: top tab nav, deep linking via hash (#mappa, #segnala, #sentinelle)
- **PWA installabile**: manifest.json + sw.js (cache `streetsmart-v12`)
- **Brand**: palette travertino (#EDE8DF), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **GeoJSON**: `streetsmart_roma.geojson` — generato da `scripts/build.py`
- **Build**: `python scripts/build.py` — batch Overpass → GeoJSON

## Regole GeoJSON
- **Solo LineString/MultiLineString** nel GeoJSON — niente Point, niente strade senza geometria
- Se Overpass non trova la geometria, la strada non va nel GeoJSON

## Social
- Instagram: @streetsmart.nav

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0609
3. Eseguire `python scripts/build.py` per rigenerare il GeoJSON
4. Rimuovere Point e strade senza geometria dal GeoJSON
5. Committare e pushare su main per deploy GitHub Pages
