# Carousel "Le scuse per odiare i ciclisti" — bollo auto abolito

Carousel Instagram (7 slide, 1080×1350) agganciato alla notizia del 16
settembre 2026: il Governo abolisce il bollo per il 70% delle auto in
circolazione (veicoli fino a 80 kW, oltre 14,5 milioni tra auto e moto,
dal 2027). Concept: una scusa classica contro i ciclisti (il bollo) è
appena scaduta per decreto — quale sarà la prossima?

Struttura: copertina (foto reale + testo) → assicurazione → traffico/
velocità → doppia fila → codice della strada → modulo con le scuse
depennate → chiusura con la bici bianca (ghost bike).

## Caption Instagram

Il Governo ha appena abolito il bollo per il 70% delle auto in Italia.
Un'altra scusa contro i ciclisti è scaduta prima ancora di essere usata
tutta.

Facciamo il punto delle motivazioni ufficiali per odiarci:

🚫 "Non paga il bollo" → abolito. Anche per le auto, ormai.
🛡️ "Non ha l'assicurazione" → vero. Se cade, rischia solo lui. Quanti
sono morti per colpa di un ciclista? Quanti per colpa di un'auto?
🐌 "Va troppo piano" → detto da chi è fermo in coda un'ora per fare 5 km.
🚗 "Occupa la strada" → detto da chi lascia l'auto in doppia fila "solo 5
minuti".
📵 "Non rispetta il codice della strada" → detto scendendo dal
marciapiede in scooter, contromano.

Le scuse finiscono sempre. Prima o poi ne salta una, come il bollo.

Quello che non finisce è il resto: e a volte il resto è una bici bianca
in mezzo alla strada.

Quale sarà la prossima scusa? Scrivetela nei commenti, prima che ve la
portino via anche quella.

**Hashtag (max 5, per direttiva esplicita — non 10-15 come nel post
Napoli):** #StreetSmart #ciclisti #mobilitasostenibile
#sicurezzastradale #bolloauto

## Post LinkedIn

Oggi il Governo ha abolito il bollo per il 70% delle auto in circolazione
in Italia — oltre 14 milioni di veicoli, motocicli inclusi.

È una buona occasione per fare un punto meno emotivo e più basato sui
dati su un tema che riguarda direttamente chi gestisce flotte di
micromobilità, pianifica infrastrutture ciclabili o sviluppa app di
navigazione: la sicurezza stradale dei ciclisti in Italia non è mai stata
una questione di tasse o di "diritti acquisiti" da parte delle auto. È
una questione di dati mancanti.

Le mappe di rischio ciclistico più diffuse — inclusa quella open-source
più nota, basata su tag OSM — classificano il pericolo per inferenza
algoritmica. Il risultato: strade note per essere pericolose vengono
sottostimate quando OSM non ha il tag corretto, e strade con divieto di
transito ciclabile vengono escluse dalla rete invece che segnalate come a
rischio.

StreetSmart nasce per colmare questo gap: 15.791 strade di Roma
classificate per pericolosità ciclistica, verificate da una rete di
segnalazioni reali — non solo inferenza da tag — con un layer di rischio
pronto da integrare via API in app di navigazione, sistemi di routing per
la micromobilità, o strumenti di pianificazione urbana.

Per chi gestisce flotte o infrastrutture, questo significa routing più
sicuro, meno incidenti, un argomento concreto nel dialogo con le
amministrazioni comunali.

Per saperne di più sull'API commerciale: [link a api.html]

**Hashtag:** #MicromobilitàUrbana #SicurezzaStradale #SmartCity
#DatiGeografici #ProptechMobility

## Note di produzione

- **Copertina**: foto reale (fornita dall'utente, diritti gestiti da lui)
  di Salvini e Meloni, usata intatta — nessun volto generato o alterato
  da AI, solo overlay di testo via HTML/CSS + screenshot Playwright
  (crop per togliere i bottoni UI dello screenshot Instagram originale).
  Deciso dopo aver scartato due strade più rischiose: (1) caricatura/foto
  fotorealistica generata da zero di politici reali — rifiutata da
  Gemini per policy sui volti di persone reali, e comunque territorio
  deepfake indipendentemente dal rifiuto del modello; (2) editing via
  Gemini della foto reale — tecnicamente valido ma ridondante una volta
  che il compositing locale garantisce lo stesso risultato senza
  dipendere dalla disponibilità/policy di un modello esterno.
- **Slide 2-5** (assicurazione, traffico, doppia fila, codice della
  strada): prompt fotorealistici per Gemini (Nano Banana Pro), scena +
  testo overlay in un unico prompt come da metodo consolidato — MAI
  generati in sessione per crediti OpenArt esauriti, solo scritti e
  consegnati all'utente per generazione manuale.
  - Slide 4 (doppia fila) usa come riferimento image-to-image una foto
    reale fornita dall'utente (vigili del fuoco bloccati da doppio
    parcheggio).
  - Slide 5 (codice della strada) usa come riferimento image-to-image
    una foto reale fornita dall'utente (scooter contromano), con
    richiesta esplicita di rimuovere loghi di brand delivery reali dalla
    giacca del rider.
- **Slide 6 (modulo)**: unica slide grafica/non fotografica del
  carosello — un "modulo" con le 5 scuse, la voce del bollo depennata e
  timbrata "ABOLITA". Costruita come pagina HTML (brand: travertino
  #EDE8DF, EB Garamond + Inter, verde #27AE60/rosso #e53935) e
  screenshottata via Playwright, non generata via AI, per garantire
  fedeltà esatta al testo e al brand.
- **Slide 7 (chiusura)**: prompt fotorealistico per Gemini, scena di
  incidente notturno con una "ghost bike" (bici bianca, simbolo reale
  usato nei memoriali per ciclisti uccisi in strada) e il modulo delle
  scuse accartocciato a terra, tutte le voci depennate — non generata in
  sessione, solo il prompt.
- **Tentativi scartati per il carosello nel suo complesso** (per
  riferimento futuro, evitare di ripartire dagli stessi vicoli ciechi):
  (1) versione interamente emoji/icone piatte — scartata, non
  abbastanza seria/professionale; (2) struttura APPROVATO/VIETATO stile
  "Logica Italiota" originale applicata al tema bollo — scartata, il
  concept giusto era la lista di scuse che si esauriscono una a una, non
  un giudizio comportamentale; (3) titolo "Logica Italiota" in copertina
  — rimosso su richiesta esplicita, il carosello non fa più riferimento
  al nome della serie precedente.
