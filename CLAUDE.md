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
| verde-giallo | 2 | Ciclabile presente ma inadeguata |
| verde-blu | 1 | Bike friendly ma alto flusso pedonale |

## Stack Tecnico
- **Database**: CSV → target GeoJSON / API REST
- **Schema colonne**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio, data_segnalazione
- **ID formato**: SS-ROM-XXXX (ultimo usato: SS-ROM-0446)
- **Hosting**: GitHub Pages — nikolaifissenko/streetsmart-volt
- **Mappa live**: https://nikolaifissenko.github.io/streetsmart-volt/
- **Form backend**: Formspree endpoint `xlgookeg`
- **PWA**: manifest.json + sw.js (offline caching), installabile su mobile
- **Logo**: `streetsmart_logo.png` (root) — ruota bici con stella 4 colori
- **Icone PWA**: `icons/icon-192.png`, `icons/icon-512.png` — generate da `scripts/generate_icons.py`

## File Master
`data/master/streetsmart_roma_completo.csv` — source of truth.
Non modificare i CSV in data/municipio/ senza aggiornare il master.

## Stato Database
- **446 strade** classificate totali
- Municipio I: ~80 strade (completato)
- Municipio II: ~80 strade (completato + segnalazioni Sentinelle)
- Municipio III: ~50 strade (completato + segnalazioni Sentinelle)
- Municipi IV, V, VII, VIII, IX, XI, XII, XIII, XIV, XV: segnalazioni Sentinelle integrate nel master
- Ultimo ID usato: SS-ROM-0446

## Community Sentinelle
- Form iscrizione: nikolaifissenko.github.io/Streetsmart-Sentille/sentinelle_form.html
- Form segnalazione: nikolaifissenko.github.io/Streetsmart-Sentille/segnalazione_form.html
- Obiettivo: 100 Sentinelle, poi portare il database alle istituzioni

## Social
- Instagram: @streetsmart.nav — tono urban rebel, community building, italiano

## Struttura Directory
```
streetsmart/
├── CLAUDE.md                        # questo file
├── data/
│   ├── master/
│   │   └── streetsmart_roma_completo.csv   # SOURCE OF TRUTH
│   ├── municipio/
│   │   ├── municipio1_final.csv
│   │   ├── municipio2.csv
│   │   └── municipio3.csv
│   └── archive/                     # vecchie versioni, non toccare
│       ├── municipio1_v1.csv
│       ├── municipio1_v2.csv
│       └── municipio1_v3.csv
├── web/
│   ├── sentinelle_form.html
│   └── segnalazione_form.html
├── icons/
│   ├── icon-192.png                 # PWA icon 192x192
│   └── icon-512.png                 # PWA icon 512x512
├── manifest.json                    # PWA manifest
├── sw.js                            # Service worker (offline cache)
├── streetsmart_logo.png             # Logo ufficiale
├── docs/
│   └── pdf/                         # materiali presentazione
└── scripts/
    ├── build.py                     # export GeoJSON
    └── generate_icons.py            # genera icone PWA da logo.png
```

## Mappa Web Interattiva
- **File principale**: `index.html` (root) — mappa Leaflet.js con CartoDB Positron Light tiles
- **GeoJSON**: `streetsmart_roma.geojson` (root) — generato da `scripts/build.py`
- **Brand**: palette travertino (#EDE8DF background), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **Copertura**: 357 LineString reali (Overpass) + 62 Point fallback (Nominatim) + 27 non trovate
- **Cache geocode**: `data/master/.geocode_cache.json` (chiavi `v3|nome_clean`)
- **Build**: `python scripts/build.py` — batch Overpass + Nominatim fallback → GeoJSON
- **Filtri mappa**: 5 classi (nero, rosso, giallo, blu, verde); verde-giallo e verde-blu mappati a verde
- **Mobile**: pannello bottom-sheet con tab Filtri (chip + legenda) e Strade (lista scrollabile con zoom-to-street) (≤700px)
- **PWA**: installabile, offline-first (cache HTML, GeoJSON, Leaflet, font)

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0446
3. Aggiornare anche il CSV del municipio corrispondente in `data/municipio/`
4. Eseguire `python scripts/build.py` per rigenerare il GeoJSON
5. Committare e pushare su main per deploy GitHub Pages
