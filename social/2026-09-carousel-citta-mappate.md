# Carousel "Città mappate" — Roma, Napoli, Bologna

Carousel Instagram (6 slide, 1080×1350) con le mappe di pericolosità ciclistica
delle 3 città coperte da StreetSmart. Slide: copertina → Roma → Napoli →
Bologna → legenda colori → CTA.

## Caption Instagram

Le strade di Roma, Napoli e Bologna colorate come piste da sci. 🎿

Ogni colore = un livello di pericolo per chi va in bici:
⚫ nero — multicarreggiata ad alta velocità
🔴 rosso — arteria trafficata, zero ciclabile
🟡 giallo — strada urbana senza ciclabile
🔵 blu — ZTL, zona pedonale
🟢 verde — pista ciclabile vera

Non è un algoritmo che indovina dai dati di OpenStreetMap. Sono migliaia di
strade verificate una per una, aggiornate anche grazie alle segnalazioni
delle nostre Sentinelle sul campo.

20.303 strade mappate finora. La mappa è gratuita, la usi prima di uscire
di casa.

Qual è la prossima città? Scrivilo nei commenti 👇

**Hashtag:** #StreetSmart #bicicletta #mobilitasostenibile #ciclabili #Roma

## Post LinkedIn

Abbiamo mappato 20.303 strade in 3 città italiane per capire dove è
pericoloso andare in bici.

Non con un algoritmo che deduce dai tag di OpenStreetMap. Con verifica
diretta, strada per strada.

Il problema con i dati "automatici": una ciclabile non taggata su OSM
sparisce dalla mappa. Una strada con bicycle=no viene esclusa invece che
segnalata come pericolosa. Il risultato è un rischio sistematicamente
sottostimato — proprio dove serve più attenzione.

StreetSmart fa diverso: ogni strada ha una classificazione a 5 livelli (da
pista ciclabile a multicarreggiata ad alta velocità), verificata da una
rete di ciclisti sul campo — le Sentinelle — non solo dedotta da un
dataset.

Oggi il layer copre:
→ Roma — 15.791 strade, il prodotto principale, curato a mano nel tempo
→ Napoli — 2.681 strade, classificazione automatica + prime segnalazioni
reali
→ Bologna — 1.831 strade, stesso metodo

Il dato è pensato per chi deve decidere su questo: operatori di
micromobilità che vogliono ridurre incidenti e ottimizzare il routing,
Comuni che pianificano interventi sulla rete ciclabile, app di navigazione
che vogliono un layer di pericolosità reale invece di un'inferenza.

Licenza commerciale disponibile via API — dati sempre sincronizzati con la
mappa pubblica, nessun database parallelo da tenere aggiornato a mano.

Se lavori in uno di questi ambiti e vuoi vedere il dato su Roma, scrivimi
pure.

**Hashtag:** #micromobilità #ciclabilità #smartcity #geodata #urbanplanning

## Note di produzione

- Le mappe delle 3 slide città sono screenshot reali della PWA (`index.html`
  con selettore città), non mockup — catturate via Playwright headless dopo
  il fix della classificazione dell'anello dei viali di Bologna (vedi
  `scripts/fix_bologna_anello_viali.py`).
- Slide costruite come pagina HTML unica (brand system: travertino #EDE8DF,
  EB Garamond + Inter, i 5 colori di classificazione), non generate via AI
  design tool, per garantire fedeltà esatta al brand.
- File immagine finali (6× PNG 1080×1350) consegnati direttamente
  all'utente in sessione, non versionati in questo repo.
