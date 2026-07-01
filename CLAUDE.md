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
- **15.790 strade** (575 manuali + 15.215 da OSM), **15.091 con geometria**
- **Source of truth**: `data/master/streetsmart_roma_completo.csv`
- **Schema**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio, data_segnalazione
- **ID formato**: SS-ROM-XXXX (ultimo: SS-ROM-15790)
- **Build GeoJSON**: `python scripts/build_fast.py`
- **Import OSM**: `python scripts/import_osm_bulk.py`
- **Parse segnalazioni**: `python scripts/parse_segnalazioni.py`

## PWA
- **URL**: https://nikolaifissenko.github.io/streetsmart-volt/
- **File**: `index.html` — 3 tab (Mappa, Segnala, Sentinelle) + bottone "Per aziende" nell'header
- **Mappa**: Leaflet.js, strade colorate, filtri, ricerca 15k strade, sidebar, geolocalizzazione
- **Brand**: palette travertino (#EDE8DF), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **PWA**: manifest.json + sw.js (cache `streetsmart-v15`), dark mode automatico

## Monetizzazione
- **Landing B2B**: `api.html` — posizionamento: "Il layer di pericolosità ciclistica per la tua app"
- **Pricing**: Mappa gratuita (uso personale) / Licenza commerciale €199/mese / Multi-città custom
- **Lead capture**: form Formspree (endpoint `xlgookeg`) su api.html → redirect `grazie.html`
- **Form segnalazioni**: Formspree endpoint `mrernnwd`
- **Instagram**: @streetsmart.nav (533 follower)

## Regole GeoJSON
- Solo LineString/MultiLineString — niente Point, niente strade senza geometria

## Struttura File
```
index.html              — PWA principale
api.html                — Landing B2B con form lead capture
grazie.html             — Thank-you page post-lead
404.html                — Redirect PWA
manifest.json / sw.js   — PWA
streetsmart_roma.geojson — GeoJSON servito dalla PWA
data/master/            — CSV source of truth + cache
scripts/build_fast.py   — Build GeoJSON (batch, principale)
scripts/import_osm_bulk.py — Import strade da OSM
scripts/parse_segnalazioni.py — Parse segnalazioni
```
