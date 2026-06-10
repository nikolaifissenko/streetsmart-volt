# StreetSmart — One Pager Tech (bozza testo)
*Da impaginare in PDF come `Street_Smart_One_Pager_Tech.pdf`*

---

## Headline
**393 strade di Roma classificate per pericolosità ciclistica — dati validati dalla community**

---

## Il problema
Roma è tra le città europee con più incidenti che coinvolgono ciclisti e utenti di micromobilità. Operatori di sharing, app di navigazione e amministrazioni locali non hanno accesso a dati granulari, aggiornati e geolocalizzati sulla sicurezza reale delle singole strade — solo dati aggregati sugli incidenti, sempre post-hoc.

## La soluzione
StreetSmart è un database stradale di Roma con un sistema di classificazione a 7 livelli del rischio ciclistico, basato su criteri oggettivi (numero corsie, presenza pista ciclabile, senso di marcia, traffico) e validato da una community di residenti ("Sentinelle").

| Colore | Score | Significato |
|---|---|---|
| nero | 5 | Multicarreggiata alta velocità — pericolosissimo |
| rosso | 4 | Strada trafficata senza ciclabile |
| giallo | 3 | Strada urbana tranquilla senza ciclabile |
| blu | 2 | ZTL / pedonale / alto flusso pedoni |
| verde-giallo | 2 | Ciclabile presente ma inadeguata |
| verde-blu | 1 | Bike-friendly, alto flusso pedonale |
| verde | 1 | Pista ciclabile presente |

## Copertura attuale (dati reali, giugno 2026)
- **393 strade classificate**
- Municipi I, II, III: copertura completa (309 strade)
- Municipi IV, V, VII–IX, XI–XV: segnalazioni community attive (84 strade)
- Distribuzione rischio: 35% giallo, 34% rosso, 14% verde, 8% nero, 6% blu/misto

> *[Inserire qui screenshot mappa GeoJSON con colori per classificazione]*

## Schema dati
```json
{
  "id": "SS-ROM-0001",
  "nome": "Lungotevere Aventino",
  "quartiere": "Aventino/Testaccio",
  "municipio": "I",
  "classificazione": "verde",
  "score": 1,
  "ciclabile": "si",
  "n_corsie": 4,
  "senso_unico": "no",
  "n_testimonianze": 4,
  "note": "pista ciclabile presente separata dal traffico"
}
```
Formato GeoJSON, ogni strada con geometria reale (coordinate OSM).

## Modello di delivery
- **Export GeoJSON** completo, aggiornamento periodico (mensile/trimestrale)
- **API REST** per query live: `/strade?municipio=I&classificazione=rosso`
- Integrazione diretta in sistemi di routing/fleet management

## Perché questi dati sono diversi
Non sono derivati solo da OSM o algoritmi: ogni strada è validata da residenti che la percorrono quotidianamente — la community delle **Sentinelle StreetSmart**, in crescita verso 100 membri attivi a Roma.

## Pricing
- **Pilot gratuito 3 mesi** per primi partner (accesso completo + supporto integrazione)
- Da **500€/mese** per accesso API in abbonamento
- Licenza dati annuale on-demand per Comuni e operatori enterprise

## Contatti
- Instagram: **@streetsmart.nav**
- Demo dati live: https://nikolaifissenko.github.io/streetsmart-volt/streetsmart_roma.geojson
- Email: nikolai.fissenko1@gmail.com
