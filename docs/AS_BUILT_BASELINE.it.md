# Baseline as-built: dispenser realmente costruito e firmware ESP32 esistente

> **Fonte prioritaria: conversazioni dell'autore con ChatGPT (febbraio/marzo 2026 e 8 novembre 2026), dichiarazioni dirette dell'autore e foto del prototipo.**
>
> **IMPORTANTE:** questa pagina documenta il punto di partenza da NON perdere quando si integra il repository. Non è una certificazione che tutti i dettagli del cablaggio o del firmware corrispondano ai pin attualmente montati: il dump del MicroPython sulla scheda non è ancora disponibile. Ogni punto riporta il suo grado di verifica.

Aggiornato: 2026-11-08. Il repository è stato inizialmente importato con modelli CAD e un **draft ESPHome non flashato**, ma esiste un **prototipo già funzionante con MicroPython su ESP32**, costruito in sessioni precedenti con ChatGPT. L'autore chiede esplicitamente di trattare **la scheda fisica, i componenti assemblati e le interazioni utente esistenti** come baseline, non di ricominciare dal firmware ESPHome.

## 1. Vincoli funzionali del prototipo (confermati dall'autore)

Questi sono i comportamenti che l'autore richiede di preservare e che riferisce come già presenti sul dispositivo installato:

1. **Click to dispense:** una pressione del pulsante dedicato avvia **una sola erogazione**. Nessuna erogazione ripetuta mentre il pulsante rimane premuto.
2. **Dispense at start / all'accensione:** l'attivazione della macchina tramite il comando ON/OFF avvia **una sola erogazione automatica**. In fase di migrazione distinguere accuratamente l'accensione comandata da reboot/watchdog/OTA: non introdurre pasti involontari a ogni reset.
3. **Sound:** ogni erogazione produce un **miagolio tramite speaker** (sintesi di tono/PWM, non è necessario un file audio).
4. **ON/OFF + indicatore:** il comando ON/OFF alterna stato attivo/inattivo e accende/spegne il LED di stato; da OFF, il pulsante dispense non fa partire il motore.
5. **Erogazione a evento:** niente ciclo continuo né erogazioni ripetute nel main loop.
6. **Commenti e codice in inglese**, come richiesto nella conversazione del 24 marzo.

> La conferma attuale dell'autore riguarda il comportamento di prodotto; **non** dimostra che i file di sorgente storici siano presenti nel repository.

### Tabella comportamentale

| Evento | Stato precedente | Azione desiderata |
| --- | --- | --- |
| ON/OFF premuto | OFF | Vai ON, LED ON, **una** erogazione con miagolio |
| ON/OFF premuto | ON | Vai OFF, LED OFF; non erogare |
| DISPENSE premuto | ON | **Una** erogazione con miagolio per pressione |
| DISPENSE premuto | OFF | Nessuna erogazione |
| DISPENSE tenuto premuto | ON | Nessun retrigger fino a rilascio + nuova pressione |
| Avvio fisico o reset | sconosciuto | **Da verificare dal firmware originale**, non dedurre che ogni reboot debba erogare; *2026-11-08: il sorgente di sviluppo importato parte in OFF, quindi un reset non eroga (da confermare sulla copia della scheda)* |
| Wi-Fi indisponibile | qualsiasi | I pulsanti fisici devono mantenere la funzione base (requisito di continuità consigliato, non ancora testato) |

## 2. Hardware, cablaggio e piattaforme (distinguere dati storici da verificati)

### Mappa pin registrata nella sessione MicroPython (24 marzo 2026)

**Stato: mappa documentata/proposta e discussa, non ancora validata contro un dump del firmware o una foto leggibile dell'ESP32 cablato.** *(2026-11-08: coincide con `src/config.py` del sorgente di sviluppo in `firmware/micropython/`; resta da verificare elettricamente, vedi §8.)*

| Dispositivo | GPIO ESP32 classico/WROVER | Note |
| --- | --- | --- |
| LED di stato | GPIO2 | LED acceso = macchina ON |
| Pulsante ON/OFF | GPIO13 | Pull-up interno, attivo LOW |
| Pulsante DISPENSE | GPIO27 | Pull-up interno, attivo LOW |
| Segnale servo | GPIO14 | PWM; cavo giallo |
| Speaker / buzzer passivo | GPIO26 | PWM attraverso resistenza 100–220 Ω, verso GND |

- Servo: marrone -> GND, rosso -> alimentazione servo, giallo -> GPIO di segnale. **Tutte le masse devono essere comuni.**
- Un esperimento *precedente* aveva proposto anche **GPIO4** come servo, prima della mappa GPIO14: verificare la reale connessione; non considerare GPIO4 confermato.
- La scheda discussa all'inizio era un **ESP32 Freenove WROVER**, con **MicroPython v1.27.0** (banner: `Generic ESP32 module with SPIRAM`), usato da **Thonny**. Sul Mac era stata osservata la porta `/dev/cu.usbserial-10` (può cambiare).
- Nel repository 2026-11-08 compare invece una foto di una **Freenove ESP32-S3 WROOM CAM** e il draft ESPHome per S3: **non è dimostrato che sia la stessa scheda attualmente flashata col firmware funzionante**. Prima di applicare pin nuovi, identificare la scheda fisica. *(2026-11-08: la foto, ora `docs/photos/freenove-esp32-cam-board-breadboard-wiring.jpg`, riporta sulla serigrafia "FREENOVE ESP… R", compatibile con la Freenove ESP32-WROVER CAM; la didascalia S3 era errata. Da verificare sul dispositivo.)*

### Alimentazione

- I test storici parlavano di servo 5 V con alimentazione sufficientemente stabile e **massa comune** con ESP32; un alimentatore da banco/USB-C limitato a **5,0 V fino a 3 A** era stato discusso per il test.
- Il documento `docs/research/elettronica-e-tenuta.it.md` definisce una **architettura di prodotto futura** con alimentatore certificato esterno da 12 V, regolatore servo 6 V e regolatore logica 5 V, interruttore EN controllato via MOSFET, protezioni, O-ring e sfiato.
- **Non dichiarare questi regolatori, MOSFET e protezioni installati**, finché foto/cablaggio non lo confermano; sono progettazione, non necessariamente as-built.
- Non alimentare il servo direttamente da un pin 3.3 V dell'ESP32 né attraverso il suo GPIO di segnale. Verificare prima il reale schema di alimentazione.

## 3. Firmware MicroPython storico: cosa sappiamo e cosa manca

- L'autore descrive il comportamento attualmente installato: click-to-dispense, dispense all'accensione, miagolio, LED/ON-OFF.
- È documentata una **proposta** di algoritmo con debounce 50 ms, servo **10° chiuso / 100° aperto**, pausa di assestamento 400 ms, apertura 800 ms e miagolio via sweep PWM circa **750 -> 1300 Hz -> 500 Hz**.
- **Le cifre sopra sono valori del codice/progetto discusso, non misure recuperate dal firmware flashato**. Anche la corsa **180°** dei modelli CAD più recenti non prova che il servo attuale utilizzi 180°.
- La cartella di esercizi iniziali era `Freenove_Super_Starter_Kit_for_ESP32-main`, con precedente prova `tablelamp.py`. Si era ipotizzato un `main.py` per il dispenser e un `CLAUDE.md` per fare il passaggio a un'altra sessione, ma **il sorgente originale completo non è ancora stato recuperato**. *(2026-11-08: è arrivata un'istantanea della cartella di sviluppo, vedi §8; la copia sulla scheda manca ancora.)*
- NON scrivere un file ricostruito chiamandolo "backup firmware originale". Una ricostruzione nuova deve essere chiaramente etichettata **reimplementation / not verified**, e non flashata sul dispositivo senza conferma.

### Recupero non distruttivo prioritario

1. Fotografare la scheda dall'alto e da entrambi i lati, incluse etichette di pin, fili e alimentazioni; aggiungere foto in `docs/photos/`.
2. Collegare il dispositivo a Thonny **senza reinstallare firmware e senza flash**. Copiare/salvare i file visibili sul filesystem MicroPython (in particolare `boot.py`, `main.py`, eventuali moduli) sul computer. In alternativa, in sola lettura: `make ls`, `make backup` e `mpremote cp` da `firmware/micropython/` (vedi il suo README).
3. Creare una directory `import/previous-chat/` con copie **esatte** e datate del codice recuperato dalla scheda e un README di provenienza. Non inserire credenziali Wi-Fi o chiavi in Git.
4. Leggere dal sorgente effettivo i pin, la macchina a stati, il PWM del miagolio, tempi/angoli e gestione avvio; confrontare con la mappa storica qui sopra.
5. Testare il comportamento fisico su banco: una pressione = un ciclo, auto-erogazione solo quando desiderata, tono, spegnimento e blocco dei retrigger.

## 4. Meccanica costruita: cosa preservare

### Versione documentata con ChatGPT

- Dispenser a **gravità**: una ciotola con disco parzialmente forato ruota grazie a un servo; l'apertura permette alle crocchette di uscire in uno scivolo.
- Servo digitale di classe **25 kg·cm**, circa **25 denti (25T)**, nelle conversazioni citato come **DS3225/DS3218-class**; c'è anche una foto con etichetta da 25 kg e 4,8–7,4 V. Verificare modello esatto dalla scritta.
- Per il fissaggio a parete/interno scatola è stato usato e ripreso un supporto `RC_Servo_Mounts.3mf` / `RC_Servo_Mounts(1).3mf` (allegati di una conversazione ChatGPT, **non presenti nel repo GitHub all'8/11**). *(2026-11-08: progetto di terzi in licenza CC BY-NC-SA, non va aggiunto al repository; vedi §8.)*
- L'autore ha **montato** il supporto, poi osservato che la ghiera/asse del servo non risultava centrata rispetto al foro della plastica. La correzione richiesta è **solo uno spessore/distanziale che mantenga la sagoma originale**, non uno spostamento laterale a destra.
- **Spessore 3 mm** era la preferenza esplicita per il primo test, ma l'autore ha chiesto se non servissero **4 o 5 mm**: la misura finale non è verificata. Non trasformarla in una quota definitiva senza una misura reale/foto di controllo.
- Il montaggio a parete esistente deve essere considerato una possibile baseline. Il nuovo `hardware/README.md` descrive invece una **culla integrata nel passante, appesa sotto al coperchio** come soluzione futura; è un'**evoluzione progettata**, non prova che quella soluzione sia già fisicamente montata.

### Stato CAD già nel repository GitHub

Questi sono **artefatti digitali presenti**, non automaticamente pezzi già stampati o assemblati:

- `hardware/3mf/disco_v3.3mf` / `hardware/stl/disco_v3.stl`: disco **Ø103 × 4 mm**, apertura trapezoidale, progetto fino a **180°**.
- `albero_mozzo`: albero Ø12 mm, esagono 8 mm, innesto servo 25T, scanalature O-ring.
- `passante_stagno`: boccola di tenuta con flangia, O-ring frontale 40×2.
- `test_scanalato`: prove di tolleranza dell'innesto 25T.
- `scivolo_v1`: condotto per far uscire una porzione.
- `hardware/cad/build_drivetrain.py`, `build_disc_v2_chute.py`, file JSON dimensioni e check.
- Box impermeabile **265 × 185 mm**, ciotola recuperata, foto di differenti prove d'assemblaggio in `docs/photos/`.
- La differenza geometrica tra corsa firmware proposta 10°–100° e disco progettato a 180° **richiede una calibrazione fisica**, mai assumere interscambiabilità.

### Gap da risolvere (ordine importante)

1. **Conservare il supporto originale e la relativa modifica** nel repository appena gli allegati 3MF risultano disponibili; aggiungere uno stato "fitted / printed / pending". *(2026-11-08: per licenza, nel repository vanno solo attribuzione, foto, misure e stato, non il 3MF né il distanziale derivato; vedi §8.)*
2. Confermare **asse servo ↔ foro ciotola**, distanza dal muro, distanziale finale 3/4/5 mm, direzione di rotazione e fine corsa.
3. Stabilire quali delle parti GitHub sono già fisicamente montate, quali sono solo stampate e quali sono soltanto modellate.
4. Solo dopo decidere se mantenere il montaggio laterale o passare a una culla sottocoperchio; progettare un adattatore invece di cancellare una soluzione che già funziona.

## 5. ESPHome nel repository: non sostituisce la baseline

`firmware/esphome/kibble-dispenser.yaml` è una **prima bozza** convalidata solo da `esphome config`, **non compilata, non flashata e non testata su hardware**. Usa Freenove ESP32-S3 e i pin **GPIO14 (servo), GPIO21 (power enable)** e crea in Home Assistant `Dispense`, `Portions`, `Dwell time`. *(2026-11-08: ora punta all'ESP32 classico, `esp32dev`, con GPIO14 e GPIO32; resta una bozza non flashata, non la baseline.)*

**Gap espliciti rispetto al prodotto costruito:** nel draft non sono implementati il pulsante ON/OFF fisico, il LED di stato, il pulsante di erogazione fisico, il miagolio e la corretta semantica di dispense-at-start. Non è un sostituto drop-in del MicroPython funzionante.

Decisione architetturale **non ancora presa**: restare su MicroPython oppure migrare a ESPHome mantenendo *identici* comportamento e cablaggio dopo verifica. *(2026-11-08: per il prototipo 1 il firmware di riferimento è il MicroPython dell'autore, suo percorso di apprendimento; ESPHome resta l'alternativa per Home Assistant e OTA.)* Se si prosegue con ESPHome, aggiungere prima le funzioni mancanti e poi validare su banco.

## 6. Checklist di accettazione per una migrazione

- [ ] Sorgente originale recuperato dalla scheda e salvato senza alterazioni né segreti
- [ ] Foto e modello esatto della scheda ESP32 attiva, pin e cablaggio confermati
- [ ] Click = un'erogazione, senza duplicati mentre il pulsante è mantenuto
- [ ] ON/OFF attiva LED ed esegue esattamente un'erogazione quando passa a ON
- [ ] OFF non permette nuove erogazioni
- [ ] Miagolio a ogni erogazione
- [ ] Nessuna erogazione imprevista per reset/OTA/fallimento Wi-Fi
- [ ] Servo alimentato correttamente, con massa comune e protezione dai picchi
- [ ] Supporto attuale, distanziale e geometria del foro verificati
- [ ] Angoli, tempi e direzione calibrati sul disco fisicamente montato
- [ ] Firmware nuovo verificato con il dispositivo, prima di sostituire il vecchio

## 7. Come collaborare tra sessioni

Questa pagina e `CLAUDE.md` sono il passaggio di consegne. L'altra sessione deve trattare il contenuto come **vincoli e promemoria di verifica**, non come sostituzione del codice originale; può consolidare foto, dump firmware e dimensioni misurate man mano che arrivano, annotando sempre origine e data. La documentazione CAD del repo non va scartata, ma va collegata a questa baseline fisica.

## 8. Aggiornamento 2026-11-08: sorgente MicroPython, scheda, licenza del supporto

### Sorgente MicroPython importato: istantanea della cartella di sviluppo

- In `firmware/micropython/` c'è il sorgente MicroPython dell'autore, byte per byte: un'**istantanea della sua cartella di sviluppo** del progetto "feedr-outdoor" (versione 0.1.0 del 24/03/2026 più le modifiche non committate dello stesso giorno: fanfara "arcade" al posto del miagolio, duty dello speaker 512, ritardo di avvio di 2 s, deploy mpremote concatenato). Senza storia git.
- **Non è una lettura dal dispositivo.** La copia presente sulla scheda resta da recuperare (Thonny, oppure `make backup` più `mpremote cp`, in sola lettura) e va in `import/previous-chat/` con la provenienza; poi si confrontano le due.
- È il firmware di riferimento (baseline) del prototipo 1; ESPHome resta l'alternativa.
- Pin come definiti nel `config.py` del sorgente di sviluppo: LED 2, ON/OFF 13, servo 14, speaker 26, dispense 27; **non ancora verificati elettricamente**. Resta da escludere sul cablaggio l'esperimento precedente con il servo su GPIO4.
- Comportamento nel sorgente: parte in OFF (un reset non eroga), una erogazione al passaggio comandato a ON, una per pressione quando è ON, nessuna ripetizione tenendo premuto. Servo 10°/100°, assestamento 400 ms, apertura 800 ms. Il miagolio 750→1300→500 Hz resta in `legacy/CatFeeder.py`.

### Scheda

- Documentata come **Freenove ESP32-WROVER** nel `PROJECT.md` dell'autore (ESP32 classico con PSRAM); **da verificare sul dispositivo**. Il banner "Generic ESP32 module with SPIRAM" citato al §2 è coerente.
- Le diciture ESP32-S3 nel repository erano errate e sono state corrette. Il draft ESPHome ora punta all'ESP32 classico ed è etichettato come bozza non flashata, non la baseline.

### Licenza del supporto a parete: solo prototipo

- `RC_Servo_Mounts.3mf` è "Standard Servo Mounts - Horizontal and Vertical" di **Tonym** su MakerWorld (design id US15638e882ab9f8), licenza **CC BY-NC-SA** (non commerciale).
- **Non aggiungere al repository** il 3MF né derivati, compreso il distanziale che ne ricalca la sagoma: qui vanno solo attribuzione, foto e misure. I file restano privati all'autore.
- Il supporto vale **solo per il prototipo**: un prodotto commerciale non può usarlo. È uno dei motivi per cui il progetto disegna una propria culla sotto il coperchio, integrata nel passante (passante_culla).
