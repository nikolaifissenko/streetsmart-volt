# StreetSmart — Piano Monetizzazione
**Data:** 10 giugno 2026
**Stato database:** 393 strade — Municipi I, II, III completi + segnalazioni Sentinelle su IV, V, VII, VIII, IX, XI, XII, XIII, XIV, XV

---

## 1. Target clienti e modelli di pricing

### A. Operatori micromobilità (Lime, Dott, Tier, Bird)
**Bisogno:** evitare di posizionare/instradare monopattini su strade pericolose (rosso/nero) → meno incidenti, meno responsabilità legale, routing più sicuro nell'app.

| Modello | Descrizione | Prezzo indicativo |
|---|---|---|
| **Licenza dati (one-off)** | Export GeoJSON completo Roma, aggiornamento trimestrale incluso per 1 anno | 3.000–8.000 €/anno per città |
| **API access (subscription)** | Endpoint REST `/strade?municipio=X&classificazione=rosso`, query live, SLA aggiornamento | 500–1.500 €/mese |
| **Pilot gratuito (3 mesi)** | Accesso completo gratis in cambio di feedback + case study + diritto a citarli come referenza | 0 € → conversione a subscription |

**Strategia consigliata:** iniziare con pilot gratuito a 1 operatore (target: Dott o Tier, più piccoli e più reattivi di Lime) per ottenere un caso studio reale prima di vendere agli altri.

### B. Comuni / Roma Capitale (Mobilità, Dipartimento PIL)
**Bisogno:** dati per pianificazione piste ciclabili, prioritizzazione interventi, dati partecipativi (community-sourced) come legittimazione politica.

| Modello | Descrizione | Prezzo indicativo |
|---|---|---|
| **Donazione/partnership iniziale** | Dataset gratuito in cambio di endorsement pubblico / patrocinio | 0 € (investimento in credibilità) |
| **Contratto di fornitura dati** | Licenza annuale dataset + dashboard aggiornamenti | 10.000–30.000 €/anno |
| **Progetto co-finanziato** | Bando PNRR/mobilità sostenibile, StreetSmart come fornitore tecnico | Variabile (grant-based) |

**Nota:** con i Comuni la vendita diretta è lenta (gare, burocrazia). Il valore nel breve termine è la **legittimazione** che genera per la vendita B2B privata.

### C. App di navigazione (Google Maps non raggiungibile, ma Komoot, Bikemap, Geovelo, Cyclers)
| Modello | Descrizione | Prezzo indicativo |
|---|---|---|
| **API access (subscription)** | Layer "rischio ciclabile" sovrapponibile al routing | 300–1.000 €/mese |
| **Revenue share** | % su feature premium "percorso sicuro" se generano abbonamenti | Da negoziare |

---

## 2. Struttura One-Pager Tech (`Street_Smart_One_Pager_Tech.pdf`)

Documento da 1 pagina, per primo contatto con operatori/Comuni. Struttura:

1. **Headline** — "393 strade di Roma classificate per pericolosità ciclistica, validate dalla community"
2. **Il problema** — incidenti ciclisti/monopattini a Roma, mancanza di dati granulari su sicurezza stradale
3. **La soluzione** — sistema di classificazione 7 livelli (verde→nero), dati raccolti da community Sentinelle + validazione
4. **Copertura attuale** — mappa/screenshot GeoJSON, 393 strade, Municipi I-III completi + 10 municipi con segnalazioni
5. **Schema dati** — esempio riga CSV/GeoJSON (id, nome, classificazione, score, coordinate)
6. **Modello di delivery** — GeoJSON export / API REST, aggiornamento periodico
7. **Pricing teaser** — "da 500€/mese — pilot gratuito disponibile"
8. **CTA** — contatto + link demo GeoJSON pubblico

**Dipendenza:** richiede Fase 1 (script `build.py` → GeoJSON, già fatto) e un export pubblico aggiornato su GitHub Pages come demo live.

---

## 3. Go-to-market — sequenza operativa

```
Step 1 — Asset pronti
  ├─ GeoJSON pubblico aggiornato (393 strade) ✅ già disponibile via GitHub Action
  ├─ One-pager tech (sezione 2) — DA CREARE
  └─ Liberatoria startup-friendly per dati community — DA RECUPERARE/FIRMARE

Step 2 — Primo contatto
  ├─ Target: Dott o Tier Roma (team locale, no HQ internazionale)
  ├─ Canale: LinkedIn (city manager / operations manager Roma)
  └─ Offerta: pilot gratuito 3 mesi + accesso GeoJSON

Step 3 — Caso studio
  ├─ Raccogliere metriche d'uso/feedback dal pilot
  └─ Costruire case study ("X strade ad alto rischio evitate nel routing")

Step 4 — Espansione commerciale
  ├─ Usare case study per contattare Lime + altri operatori
  ├─ Parallelo: contatto Comune (Dipartimento Mobilità) con dataset + case study come credibilità
  └─ Prezzo: passare da pilot gratuito a subscription (sezione 1.A)

Step 5 — Crescita database come moltiplicatore di valore
  ├─ Continuare reclutamento Sentinelle (obiettivo 100)
  └─ Coprire municipi mancanti → dataset più completo = pricing più alto
```

---

## 4. Ruolo delle Sentinelle nel pitch

Le Sentinelle non sono solo crowdsourcing dati — sono **prova di domanda sociale** e differenziano StreetSmart da un dataset OSM-derivato:
- "Dati validati da residenti, non solo algoritmi" → argomento di vendita ai Comuni (legittimità partecipativa)
- "Community attiva di N Sentinelle a Roma" → argomento di marketing per operatori micromobilità (storytelling/PR locale)
- Crescita continua del dataset senza costo marginale per StreetSmart

**Azione collegata:** il contatore Sentinelle nel form deve diventare dinamico (vedi `scaleup_report_2026-04-30.md`, Fase 0/2) prima di mostrarlo a investitori/clienti.

---

## 5. Prossimi passi concreti

- [ ] Creare `Street_Smart_One_Pager_Tech.pdf` seguendo la struttura sezione 2
- [ ] Recuperare/firmare `StreetSmart_Liberatoria_Startup_Friendly.pdf` (necessaria prima di condividere dati con terzi commerciali)
- [ ] Pubblicare GeoJSON aggiornato su URL stabile (GitHub Pages) da inserire nell'one-pager
- [ ] Identificare contatto Dott/Tier Roma su LinkedIn per primo pilot
- [ ] Aggiornare contatore Sentinelle a dinamico (dipendenza Fase 0/2 scale-up report)
