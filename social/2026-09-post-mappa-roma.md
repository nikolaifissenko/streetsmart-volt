# Post mappa Roma — screenshot reale

Screenshot reale della mappa Roma (zoom sul centro, tutti e 5 i colori
visibili) con card overlay brandizzata, stesso formato del post mappa
Napoli.

## Caption Instagram

Roma vista come una pista da sci. 🎿

Ogni colore = un livello di pericolo per chi va in bici:
⚫ nero — multicarreggiata ad alta velocità
🔴 rosso — arteria trafficata, zero ciclabile
🟡 giallo — strada urbana senza ciclabile
🔵 blu — ZTL, zona pedonale
🟢 verde — pista ciclabile vera

Su 15.791 strade mappate, solo 168 hanno una pista ciclabile. L'1,1%.

Non è un algoritmo che indovina dai tag di OpenStreetMap: sono strade
verificate una per una, aggiornate anche grazie alle segnalazioni delle
nostre Sentinelle sul campo.

La mappa è gratuita, usala prima di uscire di casa (link in bio).

Conosci una strada pericolosa che manca? Segnalacela dalla tab Segnala
della PWA, o scrivilo nei commenti 👇

**Hashtag:** #StreetSmart #Roma #ciclabili #bicicletta #mobilitasostenibile
#ciclismourbano #RomaInBici #urbanplanning #micromobilita #stradesicure

## Caption Instagram (v2, alternativa)

712 strade di Roma sono classificate come pericolose per chi va in bici.
Solo 153 sono sicure. 🚴

Non è una sensazione — è il risultato di 15.791 strade verificate una
per una:
⚫ 78 nerissime — multicarreggiata, zero protezione
🔴 634 rosse — trafficate, senza ciclabile
🟡 13.397 gialle — urbane, senza ciclabile
🔵 829 blu — ZTL, zone pedonali
🟢 153 verdi — le uniche con una pista ciclabile vera

Il rapporto è quasi 5 a 1: per ogni strada sicura, quasi 5 sono
pericolose.

Non è un algoritmo che indovina dai tag di OpenStreetMap. È verificato
sul campo, strada per strada, anche grazie alle segnalazioni delle
nostre Sentinelle.

La mappa è gratuita — guarda la tua strada prima di uscire di casa
(link in bio).

Manca una strada pericolosa che conosci? Segnalacela dalla tab Segnala,
o scrivilo nei commenti 👇

**Hashtag:** #StreetSmart #Roma #ciclabili #bicicletta #mobilitasostenibile
#ciclismourbano #RomaInBici #sicurezzastradale #micromobilita #cityplanning

## Post LinkedIn

15.791 strade di Roma classificate per pericolosità ciclistica. Solo
l'1,1% ha una pista ciclabile.

Non un'inferenza da tag OpenStreetMap: ogni strada è verificata a mano,
nel tempo, e aggiornata dalle segnalazioni sul campo di una rete di
ciclisti reali — le Sentinelle.

Il dato è pensato per chi deve decidere su questo: operatori di
micromobilità che vogliono ridurre incidenti e ottimizzare il routing,
Comuni che pianificano interventi sulla rete ciclabile, app di
navigazione che cercano un layer di pericolosità reale invece di
un'inferenza.

Licenza commerciale disponibile via API — dati sempre sincronizzati con
la mappa pubblica, nessun database parallelo da tenere aggiornato a
mano.

Se lavori in uno di questi ambiti e vuoi vedere il dato su Roma,
scrivimi pure.

**Hashtag:** #micromobilità #ciclabilità #smartcity #geodata #urbanplanning

## Note di produzione

- Screenshot reale (non mockup), prodotto con Playwright: apre
  `index.html` in locale (Roma è la città di default), aspetta che i
  path SVG delle strade colorate siano renderizzati
  (`document.querySelectorAll('#map path').length > 3000`, non un
  timeout fisso), poi centra la mappa sul centro storico
  (`mapInstance.setView([41.9028, 12.4964], 14)`) per massimizzare la
  densità e varietà di colori visibili nell'inquadratura.
- Header, tab nav, sidebar e toolbar mobile nascosti via CSS iniettato
  (`#map` portato a `position:fixed` a piena pagina) prima dello
  screenshot, poi `mapInstance.invalidateSize()` per far ridisegnare
  Leaflet sul nuovo contenitore — necessari almeno 2-3s di attesa dopo
  l'invalidate prima dello screenshot, altrimenti la mappa risulta
  vuota (tile e strade non ancora ridisegnati sul contenitore
  ridimensionato).
- Card overlay iniettata via JS (`insertAdjacentHTML`) dopo il resize
  della mappa, non prima — stesso schema del post Napoli (logo SVG
  dell'header, "Roma" in EB Garamond 64px, stat in badge verde
  pillola), posizionata in alto a sinistra su sfondo travertino
  semi-opaco con ombra, leggibile sopra qualunque densità di strade
  sottostante.
- Viewport Playwright impostato direttamente a 1080×1350 (formato 4:5
  IG) con `device_scale_factor=2`: lo screenshot finale non richiede
  crop successivo con PIL, a differenza del post Napoli.
- Stat scelta come hook: 168 strade su 15.791 hanno una pista ciclabile
  a Roma (1,1%) — dato reale da
  `data/master/streetsmart_roma_completo.csv` (campo
  `ciclabile_presente`), non inventato.
- Hashtag portati a 10 (mix niche/medio) invece dei 5 usati per il post
  Napoli, seguendo la nota di produzione già in CLAUDE.md sulla resa
  ottimale per un account a 533 follower.
- File immagine finale consegnato direttamente all'utente in sessione,
  non versionato in questo repo (stessa convenzione del post Napoli).
- Stat alternativa per la v2: 712 strade nero+rosso (78+634) vs 153
  verdi, stesso CSV, campo `classificazione`/`ciclabile_presente` — numeri
  coerenti con i contatori "Dangerous"/"Safe" già mostrati in header su
  `index.html`.
