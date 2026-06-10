# StreetSmart — Il database della pericolosità ciclistica di Roma

## Il problema
Le mappe stradali standard (Google Maps, OSM) non dicono a un ciclista, monopattino o operatore di micromobilità **quanto è rischiosa una strada**. Roma ha migliaia di km di strade molto eterogenee: alcune sicure, molte pericolose. Oggi questa informazione non esiste in forma strutturata e utilizzabile.

## La soluzione
StreetSmart è un database georeferenziato che classifica le strade di Roma su una scala di pericolosità ciclistica (1-5), basato su:
- presenza/assenza di piste ciclabili
- numero di corsie e velocità del traffico
- senso unico, flusso pedonale, ZTL
- segnalazioni dirette di una community di ciclisti reali ("Sentinelle")

**Stato attuale:** 393 strade classificate, copertura su 13 dei 15 municipi di Roma, dataset in formato CSV/GeoJSON pronto per integrazione.

| Colore | Score | Significato | N. strade |
|--------|-------|-------------|-----------|
| Nero | 5 | Multicarreggiata alta velocità | 32 |
| Rosso | 4 | Trafficata, no ciclabile | 132 |
| Giallo | 3 | Urbana tranquilla, no ciclabile | 143 |
| Verde | 1 | Pista ciclabile presente | 55 |
| Blu | 2 | ZTL/pedonale/alto flusso | 25 |

## Per chi è utile

### Operatori di micromobilità (Lime, Dott, Tier, ecc.)
- **Routing più sicuro**: suggerire percorsi a basso rischio agli utenti riduce incidenti, claim assicurativi e danni reputazionali
- **Posizionamento flotta**: evitare di concentrare mezzi su strade ad alto rischio (score 4-5)
- **Dati per assicurazioni/compliance**: dimostrare un approccio data-driven alla sicurezza

### Comune di Roma / Dipartimento Mobilità
- **Mappa prioritaria interventi**: dove costruire piste ciclabili con il maggior impatto sulla sicurezza
- **Dati bottom-up**: la rete Sentinelle fornisce segnalazioni continue dal campo, a costo marginale nullo per l'amministrazione
- **Base per pianificazione PUMS** e monitoraggio nel tempo (il dataset si aggiorna)

## Modello di accesso (proposta)
- **Demo gratuita**: dataset Municipio I (131 strade) in GeoJSON, per valutazione tecnica
- **Licenza dati B2B**: accesso completo al dataset (CSV/GeoJSON/API), aggiornamenti periodici, canone annuale
- **Partnership istituzionale**: dataset completo + collaborazione con la rete Sentinelle per copertura/aggiornamento continuo

## Vantaggio competitivo
- Dati raccolti sul campo, non derivati da modelli statistici generici
- Community attiva (Sentinelle) che garantisce aggiornamento continuo a costo marginale basso
- Pronto all'uso: formato GeoJSON standard, integrabile in qualsiasi stack di routing/mappe

## Contatti
Nikolai Fissenko — nikolai.fissenko1@gmail.com
Instagram: @streetsmart.nav
