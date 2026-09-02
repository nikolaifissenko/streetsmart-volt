# StreetSmart — Contesto Progetto

## Cos'è
Database B2B delle strade di Roma classificate per pericolosità ciclistica.
Prodotto: layer di pericolosità (un colore per strada) vendibile con licenza commerciale a app di navigazione, operatori micromobilità (Lime, Dott, Tier), Comuni.
Sviluppato da Nikolai.

## Workflow di deploy
Nikolai vuole che tutto il lavoro verificato vada **sempre live sulla PWA**,
non lasciato in un branch/PR in attesa. Quindi: dopo aver completato e
verificato una modifica (dati o codice), pusha direttamente su `main`
(fast-forward se possibile) invece di fermarti su un branch separato — a
meno che l'utente non chieda esplicitamente una PR per fare review prima.
Questo vale anche quando le istruzioni di sessione indicano un branch di
sviluppo dedicato: quel branch è il punto di partenza per il lavoro, ma il
merge su `main` a fine task è la norma per questo repo, non un'eccezione
da richiedere ogni volta.

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
- **15.791 strade** (576 manuali + 15.215 da OSM), **15.091 con geometria**
- **Source of truth**: `data/master/streetsmart_roma_completo.csv`
- **Schema**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio, data_segnalazione
- **ID formato**: SS-ROM-XXXX (ultimo: SS-ROM-15791)
- **Build GeoJSON**: `python scripts/build_fast.py`
- **Import OSM**: `python scripts/import_osm_bulk.py`
- **Parse segnalazioni (vie nuove)**: `python scripts/parse_segnalazioni.py` — aggiunge
  solo vie assenti dal dataset, non tocca quelle già presenti
- **Riconcilia segnalazioni (vie esistenti)**: script una-tantum tipo
  `scripts/reconcile_segnalazioni_luglio.py` — a differenza di `parse_segnalazioni.py`,
  aggiorna classificazione/score/note/n_testimonianze/municipio delle vie già presenti
  quando le segnalazioni reali (raggruppate per via, maggioranza vince) divergono dal
  dato corrente; poi rigenerare con `build_fast.py`. Se ne scrive uno nuovo ad ogni
  lotto di segnalazioni da riconciliare (nome file = periodo coperto)

## PWA
- **URL**: https://nikolaifissenko.github.io/streetsmart-volt/
- **File**: `index.html` — 3 tab (Mappa, Segnala, Sentinelle) + bottone "Per aziende" nell'header
- **Onboarding Sentinelle**: le iscrizioni arrivano via form Formspree (endpoint `xlgookeg`,
  `form_type=sentinella`) — nessuna integrazione Instagram automatica, quindi ogni nuova
  Sentinella va contattata a mano su @streetsmart.nav con un DM di benvenuto che spiega
  come installare la PWA (Android: bottone "Installa"; iPhone: Condividi → Aggiungi a Home)
  e come segnalare strade dalla tab Segnala. Il contatore "Sentinelle attive" in pagina
  (`index.html`, sezione Sentinelle) è un numero scritto a mano, va aggiornato manualmente
  a ogni iscrizione confermata
- **Mappa**: Leaflet.js, strade colorate, filtri, ricerca 15k strade, sidebar, geolocalizzazione
- **Geolocalizzazione automatica**: alla prima apertura, dopo che le strade sono caricate,
  la mappa tenta la geolocalizzazione in silenzio (nessun toast se negata/non disponibile)
  e centra la vista sulla posizione dell'utente invece di lasciarla sull'inquadratura
  dell'intera città. Applicata con ~350ms di ritardo rispetto al fix GPS: il `fitBounds()`
  sul dataset appena caricato può avere ancora un'animazione di pan/zoom in corso quando
  arriva la posizione (spesso quasi istantanea), e il suo step di completamento
  sovrascrive silenziosamente una vista impostata troppo presto
- **Localizzazione IT/EN**: rileva `navigator.language` e mostra tutta l'interfaccia
  (Mappa, Segnala, Sentinelle) in inglese se il browser/dispositivo è in inglese,
  altrimenti in italiano — solo l'etichetta visiva cambia, i valori di classificazione
  nel database e le note curate delle strade restano sempre in italiano. Meccanismo:
  dizionario `I18N` + attributi `data-i18n`/`data-i18n-html`/`data-i18n-placeholder`/
  `data-i18n-title`/`data-i18n-aria-label` in `index.html`, applicati da `applyStaticI18n()`
  al caricamento; le stringhe generate via JS (popup, toast, contatori) chiamano `t(key)`
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
  collegata alla PWA tramite il selettore città ed è **prevalentemente classificazione
  automatica OSM** — qualità inferiore a Roma finché non c'è un giro di revisione
  manuale più ampio. Da luglio 2026 esiste però un primo layer di segnalazioni reali
  anche per Napoli (vedi sotto), stesso meccanismo di Roma: l'obiettivo dichiarato è
  portare Napoli allo stesso livello di dati "vivi" di Roma. L'API commerciale
  (`worker/`) serve solo i tile di Roma, non ancora estesa alle altre città.
- **Build**: `python scripts/build_city.py "<NomeCitta>" <PREFISSO>` (es. `"Napoli" NAP`)
  — fetcha OSM in bulk e classifica automaticamente con le stesse regole di Roma.
  Rilanciarlo rigenera tutto da zero (nuovo fetch OSM, ID rinumerati) — se nel
  frattempo sono state riconciliate segnalazioni reali, vanno riapplicate dopo.
- **Output**: `cities/<slug>/streetsmart_<slug>.csv` + `cities/<slug>/tiles/zona-*.geojson`
  (raggruppate per griglia geografica generata dinamicamente, non per municipio
  reale — non esiste una mappatura amministrativa per città non-Roma).
- **Segnalazioni reali per città non-Roma**: `cities/<slug>/segnalazioni_<slug>.csv`
  (log grezzo) + `scripts/reconcile_segnalazioni_<slug>.py` — stesso meccanismo di
  riconciliazione di Roma, ma patcha anche i tile già generati senza rifare il fetch
  OSM completo. Nota: il form Formspree di Segnala è raggiungibile anche da città
  diverse da Roma pur con `communityFeatures: false` in `index.html` (che disabilita
  solo l'accesso dalla UI PWA) — prima segnalazione reale ricevuta così: Via Medina,
  Napoli, luglio 2026.
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
scripts/parse_segnalazioni.py — Parse segnalazioni (vie nuove)
scripts/reconcile_segnalazioni_*.py — Riconcilia segnalazioni su vie esistenti (Roma e altre città)
cities/<slug>/           — Dataset altre città (es. cities/napoli/), vedi Altre città
cities/<slug>/segnalazioni_<slug>.csv — Log segnalazioni reali per città non-Roma
worker/                 — API commerciale (Cloudflare Worker), vedi API.md
API.md                  — Doc dell'API commerciale
```
