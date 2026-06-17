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
- **PWA live**: https://nikolaifissenko.github.io/streetsmart-volt/
- **Form backend**: Formspree endpoint `xlgookeg` (sentinelle), `mrernnwd` (segnalazioni)
- **PWA**: manifest.json + sw.js — installabile su home screen, caching offline

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
- Form iscrizione: https://nikolaifissenko.github.io/streetsmart-volt/#sentinelle
- Form segnalazione: https://nikolaifissenko.github.io/streetsmart-volt/#segnala
- Vecchi form standalone ancora in `web/sentinelle_form.html` e `web/segnalazione_form.html` (legacy)
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
├── manifest.json                    # PWA manifest
├── sw.js                            # service worker (cache v7)
├── icon-192.png                     # icona PWA 192x192
├── icon-512.png                     # icona PWA 512x512
├── streetsmart_roma.geojson         # GeoJSON generato da build.py
├── web/
│   ├── sentinelle_form.html         # legacy (ora in index.html #sentinelle)
│   └── segnalazione_form.html       # legacy (ora in index.html #segnala)
├── docs/
│   └── pdf/                         # materiali presentazione
└── scripts/
    ├── build.py                     # genera GeoJSON da CSV master
    └── gen_icons.py                 # genera icone PNG con Pillow
```

## PWA Unificata
- **File principale**: `index.html` (root) — PWA con 3 view: Mappa, Segnala, Sentinelle
- **Navigazione**: top tab nav con 3 tab (Mappa, Segnala, Sentinelle), deep linking via hash (#mappa, #segnala, #sentinelle)
- **manifest.json**: configurazione PWA (installabile su home screen) con icone PNG 192x192 e 512x512
- **sw.js**: service worker network-first con caching offline (cache attuale: `streetsmart-v7`)
- **Mappa principale**: Leaflet.js con CartoDB Positron Light tiles, `tap: false` per compatibilità mobile
- **Mappa segnala**: seconda mappa Leaflet nella tab Segnala — click su strada compila form automaticamente, geolocalizzazione automatica, lazy-init quando si apre la tab
- **Popup mappa**: ogni strada ha bottone "Segnala questa strada" che compila form e switcha tab
- **Geolocalizzazione**: bottone sulla mappa principale + auto-geolocalizzazione nella mappa segnala
- **GeoJSON**: `streetsmart_roma.geojson` (root) — generato da `scripts/build.py`
- **Icone**: `icon-192.png` e `icon-512.png` generati da `scripts/gen_icons.py` (Pillow)
- **Brand**: palette travertino (#EDE8DF background), font EB Garamond + Inter
- **Colori mappa**: nero=#1a1a1a, rosso=#e53935, giallo=#e6940a, blu=#1976D2, verde=#27AE60
- **Copertura**: 357 LineString reali (Overpass) + 62 Point fallback (Nominatim) + 27 non trovate
- **Cache geocode**: `data/master/.geocode_cache.json` (chiavi `v3|nome_clean`)
- **Build**: `python scripts/build.py` — batch Overpass + Nominatim fallback → GeoJSON
- **Filtri mappa**: 5 classi (nero, rosso, giallo, blu, verde); verde-giallo e verde-blu mappati a verde

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0446
3. Aggiornare anche il CSV del municipio corrispondente in `data/municipio/`
4. Eseguire `python scripts/build.py` per rigenerare il GeoJSON
5. Committare e pushare su main per deploy GitHub Pages
