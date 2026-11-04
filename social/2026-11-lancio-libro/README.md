# Lancio libro su Instagram + LinkedIn — novembre 2026

"Il Codice della ~~Strada~~ Sopravvivenza" su @streetsmart.nav.
Visual: `slide-1..8.png` (carousel IG, 1080×1350), `linkedin.png` (post LinkedIn).
Sorgente: `carousel.html` (render con Playwright, ogni `.s` = una slide).
Gli articoli citati nelle slide sono quelli reali di `libro/index.html` (Art. 1, 5, 7, 9, 13).

---

## 1. Bio Instagram

**Nome** (campo indicizzato nella ricerca IG, non sprecarlo col solo brand):
```
StreetSmart · Roma in bici
```

**Bio** (≤150 caratteri):
```
Le strade di Roma colorate per pericolo 🟢🔵🟡🔴⚫
Segnalate da ciclisti veri
📕 Il mio libro: Il Codice della Sopravvivenza ↓
```

**Link** (IG ne permette 5 — l'ordine conta, il primo è quello che si vede):
1. `https://nikolaifissenko.github.io/streetsmart-volt/libro/` — titolo: `📕 Il libro`
   (la pagina sceglie la lingua da sola e porta ad Amazon IT/EN: va bene sia per italiani che per turisti)
2. `https://nikolaifissenko.github.io/streetsmart-volt/` — titolo: `🗺️ La mappa`

Durante il lancio il libro sta primo. Finito il lancio (~4 settimane) rimettere la mappa prima.

---

## 2. Carousel annuncio (8 slide)

1. Hook: "A Roma il Codice della Strada non lo rispetta nessuno. Allora ne ho scritto uno nuovo." + copertina
2. Art. 1 — Tutti sono idioti. *Te compreso.*
3. Art. 13 — Ogni auto parcheggiata contiene una portiera che sta per aprirsi.
4. Art. 5 — Fermati ai semafori… quando serve.
5. Art. 7 — Passo d'uomo con la marcia alta. *Il turista con il gelato ha la precedenza assoluta.*
6. Art. 9 — L'indecisione è vietata. *L'indeciso viene asfaltato.*
7. Il libro — copertine IT + EN, 16 articoli, tascabile a colori, Kindle
8. CTA — Commenta CODICE e ti mando il link in DM

**Caption:**
```
Il Codice della Strada a Roma è un suggerimento. Questo no. 📕

Nei miei tour in bici per Roma ripeto sempre le stesse regole. Le ho messe nero su bianco:

🔴 Ogni auto parcheggiata contiene una portiera che sta per aprirsi
🔴 L'indeciso viene asfaltato
🔵 Il turista col gelato ha la precedenza assoluta
⚫ Tutti sono idioti. Te compreso.

16 articoli. Fa ridere, ma ogni regola ti tiene vivo davvero.

Commenta CODICE e ti mando il link 👇
(o link in bio — c'è anche in inglese, per l'amico straniero che vuole affittare una bici a Roma)

#StreetSmart #Roma #RomaInBici #ciclistiurbani #bici #ciclismourbano #mobilitasostenibile #libri #umorismo #romanità #bikelife #cyclingrome #libridaleggere #regalo #KindleItalia
```

---

## 3. Reel POV per il libro (riusa il format che già funziona)

Stesso scheletro dei reel StreetSmart (commento d'odio → POV nel traffico → chiusura),
ma i puntini colorati diventano **gli articoli del Codice**: ogni pericolo che incontri
compare a schermo con il suo articolo. Chiusura: il libro invece della legenda.

**Durata:** 15-20s. Tagli ogni 2-3s. Sottotitoli sempre (80% guarda senza audio).

| Tempo | Video | Testo a schermo |
|---|---|---|
| 0-2s | Screenshot del commento d'odio (vero o ricreato in stile IG) | `"Voi ciclisti il codice della strada neanche sapete cos'è"` |
| 2-4s | Tu sulla bici, camera in faccia, sguardo in camera | `Lo so benissimo. Ne ho scritto uno migliore.` |
| 4-7s | POV: passi accanto a auto parcheggiate | 🔴 `Art. 13 — Ogni auto parcheggiata contiene una portiera che sta per aprirsi` |
| 7-10s | POV: semaforo / incrocio caotico | 🔴 `Art. 5 — Fermati ai semafori… quando serve` |
| 10-13s | POV: centro storico, pedoni, turista col gelato | 🔵 `Art. 7 — Il turista col gelato ha la precedenza assoluta` |
| 13-15s | POV: auto che esita a un incrocio, tu passi deciso | 🔴 `Art. 9 — L'indeciso viene asfaltato` |
| 15-18s | Libro in mano (o nel cestino della bici), copertina ben visibile | `Il Codice della Sopravvivenza · 16 articoli` + `Commenta CODICE 📕` |

**Hook alternativi** (testare uno per reel, stesso montaggio):
- `"I ciclisti a Roma dovrebbero prendere la patente"` → `Ho fatto di meglio. Ho scritto il codice.`
- `POV: sei l'unico a Roma che ha letto il codice della strada` (e vedi tutti violarlo)
- `Le 3 regole che nessuna scuola guida ti insegna su Roma`
- `Guido tour in bici a Roma. Questa è la prima cosa che dico ai turisti.` → Art. 1

**Caption:**
```
Avevano ragione: il codice della strada non lo rispetto. Rispetto questo. 📕

Il Codice della Sopravvivenza — 16 articoli per uscire vivi dalle strade di Roma.

Commenta CODICE e ti mando il link 👇

#StreetSmart #RomaInBici #ciclistiurbani #Roma #pov
```

**Audio:** trend audio a volume basso sotto + nessuna voce, oppure voce tua che legge l'articolo
(la voce dell'autore converte meglio su un prodotto). Copertina reel = frame del libro in mano con
testo grosso "Art. 9 — L'indeciso viene asfaltato".
Versione grafica pronta: `reel-cover.png` (1080×1920, sorgente `reel-cover.html`; contenuto chiave nella fascia centrale 3:4 visibile in griglia profilo).

---

## 4. Post LinkedIn (immagine: `linkedin.png`)

```
Ho scritto un libro. Non è un libro sui dati.

Da più di un anno costruisco StreetSmart: 15.791 strade di Roma classificate per pericolosità ciclistica, verificate da una rete di ciclisti che segnalano quello che vedono ogni giorno.

Ma il dato più interessante l'ho raccolto prima ancora di aprire un CSV: nei tour in bici che guido per Roma passo metà del tempo a spiegare ai turisti come non farsi male. Sempre le stesse regole. Nessuna scritta in un codice ufficiale.

Così le ho scritte io. "Il Codice della Sopravvivenza" è un manuale satirico in 16 articoli, in italiano e in inglese. Fa ridere, ma ogni regola descrive un rischio reale:

— Ogni auto parcheggiata contiene una portiera che sta per aprirsi.
— L'indecisione è vietata: l'indeciso viene asfaltato.
— Tutti sono idioti. Te compreso.

È la stessa intuizione dietro StreetSmart: chi pedala in città sa cose che le mappe non sanno. Il libro le racconta alle persone, il database le dà a chi progetta mobilità — operatori di sharing, navigatori, amministrazioni.

Link al libro nel primo commento.
```

**Versione bilingue IT + EN** (un solo post, IT sopra / EN sotto — il libro esce in entrambe le lingue):
```
Ho scritto un libro. Non è un libro sui dati.

Da più di un anno costruisco StreetSmart: 15.791 strade di Roma classificate per pericolosità ciclistica, verificate da una rete di ciclisti che segnalano quello che vedono ogni giorno.

Nei tour in bici che guido per Roma passo metà del tempo a spiegare ai turisti come non farsi male. Sempre le stesse regole, nessuna scritta in un codice ufficiale. Così le ho scritte io: "Il Codice della Sopravvivenza", 16 articoli satirici. Fa ridere, ma ogni regola descrive un rischio reale:

— Ogni auto parcheggiata contiene una portiera che sta per aprirsi.
— L'indeciso viene asfaltato.
— Tutti sono idioti. Te compreso.

Chi pedala in città sa cose che le mappe non sanno. Il libro le racconta alle persone, StreetSmart le dà a chi progetta mobilità.

🇬🇧
I wrote a book. It's not a book about data.

For over a year I've been building StreetSmart: 15,791 streets in Rome classified by cycling danger, verified by a network of cyclists reporting what they see every day.

On the bike tours I guide around Rome, I spend half the time explaining to tourists how not to get hurt. Always the same rules, none of them written in any official code. So I wrote them down: "Italian Cycling Survival Guide", 16 satirical articles. It's funny, but every rule describes a real risk:

— Every parked car contains a door that is about to open.
— The undecided get flattened.
— Everyone is an idiot. Including you.

People who ride in cities know things maps don't. The book tells people; StreetSmart gives it to those who design mobility.

Link in the first comment · Link nel primo commento.
```

**Primo commento** (link fuori dal post: LinkedIn penalizza la portata dei post con link esterni):
```
📕 Il libro (IT + EN): https://nikolaifissenko.github.io/streetsmart-volt/libro/
🗺️ La mappa: https://nikolaifissenko.github.io/streetsmart-volt/
```

---

## Piano di uscita (2 settimane)

| Giorno | Contenuto |
|---|---|
| G1 | Cambio bio + link. Carousel annuncio → **pinnato** in cima al profilo. Post LinkedIn. |
| G1 | Storie: copertina + sticker link diretto Amazon (1 tap, niente passaggio dalla bio) |
| G3 | Reel POV libro (hook principale) |
| G5 | Reel classico StreetSmart (mappa) — non trasformare il profilo in un catalogo |
| G7 | Reel POV libro (hook alternativo) |
| G10 | Storia: foto di chi l'ha comprato / screenshot recensione (prova sociale) |
| G12 | Reel POV libro (hook alternativo 2) |

Metriche: commenti "CODICE" (= lead), tap sul link in bio (Insights → Attività profilo),
salvataggi del carousel, vendite KDP giorno per giorno sulla dashboard KDP.
