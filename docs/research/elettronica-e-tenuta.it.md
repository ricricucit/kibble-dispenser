# Distributore croccantini: alimentazione, elettronica e tenuta

Ricerca dell'8 novembre 2026. Dove un valore è una mia stima e non viene da una fonte, lo dico esplicitamente. Le fonti sono in fondo.

---

## 0. In breve

- **Alimentazione**: alimentatore esterno certificato da 12 V (circa 3 A, ad esempio Mean Well serie GST36 a 12 V) e solo bassa tensione nella scatola. Niente 230 V dentro la scatola, e niente USB-C come soluzione principale.
- **Servo**: alimentarlo a **6,0–6,8 V**, non a 7,4 V. Il regolatore deve reggere ≥3,5 A di picco. Mettere 1000 µF low-ESR sul connettore del servo. Il servo va su un regolatore separato da quello dell'ESP32, con massa comune a stella.
- **Movimento**: PWM a 50 Hz, salita graduale ("rampa") di 1–2 s, poi stop degli impulsi e spegnimento del regolatore del servo tramite il suo pin EN.
- **Ingresso cavo**: connettore da pannello IP68 Weipu SP13 a 2 poli. In alternativa, pressacavo M16 con un cavo corto e un connettore stagno in linea. Evitare i GX12, che non hanno una tenuta dichiarata.
- **Condensa**: lo standard è una membrana ePTFE di equalizzazione della pressione. Con il limite di 2 fori conviene un **pressacavo ventilato M16**, più una bustina di silica gel e una vernice protettiva acrilica sulla scheda.
- **Tenuta albero**: un O-ring su un albero lento va bene, **ma con 10×2 in un foro da 12,4 lo schiacciamento rischia di arrivare al 40%** (vedi §5). Va portato al 15% circa. Sopra il coperchio serve un "ombrello" (labirinto) che tenga acqua e briciole lontane dalla tenuta.

---

## 1. Architettura di alimentazione

### (a) 230 V nella scatola con modulo AC-DC (es. Mean Well IRM-20-12)
- Il modulo in sé è buono. Ha la certificazione EN 62368-1, emissioni in Classe B e funziona da −30 a +85 °C. **Però è specificato per umidità 20–90% RH senza condensa**, che è proprio la condizione che una scatola all'aperto non garantisce.
- Mean Well stessa scrive che il prodotto finale deve comunque riconfermare la conformità EMC del sistema completo.
- Il rischio vero non è il modulo, ma tutto quello che c'è intorno: morsetti, fusibile, cavo di rete, saldature a 230 V, distanze superficiali e in aria, ancoraggio del cavo, plastica della scatola adatta vicino a parti in tensione. Con la condensa si aggiunge il rischio di scariche superficiali sulla scheda.
- **In serie**: la parte a 230 V va progettata e provata da te come costruttore (sicurezza elettrica, IP reale secondo IEC 60529, prove sulla plastica). Chi installa deve fornire un'alimentazione di rete esterna a norma (CEI 64-8) con differenziale. Costa molto di più in prove e responsabilità.

### (b) Alimentatore esterno a bassa tensione (SELV)
- Tutta la parte a rischio la certifica il produttore dell'alimentatore. Nella scatola restano 12 V.
- **Esempio**: Mean Well GST25A12-P1J, cioè 12 V 2,08 A, Level VI, −30…+70 °C, circa 22 £ + IVA. Per avere margine sui picchi del servo meglio la **GST36 a 12 V (3 A)**: "E" è la versione da muro, "A" quella da tavolo.
- L'alimentatore va comunque **al chiuso** o dentro una presa esterna IP55 con coperchio. All'aperto corre solo il cavo a 12 V.
- **Caduta di tensione (mia stima)**: con 10 m di cavo 2×0,75 mm² la resistenza totale andata e ritorno è circa 0,5 Ω. Con 2,5 A di picco si perde circa 1,2 V, quindi alla scatola arrivano circa 10,8 V. Va benissimo per i regolatori a valle.

### USB-C?
- **A 5 V non basta.** Per avere 7,4 V × 3,5 A servono circa 26 W, cioè più di 5 A a 5 V, ben oltre i 3 A dell'USB standard.
- Servirebbe un "trigger" USB PD a 9 o 12 V (es. il chip CH224K). Però:
  - se l'utente usa un caricatore senza PD, il servo resta senza potenza;
  - i connettori USB-C non sono stagni;
  - i cavi sono corti.
- Ha senso al massimo per una versione da interno.
- Per quanto risulta, il prodotto non rientra nelle categorie della direttiva sul caricatore universale (che riguarda telefoni, tablet, cuffie, portatili ecc.).

### Regole che valgono in entrambi i casi (prodotto con Wi-Fi venduto in serie)
- Si applica la **direttiva RED 2014/53/UE**. L'art. 3.1(a) richiama gli obiettivi di sicurezza della direttiva Bassa Tensione **senza limite inferiore di tensione**: anche a 12 V serve una valutazione di sicurezza, ma con una sorgente SELV a potenza limitata è molto più semplice.
- **EMC e radio**: norme della famiglia EN 301 489, più EN 300 328 per il Wi-Fi.
- **Cybersecurity**: dal 1° agosto 2025 il Regolamento delegato (UE) 2022/30 (standard EN 18031-1) è obbligatorio per i dispositivi radio connessi a internet. In pratica: niente password di default uguali per tutti, aggiornamenti OTA sicuri, API cifrata. Questo pesa sulla scelta firmware (ESPHome o firmware proprio).
- **Altri obblighi**: regolamento GPSR, RoHS, iscrizione al Registro AEE (RAEE) come produttore.
- Un modulo ESP32 già certificato (ESP32-C3-MINI-1, ESP32-S3-WROOM-1) aiuta per le prove radio, ma non sostituisce la Dichiarazione di Conformità del prodotto finito.

**Raccomandazione: (b), alimentatore esterno da 12 V e 3 A con bassa tensione nella scatola.** Il costo per pezzo è simile a (a) (circa 20–25 € l'alimentatore di marca più 4–8 € di connettore), ma il costo di certificazione è molto più basso e la sicurezza in un ambiente umido è nettamente migliore.

---

## 2. Coppia massima dal servo, in sicurezza

### Tensione
- **Dati dei servo simili al tuo:**
  - DS3218MG: 19 kg·cm a 5 V, 21,5 kg·cm a 6,8 V.
  - DS3225MG: 21 kg·cm a 5 V, 24,5 kg·cm a 6,8 V.
  - DS3235: 32 kg·cm a 6 V, 35 kg·cm a 7,4 V.
- **Passare da 6 a 7,4 V dà solo circa il 10% di coppia in più.** La corrente e il calore crescono di più, e su 7,4 V non c'è margine: un regolatore con tolleranza del ±4% può dare circa 7,7 V.
- **Consiglio**: 6,0 V fissi, oppure 6,8 V con un regolatore regolabile. Sali a 7,4 V solo se le prove mostrano che manca coppia.
- **Corsa**: se trovi la variante **a 270°** dello stesso servo, i 180° che ti servono restano lontani dai fine corsa interni. Con un servo da 180° invece lavori agli estremi, e se tocchi il fermo interno il servo resta in stallo.
- **Trasmissione**: alla coppia massima, un'albero con scanalatura a 25 denti stampata in PETG rischia di spanarsi. Meglio una squadretta 25T in alluminio avvitata all'albero stampato.

### Correnti da prevedere
- **Stallo:**
  - Miuzei DS3218: 1,8–2,2 A.
  - FeeTech FT5325M (25 kg·cm, 25T): **3,5 A a 7,4 V**.
  - **Prevedi 3,5 A di picco** sul regolatore del servo.
- **Altri consumi del servo**: a riposo circa 6 mA; in movimento a vuoto circa 120 mA; sotto carico normale, stima di 0,5–1,5 A.
- **ESP32**: in media 80–120 mA, con picchi di 300–500 mA all'avvio del Wi-Fi.
- **Totale all'ingresso a 12 V (stima)**: circa 26 W più 2 W, diviso il rendimento, fa circa 2,5–2,8 A di picco. Per questo l'alimentatore da 3 A: se va in protezione per sovraccarico, resetta tutto.

### Regolatore per il servo (un modulo con tutta la corrente necessaria, niente moduli piccoli)
- **Pololu D36V50F6**: 6 V, 5,5 A tipici, ingresso 6,5–50 V. Ha protezione contro l'inversione di polarità fino a −40 V e un **pin EN** che porta il consumo sotto 1 mA. Costa circa 40 $.
- **Pololu D36V50F7**: versione a 7,5 V, ingresso da 8,3 V. Ha anche protezione da sovracorrente e da sovratemperatura e avvio graduale (soft-start).
- **Hobbywing UBEC 5A V2 Air** (alternativa economica, circa 11 £): ingresso 2–8S, quindi 12 V va bene. Uscita selezionabile 5 / 6 / 7,4 V, 5 A continui e 15 A di picco. Non ha il pin EN.
- **Da evitare per il servo**: MP1584 e LM2596 (3 A nominali, molto meno nella realtà) e gli XL4015 "da 5 A" senza margine.

### Condensatori
- **Sul connettore del servo**: 470–1000 µF low-ESR da 16 V e 105 °C, più 100 nF ceramico in parallelo. Il condensatore assorbe gli impulsi del ponte H interno del servo digitale; lo stallo prolungato lo regge comunque il regolatore.
- **Inverni dell'Alta Langa**: d'inverno gli elettrolitici perdono capacità e la resistenza interna sale. Se puoi, usa un condensatore a polimero solido.
- **All'ingresso a 12 V**: 220–470 µF da 25 V, che smorza anche i picchi quando si collega un cavo lungo.
- **Sul lato ESP32**: 100–470 µF più 100 nF vicino al modulo.

### Cavi
- **Dentro la scatola**: 0,5 mm² (AWG 20) per i 12 V e per l'alimentazione del servo. Il codino originale del servo (circa AWG 22) va bene se resta corto.
- **Niente cavetti Dupont** sull'alimentazione del servo: usa morsetti a vite o saldature.
- **All'esterno**: H05RN-F 2×0,75 o 2×1 mm² (gomma, adatto all'aperto), diametro esterno circa 6–7 mm.

### Segnale da 3,3 V
- Gli ingressi dei servo commutano di solito tra 1,8 e 2,5 V. Il 3,3 V dell'ESP32 funziona quasi sempre, ma con poco margine; alcuni servo vogliono circa 3 V.
- **Procedura**: prova prima diretto, con una resistenza da 220–330 Ω in serie e una da 10 kΩ verso massa sul segnale.
- Se vedi tremolii, aggiungi un **74AHCT1G125** (o 74AHCT125) alimentato a 5 V.
- **GPIO da evitare**, perché cambiano stato all'avvio:
  - ESP32 classico: 0, 2, 12, 15.
  - C3: 2, 8, 9.
  - S3: 0, 3, 45, 46.

### Impostazioni PWM
- 50 Hz con risoluzione di 14 bit (funziona su C3 e S3; il classico arriva oltre). Ogni passo vale circa 1,2 µs, mentre la zona morta del servo è di 2–3 µs.
- In Arduino-ESP32 3.x: `ledcAttach(pin, 50, 14)`, poi `ledcWrite`, poi `ledcDetach`.
- **Ampiezza degli impulsi**: parti da 1000–2000 µs e allarga a passi misurando l'angolo vero. I DS3218 dichiarano 500–2500 µs.
- Lascia 2–3° di margine dai fermi meccanici.

### Rampa e rilascio
- **Rampa**: interpola la posizione a ogni periodo da 20 ms con un profilo morbido all'inizio e alla fine, per 1–2 s in tutto. Mantenere piccolo l'errore di posizione abbassa i picchi di corrente e salva la scanalatura stampata.
- **Rilascio**: arrivato a destinazione, aspetta 300–500 ms e ferma gli impulsi. I servo digitali reagiscono in modi diversi: alcuni tengono la posizione, altri si rilasciano.
- **Spegnimento del servo**: spegnere solo gli impulsi non toglie corrente al servo. Per azzerare consumo, ronzio e calore **spegni anche il regolatore**:
  - con il Pololu, il pin EN tramite un N-MOSFET 2N7002 a drain aperto (EN ha un pull-up interno verso l'ingresso a 12 V: **non collegarlo direttamente al GPIO**);
  - altrimenti, un P-MOSFET sul lato positivo.
- **Ordine giusto**:
  1. accendi il servo;
  2. aspetta 50–100 ms;
  3. manda impulsi all'**ultima posizione salvata** in memoria NVS, così il servo non scatta;
  4. esegui il movimento;
  5. ferma gli impulsi e porta il pin basso;
  6. spegni il servo. Così il servo non viene alimentato attraverso il filo del segnale.
- **ESPHome** fa tutto questo: il componente `servo` ha `transition_length` (rampa) e `auto_detach_time` (rilascio); di default `min_level` è 3% e `max_level` 12%, cioè 600–2400 µs a 50 Hz. Con un output `ledc` a 50 Hz e un interruttore GPIO sul pin EN hai già l'integrazione con Home Assistant.

### Protezione contro i cali di tensione dell'ESP32
- Due regolatori separati che partono dai 12 V, così lo stallo del servo non tocca la tensione dell'ESP32. Massa comune a stella sul condensatore d'ingresso: il ritorno del servo non deve passare per la massa della scheda ESP32.
- Lascia attivo il rilevatore di sottotensione (brownout) e registra `esp_reset_reason()` per accorgerti dei reset `ESP_RST_BROWNOUT` sul campo.
- **Inceppamenti (opzionale ma utile)**: un sensore di corrente INA219 sul ramo del servo, con timeout. Se il disco si blocca sui croccantini, interrompi invece di restare in stallo.

---

## 3. Ingresso cavo

- **Opzione consigliata per il prodotto: connettore da pannello sulla scatola.**
  - Weipu SP13 a 2 poli: IP68, 13 A, 250 V, circa 3–4 $ (TME).
  - Contatti femmina sul lato dell'alimentatore (quello in tensione), maschi sulla scatola.
  - Il grado IP vale **a connettore inserito**: da staccato usa il tappo.
  - Montalo su una parete laterale e fai un'ansa di gocciolamento nel cavo.
- **Alternativa**: M12 codifica A da pannello (es. Binder 09 0435 87 04): IP67, 4 A per contatto, più costoso.
- **Opzione semplice ed economica: pressacavo più cavo corto.**
  - LAPP SKINTOP ST-M16×1,5: serra cavi da 4,5 a 10 mm, IP68, −40…+100 °C, foro circa 16,2–16,5 mm.
  - LAPP ST-M12: serra da 3,5 a 7 mm.
  - Un cavo corto di 30–50 cm esce dalla scatola e finisce con un connettore stagno in linea (SP13 da cavo a cavo): la scatola resta chiusa e il connettore si sostituisce facilmente.
- **Da evitare:**
  - GX12 / GX16 "aviazione": nessun grado IP dichiarato, solo "una certa resistenza all'acqua".
  - Prese DC IP67 (Same Sky PJ-001AH-67): sono da circuito stampato, non da pannello, e una presa a barilotto all'aperto con 3 A di picco non dà affidabilità nel tempo.

---

## 4. Condensa e umidità: la pratica standard

- **Il meccanismo**: ogni ciclo di temperatura gonfia e poi mette in depressione una scatola sigillata. In depressione l'aria umida entra dal punto più debole, **che qui sarebbe proprio la tenuta dell'albero sul coperchio**, dove l'acqua può ristagnare.
- La membrana di equalizzazione elimina la differenza di pressione e protegge anche gli O-ring.
- **Membrana ePTFE** (standard industriale). Per una scatola da circa 4–5 L basta un M12.
  - **Con soli 2 fori**: un **pressacavo ventilato M16**, che fa da passaggio cavo e da sfiato insieme:
    - WISKA ESVG 16: membrana ePTFE, serra cavi da 4,5 a 10 mm, IP68/IP69;
    - Delock 60615: M16, serra da 4 a 8 mm, IP68.
    - È la soluzione indicata per scatole piccole perché evita il secondo foro.
  - **Se scegli invece il connettore SP13**, serve un terzo foro M12 per lo sfiato: Gore PolyVent Standard M12×1 (PMF 100319, circa 6 £). Oppure una membrana adesiva ePTFE su un canalino ricavato nella flangia della boccola, protetto dall'"ombrello" del §5.
  - Monta lo sfiato **di lato**, non in alto dove l'acqua ristagna, e non verniciarlo.
- **Silica gel**: 10–20 g con cartoncino indicatore di umidità, da sostituire o rigenerare durante la manutenzione. Assorbe l'umidità residua ma non sostituisce lo sfiato.
- **Vernice protettiva** su scheda ESP32 e regolatori: acrilico, ad esempio CRC Plastik 70 (facile da trovare in Italia), MG Chemicals 419D, HumiSeal 1B31. Copri prima con nastro i connettori e i pulsanti.
- **Accorgimenti utili:**
  - schede in alto e in verticale, mai sul fondo;
  - lasciare l'ESP32 sempre acceso (0,3–0,5 W) tiene l'interno 1–2 °C sopra l'ambiente e riduce la condensa (mia stima).

---

## 5. Verifica della tenuta dell'albero

### Il concetto va bene
- Velocità di strisciamento trascurabile: circa 20 mm/s per 180° in 1 s.
- Nessuna pressione da contenere.
- L'effetto Gow-Joule (la gomma tirata che si contrae scaldandosi) qui è irrilevante.

### Il punto critico è lo schiacciamento
- **Il calcolo**: un O-ring 10×2 ha diametro esterno 14. Se la gola sull'albero ha fondo da Ø10 (O-ring non tirato), nel foro da 12,4 lo spazio radiale è 1,2 mm contro una sezione di 2 mm: **circa 40% di schiacciamento**.
- **I valori di riferimento**: le tabelle ERIKS per sezione 2,0 mm danno una profondità della sede di 1,45 mm per tenute statiche e **1,60 mm per tenute dinamiche** (larghezza della gola 2,65 mm). Le guide indicano 8–15% di schiacciamento per tenute dinamiche e 20–30% per quelle statiche.
- **Correzione A**: O-ring **9×2**, gola con fondo da **Ø9,0**, foro da **12,4**. Sede profonda 1,7 mm, schiacciamento circa 15%, O-ring non tirato.
- **Correzione B**: tenere il 10×2 con gola da Ø10,2 (2% di tiraggio) e allargare il foro a circa 13,6 (schiacciamento circa 15%). In questo caso l'albero va guidato da un tratto di boccola separato.
- **Attenzione alla stampa FDM**: un foro da 12,4 spesso esce a circa 12,2, cioè +5% di schiacciamento. Ogni 0,1 mm sul diametro vale circa 2,5%. Stampa provini con diametri a passi di ±0,1 mm e misura.

### Stima della coppia di attrito (mia stima, ordini di grandezza)
- Ipotesi:
  - carico radiale per NBR 70 Shore A, sezione 2 mm: circa 0,45 N/mm al 15% e circa 3 N/mm al 40%;
  - coefficiente di attrito lubrificato 0,3–0,5 secondo la fonte (uso 0,4), a secco 1–1,2;
  - contatto: 2 O-ring per 39 mm di circonferenza;
  - raggio: 6,2 mm.
- **Al 15%**: circa 0,09 N·m, cioè **circa 0,9 kg·cm** in movimento e circa 2 kg·cm allo spunto dopo giorni di fermo. Trascurabile.
- **Al 40%**: circa 0,6 N·m, cioè **circa 6 kg·cm** in movimento e fino a circa 15 kg·cm allo spunto se il grasso se n'è andato. Si mangia gran parte della coppia utile: la coppia nominale continua di un servo da 25 kg·cm di stallo è circa 8 kg·cm (dato FT5325M).
- **Un solo O-ring** ben dimensionato più una protezione esterna basta. Il secondo raddoppia l'attrito.

### Grasso
- Grasso al silicone (compatibile con l'NBR), di grado alimentare **NSF H1** perché sta vicino al cibo: ad esempio Super Lube 92003 o Molykote 111.

### Superfici stampate
- Stampa la boccola in verticale: le linee di strato diventano anelli e l'O-ring scorre lungo le linee invece di attraversarle.
- Passa un alesatore nel foro, oppure inserisci una bussola in ottone o inox.

### Paraolio 12×22×5 (DIN 3760 tipo AS in NBR, es. SKF 12×22×5 HMS5 RG)
- Attrito più basso e costante, e il tipo AS ha anche il labbro parapolvere.
- **Però richiede un albero metallico liscio e duro**: sulla PETG il labbro scava un solco e perde. La soluzione è un tratto in **barra rettificata cromata da 12 mm h6** (quella delle stampanti 3D), con il giunto stampato verso la squadretta del servo.
- Sede da 22 mm stampata con leggera interferenza: meglio la versione con diametro esterno in gomma (RG).
- **Labbro principale rivolto verso l'esterno**, perché il fluido da tenere fuori è l'acqua.
- **Per la serie è l'aggiornamento più robusto.**

### Polvere, briciole e pioggia (la cosa più importante, qualunque tenuta scegli)
- Il foro è **sul coperchio, rivolto in alto**: lì l'acqua ristagna.
- Alza la boccola di 5–8 mm sopra il coperchio e fai del mozzo del disco un **cappello** che la copre: sovrapposizione verso il basso di 3 mm o più, gioco radiale di circa 1 mm. Così si forma un labirinto e l'acqua gocciola fuori.
- **In aggiunta (opzionale)**: un V-ring **VA-12** (per alberi da 11,5–12,5 mm, largo 5,5 mm). Va montato sull'albero e il suo labbro preme assialmente sulla faccia superiore della boccola. Rispetta la quota di montaggio del catalogo.

### Viti M3 della flangia
- Se attraversano il coperchio, devono stare **dentro** il cerchio dell'O-ring frontale. Altrimenti servono rondelle di tenuta (in rame, nylon o rondelle bonded M3).
- Con le viti fuori dall'O-ring hai di fatto 3 fori in più non sigillati.

---

## 6. Elenco dei collegamenti, dalla presa al servo

1. **Presa**: presa interna, oppure presa esterna IP55 con coperchio. Alimentatore **12 V 3 A** certificato CE, Level VI (Mean Well serie GST36 a 12 V).
2. **Cavo**: H05RN-F 2×0,75/1 mm², fino a circa 10–15 m, con ansa di gocciolamento. Spina **SP13 femmina** sul lato dell'alimentatore.
3. **Ingresso nella scatola**: presa SP13 da pannello, **oppure** pressacavo ventilato M16 con cavo corto e connettore in linea.
4. **Protezioni**, in quest'ordine:
   - fusibile **T3,15 A** (5×20 in portafusibile da scheda) o PTC con 2,5–3 A di tenuta;
   - **diodo Schottky SS54** in serie contro l'inversione di polarità (oppure P-MOSFET ≥30 V a bassa resistenza);
   - **TVS SMBJ15A** tra 12 V e massa (SMBJ28A se usi 24 V);
   - **470 µF / 25 V più 100 nF**. Questo è il punto di massa a stella.
5. **Ramo servo**:
   - 12 V entrano nel **Pololu D36V50F6** (6 V; oppure l'F7 a 7,5 V, o un UBEC Hobbywing 5A impostato a 6 V);
   - il pin EN è comandato dal GPIO tramite un N-MOSFET 2N7002;
   - **1000 µF low-ESR / 16 V più 100 nF** sul connettore del servo;
   - cavo da 0,5 mm² fino al servo.
6. **Ramo logica**: 12 V entrano in un regolatore da 5 V e 1 A (Pololu D24V10F5 o D36V6F5), poi 100–470 µF più 100 nF, poi il pin 5V/VIN della scheda ESP32 (il suo regolatore interno dà i 3,3 V). Non alimentare la scheda contemporaneamente da USB e dal pin 5V senza verificare che ci sia un diodo.
7. **Segnale**: GPIO, resistenza da 220–330 Ω in serie, eventuale 74AHCT1G125 a 5 V, ingresso segnale del servo. 10 kΩ verso massa sul segnale.
8. **Masse**: tutte riportate al punto a stella. Il ritorno del servo va direttamente al regolatore del servo o al punto a stella, non attraverso la scheda ESP32.
9. **Opzionali**: partitore resistivo dai 12 V a un ingresso analogico per monitorare la tensione; INA219 sul ramo del servo per riconoscere gli inceppamenti.

---

## Fonti

- Specifiche DS3218/DS3225/DS3235 (dsservo): https://rcdrone.top/de/products/dsservo-waterproof-servo-ds3218-20kg-ds3225-25kg-ds3235-35kg
- Miuzei DS3218 (stallo 1,8–2,2 A, 500–2500 µs): https://servodatabase.com/servo/miuzei/ds3218
- FeeTech FT5325M (25 kg·cm, stallo 3,5 A a 7,4 V, 25T): https://www.robotshop.com/products/feetech-180-degrees-digital-servo-74v-25kg-cm-ft5325m
- Mean Well IRM-20 datasheet: https://www.meanwell.com/Upload/PDF/IRM-20/IRM-20-SPEC.PDF
- Mean Well GST25A12-P1J: https://uk.rs-online.com/web/p/ac-dc-adapters/1176129
- Serie Mean Well GST18/25/36: https://www.mouser.ee/new/meanwell/mean-well-gst18-gst25-gst36/
- RED art. 3.1(a), sicurezza senza limite inferiore di tensione: https://cecheck-com.pages.dev/radio-equipment-directive/
- Regolamento delegato RED 2022/30 (dal 1° agosto 2025): https://www.soselectronic.com/en-ki/articles/sos-supplier-of-solution/the-delegated-act-on-cybersecurity-under-red-eu-202230-comes-into-effect-on-1-august-2025-3074
- Pololu D36V50F6: https://www.pololu.com/product/4092/specs
- Pololu D36V50F7: https://www.pololu.com/product/4093
- Hobbywing UBEC 5A V2 Air: https://www.3dxr.co.uk/products/hobbywing-5a-ubec-5v-6v-7-4v-2-8s-v2-air
- LEDC Arduino-ESP32: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html
- Componente servo di ESPHome: https://esphome.io/components/servo/
- Livelli del segnale dei servo e level shifter: https://zbotic.in/servo-signal-wire-pwm-timing-signal-voltage-level-shifting/
- Cali di tensione dell'ESP32: https://www.espboards.dev/troubleshooting/issues/power/esp32-brownout-reset/
- Servo che si scalda dopo detach, interruttore sul positivo: https://industrialmonitordirect.com/blogs/knowledgebase/resolving-rc-servo-heat-after-arduino-detach-power-cutoff-guide
- Servo digitali e mantenimento della posizione: https://forum.pololu.com/t/power-down-digital-servos/3764
- Trigger USB PD CH224: https://www.beyondlogic.org/review-usb-c-power-delivery-trigger-board-ch224/
- Weipu SP13 (TME): https://www.tme.com/in/en/details/sp1312_s2/weipu-connectors/weipu/sp1312-s2-n/
- GX12, nessun grado IP dichiarato: https://elecbee.com/GX12-Aviation-Connector-Feature-and-Environmental-conditions
- Binder M12-A da pannello: https://www.binder-usa.com/us-en/products/automation-technology/m12-a/09-0435-87-04-m12-a-male-panel-mount-connector-4-unshielded-solder-ip67-pg-11
- Prese DC IP67 Same Sky: https://ar.mouser.com/new/same-sky/cui-waterproof-power-jacks
- LAPP ST-M16: https://www.rapidonline.com/catalogue/product/49-2183
- WISKA ESVG 16 (pressacavo ventilato): https://www.electrical4less.co.uk/product/wiska-esvg-16-ventgland-polyamide-pressure-compensation-cable-gland-grey/
- Delock 60615 (pressacavo ventilato M16): https://www.delock.com/produkt/60615/merkmale.html?f=n
- Gore PolyVent M12×1: https://uk.rs-online.com/web/p/enclosure-ventilation/2844819?gb=s
- Sfiato da pannello e pressacavo ventilato a confronto: https://viox.com/breather-plug-vs-breathable-cable-gland/
- Cicli termici e umidità nelle scatole sigillate: https://www.agmcontainer.com/blog/breather-valves/manage-temperature-cycling-sealed-containers/
- ERIKS, progettazione delle sedi per O-ring (sedi radiali, tenute rotanti): https://o-ring.info/en/technical%20manual/eriks%20-%20technical%20manual%20-%20o-ring%20gland%20design%20information.pdf
- Schiacciamento O-ring dinamico/statico e coefficiente d'attrito: https://www.xmbestseal.com/info/o-ring-compression-force-calculation-and-desig-103166838.html
- Paraolio SKF 12×22×5 HMS5 RG: https://www.acorn-ind.co.uk/p/skf/oil-seals/12x22x5hms5rg-skf
- V-ring VA-12: https://memi.ee/product/v-rongastihend-12mm-vollile-fkm-viton/
