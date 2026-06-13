# StreetSmart — One Pager Tech

_Aggiornato il 2026-06-13_

## Cos'è

StreetSmart è il database B2B delle strade di Roma classificate per pericolosità ciclistica, costruito da una community di Sentinelle e verificato manualmente. Vendibile a operatori di micromobilità (Lime, Dott, Tier), Comuni e app di navigazione per ottimizzare routing e sicurezza dei ciclisti/monopattini.

## Numeri chiave

- **433 strade** classificate a Roma
- **42.0%** delle strade è ad alto rischio (rosso/nero)
- **15.5%** ha una ciclabile presente (verde)
- Copertura: 13 municipi

## Distribuzione classificazioni

| Classificazione | Strade | % |
|---|---|---|
| giallo | 152 | 35.1% |
| rosso | 146 | 33.7% |
| verde | 61 | 14.1% |
| nero | 36 | 8.3% |
| blu | 32 | 7.4% |
| verde-blu | 4 | 0.9% |
| verde-giallo | 2 | 0.5% |

## Municipi a maggior rischio

| Municipio | Zona | Strade | % pericolose |
|---|---|---|---|
| XV | Cassia/Flaminia | 1 | 100.0% |
| XI | Portuense/Magliana | 10 | 70.0% |
| XIII | Aurelio | 12 | 66.7% |

## Formato dati

CSV (source of truth) e GeoJSON/JSON via API statica (`dist/streetsmart_roma.geojson`, `dist/api/strade.json`), aggiornati automaticamente via CI ad ogni nuova segnalazione.

## Community Sentinelle

Obiettivo: 100 Sentinelle attive per la raccolta dati, poi il database viene proposto alle istituzioni comunali.

---

Contatti: Instagram [@streetsmart.nav](https://instagram.com/streetsmart.nav)
