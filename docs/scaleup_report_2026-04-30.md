# StreetSmart — Rapporto Scale-Up
**Data:** 30 aprile 2026
**Stato database:** 202 strade — Municipi I, II, III completi + spot su IX, XI, XII

---

## 1. Stato attuale del database

### Schema CSV (11 colonne)
```
id, nome, quartiere, classificazione, score, note,
ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio
```

### Distribuzione classificazioni (stima)
| Classificazione | Score | % database |
|---|---|---|
| giallo | 3 | ~45% |
| rosso | 4 | ~30% |
| verde | 1 | ~12% |
| nero | 5 | ~8% |
| blu / verde-giallo / verde-blu | 1–2 | ~5% |

### Copertura per municipio
| Municipio | Strade | Stato |
|---|---|---|
| I — Centro Storico | ~82 | Completo |
| II — Parioli / Flaminio | ~57 | Completo |
| III — Montesacro | ~47 | Completo |
| IX, XI, XII | ~16 | Spot (Sentinelle) |
| IV–VIII, X, XIII–XV | 0 | Non iniziati |

---

## 2. Problemi strutturali identificati

### Database
- **Nessuna coordinata geografica** — senza lat/lon il CSV è un elenco nomi, non mappabile né vendibile
- **`n_testimonianze` quasi sempre = 1** — validazione comunitaria virtualmente assente
- **Note libere non strutturate** — "4 corsie veloci" non è interrogabile via query
- **Nessun timestamp né campo `fonte`** — impossibile sapere quando e da chi è stata classificata una strada
- **Score e classificazione disallineati** — verde-giallo=2, verde-blu=1, ma la tabella di riferimento è ambigua
- **Nessun OSM way_id** — senza collegamento a OpenStreetMap, aggiungere geometria richiede geocodifica manuale
- **Duplicazione master + municipio CSV** — sync manuale, errori garantiti nel tempo

### Form web (segnalazione + sentinelle)
- **Stesso endpoint Formspree per entrambi i form** — segnalazioni e iscrizioni arrivano mescolate nella stessa inbox
- **Contatore Sentinelle hardcodato** — `<span>3</span>` nell'HTML, non si aggiorna mai automaticamente
- **Formspree come unico backend** — ogni segnalazione arriva via email, integrazione nel CSV è manuale al 100%
- **Mancano 2 classificazioni** — `verde-giallo` e `verde-blu` non sono selezionabili nel form segnalazione
- **Nessun campo coordinate** — la posizione di una segnalazione dipende dal testo libero
- **Nessun collegamento a strade esistenti** — impossibile aggiungere una testimonianza a SS-ROM-XXXX
- **Nessuna foto** — zero proof della classificazione inviata

---

## 3. Quando lasciare il CSV

La soglia non è il numero di righe ma le operazioni sul dato.

| Operazione | Limite del CSV | Stato attuale |
|---|---|---|
| Inserimento righe | ~1.000 | OK (202 righe) |
| Sync multi-file | 1 file | **Già oltre** |
| Query e filtri | ~200 righe | **Già oltre** |
| Produzione GeoJSON | 0 righe | **Già oltre** |
| Validazione schema | 0 righe | **Già oltre** |
| Condivisione B2B | 0 righe | **Già oltre** |

**Conclusione:** il CSV rimane interfaccia di inserimento umano. Il codice si aggiunge come strato di trasformazione, non lo sostituisce.

---

## 4. Roadmap di migrazione

### Fase 0 — Fix immediati (2–4 ore)
*Nessuna modifica architetturale. Riduzione del debito attuale.*

- [ ] Creare secondo endpoint Formspree separato per iscrizioni Sentinelle
- [ ] Aggiungere `verde-giallo` e `verde-blu` ai bottoni classificazione del form
- [ ] Aggiungere campo `indirizzo_completo` o link Google Maps per catturare posizione
- [ ] Aggiungere campo hidden `form_type` a entrambi i form per distinguere le email

---

### Fase 1 — Script di build locale (3–5 ore)
*Il CSV rimane la sorgente. Il codice fa il lavoro sporco.*

Script `scripts/build.py`:
1. Legge `data/master/streetsmart_roma_completo.csv`
2. Valida ogni riga (score coerente, ID formato corretto, campi obbligatori)
3. Per ogni strada senza coordinate → query Nominatim/OSM → aggiunge `lat`, `lon`, `osm_way_id`
4. Produce `dist/streetsmart_roma.geojson`
5. Stampa report: N strade, distribuzione classificazioni, N senza coordinate

Esecuzione: `python scripts/build.py` dopo ogni aggiornamento del CSV.

**Output chiave:** primo GeoJSON reale, consegnabile per demo B2B.

---

### Fase 2 — Backend minimo (1–2 settimane)
*Sostituisce Formspree con un database reale.*

**Stack:** Supabase (PostgreSQL hosted + API REST auto-generata, free tier).

Schema tabelle:
```sql
strade          -- schema CSV + colonna geom (PostGIS)
segnalazioni    -- id, strada_nome, quartiere, municipio, classificazione,
                -- note, instagram, lat, lon, foto_url,
                -- stato ENUM(pending/approved/rejected), created_at
sentinelle      -- id, nome, instagram, citta, tipo, n_validazioni, created_at
testimonianze   -- id, strada_id FK, sentinella_id FK, classificazione,
                -- note, created_at
```

I form HTML puntano alle API Supabase invece di Formspree.
Il contatore Sentinelle diventa `SELECT COUNT(*) FROM sentinelle` — dinamico.

**Output chiave:** segnalazioni in database reale, zero email da processare manualmente.

---

### Fase 3 — Admin panel leggero (3–5 giorni)
*Sostituisce il flusso "email → CSV a mano".*

Pagina HTML protetta da password (o Supabase Studio):
- Lista segnalazioni `pending`
- Approva con un click → strada entra nel DB con coordinate
- Rifiuta con nota
- Export GeoJSON aggiornato

Nessun framework. HTML + JS vanilla + fetch alle API Supabase.

**Output chiave:** tempo di integrazione segnalazione da ~10 minuti a ~30 secondi.

---

### Fase 4 — GeoJSON pubblico e API (2–3 giorni)
*Il database diventa accessibile esternamente.*

- Endpoint pubblico `GET /strade?municipio=I&classificazione=rosso`
- Endpoint `GET /strade/{id}`
- GeoJSON statico rigenerato ogni notte via GitHub Action e pubblicato su GitHub Pages

URL consegnabile a un developer di Lime/Dott:
```
https://nikolaifissenko.github.io/Streetsmart-Sentille/streetsmart_roma.geojson
```

---

### Fase 5 — Classificazione semi-automatica (1 mese, opzionale)
*Scala da 202 strade a tutta Roma senza lavoro manuale.*

Script OSM che scarica tutte le strade di un municipio e applica regole:

| Attributi OSM | Classificazione assegnata |
|---|---|
| `highway=motorway/trunk` + nessuna `cycleway` | nero |
| `highway=primary/secondary` + `lanes≥3` + nessuna `cycleway` | rosso |
| `cycleway=*` presente | verde |
| `highway=pedestrian` o zona ZTL | blu |

Strade auto-classificate entrano nel DB con `fonte=osm_auto`.
Le Sentinelle diventano **validatori** di un database pre-esistente invece di esploratori da zero.

**Output chiave:** copertura totale Roma in una notte.

---

## 5. Stack finale

| Layer | Tecnologia | Costo |
|---|---|---|
| Database | Supabase — PostgreSQL + PostGIS | Free |
| API | Supabase REST auto-generata | Free |
| Frontend | HTML/JS vanilla | Free |
| Hosting | GitHub Pages | Free |
| GeoJSON build | Python + GitHub Actions (cron) | Free |
| Dati stradali | Overpass API / Nominatim (OSM) | Free |

**Nessun server da gestire.** Supabase è hosted. GitHub Pages è statico. Il costo di infrastruttura fino alla prima vendita B2B è 0€.

---

## 6. Percorso minimo verso la prima demo B2B

```
Fase 0 (fix form)
    ↓
Fase 1 (build.py → GeoJSON)
    ↓
GeoJSON su GitHub Pages
    ↓
Demo deck per Lime / Dott / Tier
```

Le fasi 2–5 vengono dopo il primo contatto commerciale confermato.
