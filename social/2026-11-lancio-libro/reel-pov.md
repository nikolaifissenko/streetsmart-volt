# Reel POV libro — copertina, prompt Gemini, caption

Piano del montaggio (tempi, clip, testi a schermo): `README.md`, sezione 3.

## Copertina 9:16
- **Versione grafica pronta:** `reel-cover.png` (1080×1920, sorgente `reel-cover.html`).
  Art. 9 "L'indeciso viene asfaltato." + copertina del libro + logo. Contenuto chiave dentro la
  fascia centrale 3:4, visibile anche nel ritaglio della griglia profilo.
- **Versione fotorealistica (da fare):** POV in bici nel traffico, libro in mano.

## Prompt Gemini — foto POV con il libro in mano
Allegare `libro/cover-it.jpg` nello stesso messaggio.

```
Usa l'immagine allegata come copertina del libro: deve comparire identica (stessi colori, stessa grafica, stesse scritte, la bici con le bande colorate, il logo rotondo in basso a destra), senza reinventarla.

Fotografia fotorealistica verticale 9:16, punto di vista in prima persona di un ciclista che pedala nel traffico di Roma. In basso si vede il manubrio di una bici da città: la mano destra stringe il manubrio, la mano sinistra tiene sollevato verso la camera il libro tascabile con questa copertina, quasi frontale e leggermente inclinato, a fuoco, ben illuminato, grande circa un quarto dell'immagine. Davanti, una strada del centro storico con sampietrini, palazzi color ocra e terracotta, traffico denso: auto ferme, scooter che si infilano, un'utilitaria di traverso a un incrocio. Luce calda del tardo pomeriggio, traffico sullo sfondo leggermente sfocato con un po' di motion blur. Mani anatomicamente corrette, cinque dita. Nessun volto riconoscibile, targhe illeggibili. Stile foto da smartphone, colori naturali. Terzo superiore dell'immagine poco dettagliato. Nessun'altra scritta nell'immagine oltre a quelle della copertina.
```

**Se esce male:**
- Scritte della copertina storpiate (frequente): non rigenerare. Generare con il libro a
  copertina bianca e sovrapporre `cover-it.jpg` in prospettiva in post.
- Mani deformi: rigenerare.
- Libro piccolo o di lato: ripetere "copertina frontale verso la camera".
- `cover-it.jpg` è 600×960: va bene se il libro occupa circa ¼ dell'immagine. Per un primo piano
  serve il file ad alta risoluzione (repo privato `Nikolai-Life-`, `libro-codice-sopravvivenza/`).

**Composizione finale:** sulla foto si aggiungono una sfumatura scura in alto per la leggibilità,
il testo "Art. 9 — L'indeciso viene asfaltato." e il logo, poi export a 1080×1920.

Alternativa più autentica: un fotogramma vero delle clip POV girate, lavorato allo stesso modo.

## Caption Instagram
```
Avevano ragione: il codice della strada non lo rispetto. Rispetto questo. 📕

Art. 9 — L'indeciso viene asfaltato.
Art. 13 — Ogni auto parcheggiata contiene una portiera che sta per aprirsi.

Il Codice della Sopravvivenza: 16 articoli per uscire vivi dalle strade di Roma. Cartaceo e Kindle, IT + EN.

Commenta CODICE e ti mando il link 👇
Qual è l'articolo 17 che manca? Scrivilo qui sotto.

#StreetSmart #RomaInBici #ciclistiurbani #Roma #pov #biciclettaroma #mobilitasostenibile #ciclismourbano #libri #romacentro
```

## Caption TikTok
```
POV: pedali a Roma e hai letto l'unico codice che funziona 📕 Qual è l'articolo 17? #roma #bici #pov #ciclisti #booktokitalia
```

## Note
- La domanda sull'"articolo 17" porta commenti anche da chi non compra, e il reel gira di più.
- TikTok: il link in bio richiede un account business o almeno 1.000 follower. Fino ad allora,
  fissare come primo commento "Cerca *Il Codice della Sopravvivenza* su Amazon".
- "Commenta CODICE" funziona solo con ManyChat (o un tool simile) attivo. Altrimenti i link in DM
  vanno mandati a mano.
- Il link EN punta ancora alla ricerca Amazon finché manca `ASIN_EN`.
