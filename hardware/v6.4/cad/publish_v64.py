#!/usr/bin/env python3
"""
Publish design v6.4 (hardware 6.4.0) and the electronics module case 1.0 from build/ into the repository folders.

build_v64.py calls this at the end of a full run; it can also run on its own after a build:
    python hardware/v6.4/cad/publish_v64.py

Writes:
  hardware/v6.4/assembly/*.stl              meshes at the assembled position (gate open, module in place) for the 3D
                                            viewer: chassis, module and simple placeholders of the bought parts
  hardware/v6.4/assembly/v64_viewer.json    viewer manifest: file names relative to it, names in English, Italian, German
  hardware/v6.4/template/                   1:1 drilling template for the shelf (A4, SVG and PDF)
  hardware/v6.4/cad/v64.json                design data (split, interface, module, review, checks, grams, open risks)
  hardware/v6.4/cad/check_v64.png           section and check image
  hardware/module/case-1.0/parts/           the module case parts as exported by the CAD (assembled position, STL and 3MF)
  hardware/module/case-1.0/interface/       the dimensioned interface drawing between chassis and module (PDF, SVG, PNG)
These folders are emptied first, so they always hold exactly one build. The print-ready files of both products are in
hardware/v6.4/plates/ (plates/tools/run_all.sh rebuilds that package from build/).
Only the Python standard library is needed.
"""
import json
import shutil
import sys
from pathlib import Path

CAD = Path(__file__).resolve().parent
V64 = CAD.parent
MODULE = V64.parent / 'module' / 'case-1.0'
BUILD = CAD / 'build'

TITLE = 'Kibble Dispenser Outdoor v6.4'
STATUS = 'designed and checked in CAD only: not printed, assembled or tested yet'
SUBTITLE = {'en': 'Design v6.4 + module case 1.0 · designed, not yet printed or tested',
            'it': 'Progetto v6.4 + modulo case 1.0 · progettato, non ancora stampato né provato',
            'de': 'Entwurf v6.4 + Modul case 1.0 · konstruiert, noch nicht gedruckt oder getestet'}
STATUS_SHORT = {'en': 'not yet printed or tested', 'it': 'non ancora stampato né provato',
                'de': 'noch nicht gedruckt oder getestet'}
GROUPS = {
    'struttura': {'en': 'Structure', 'it': 'Struttura', 'de': 'Struktur'},
    'dosatore': {'en': 'Dosing', 'it': 'Dosatore', 'de': 'Dosierung'},
    'trasmissione': {'en': 'Drive', 'it': 'Trasmissione', 'de': 'Antrieb'},
    'elettronica': {'en': 'Wiring', 'it': 'Cablaggio', 'de': 'Verkabelung'},
    'guarnizioni': {'en': 'Seals', 'it': 'Guarnizioni', 'de': 'Dichtungen'},
    'ferramenta': {'en': 'Fasteners', 'it': 'Ferramenta', 'de': 'Befestigung'},
    'modulo': {'en': 'Electronics module', 'it': 'Modulo elettronica', 'de': 'Elektronikmodul'},
}
MODULE_PARTS = ['modulo_vasca_v64', 'modulo_coperchio_v64', 'modulo_guarnizione_v64', 'modulo_anello_speaker_v64']
# Part names by viewer id: (English, Italian, German); materials likewise.
NAMES = {
    'guarnizione_piano': ('Shelf gasket (TPU)', 'Guarnizione del ripiano (TPU)', 'Regalbrett-Dichtung (TPU)'),
    'colletto_v6': ('Funnel collar', 'Colletto imbuto', 'Trichterkragen'),
    'flangia_piano_v63': ('Lower flange plate (bayonet, dowel pivot)', 'Flangia inferiore (baionetta, perno a spina)', 'Unterer Flansch (Bajonett, Stiftachse)'),
    'spina_4x6': ('Dowel pin ISO 2338 4x6 (gate pivot)', 'Spina ISO 2338 4x6 (perno della saracinesca)', 'Zylinderstift ISO 2338 4x6 (Schieberachse)'),
    'saracinesca_v63': ('Gate blade (one colour, open)', 'Lama della saracinesca (un colore, aperta)', 'Schieberblatt (einfarbig, offen)'),
    'anello_saracinesca_v63': ('Gate ring (teardrop window, open)', 'Anello della saracinesca (finestra a goccia, aperta)', 'Schieberring (Tropfenfenster, offen)'),
    'flangia_alta_v63': ('Upper flange plate (3 pins, cable-tie window)', 'Flangia superiore (3 spine, finestra della fascetta)', 'Oberer Flansch (3 Stifte, Kabelbinder-Fenster)'),
    'labbro_ombra_v611': ('Skirt lip (TPU, closes the gap)', 'Labbro ombra (TPU, chiude la fessura)', 'Schürzenlippe (TPU, schließt den Spalt)'),
    'passacavo_v63': ('Cable grommet in the flange tunnel (TPU)', 'Passacavo nel tunnel della flangia (TPU)', 'Kabeltülle im Flanschtunnel (TPU)'),
    'viti_legno': ('Wood screws 5x35', 'Viti da legno 5x35', 'Holzschrauben 5x35'),
    'guarnizione_baionetta_v61': ('Bayonet rim lip seal', 'Guarnizione a labbro della baionetta', 'Bajonett-Lippendichtung'),
    'piastra_finestra_nero': ('Window plate (black)', 'Piastra finestra (nero)', 'Fensterplatte (schwarz)'),
    'piastra_finestra_verde': ('Window plate (green)', 'Piastra finestra (verde)', 'Fensterplatte (grün)'),
    'labbri': ('Comb lips (4, all the same)', 'Labbri a pettine (4 uguali)', 'Kammlippen (4 gleiche)'),
    'disco_v61_arancio': ('Self-cleaning dosing disc', 'Disco dosatore autopulente', 'Selbstreinigende Dosierscheibe'),
    'disco_v61_nero': ('Dosing disc (label)', 'Disco dosatore (etichetta)', 'Dosierscheibe (Beschriftung)'),
    'piastra_gate_nero': ('Outlet plate (black)', 'Piastra gate (nero)', 'Auslassplatte (schwarz)'),
    'piastra_gate_verde': ('Outlet plate (green)', 'Piastra gate (verde)', 'Auslassplatte (grün)'),
    'chiocciola_v63': ('Dosing housing (bowl)', 'Chiocciola (vasca dosatore)', 'Dosiergehäuse (Schale)'),
    'linguetta_sicura': ('Safety latch', 'Linguetta di sicurezza', 'Sicherungslasche'),
    'inserti_vasca': ('M3 inserts (bowl, 3)', 'Inserti M3 (vasca, 3)', 'M3-Gewindeeinsätze (Schale, 3)'),
    'pulsante_v611': ('Release button (O-ring)', 'Pulsante di sgancio (O-ring)', 'Entriegelungsknopf (O-Ring)'),
    'viti_guscio': ('PT K30x12 screws, shell to bowl (3)', 'Viti PT K30x12 guscio-vasca (3)', 'PT-K30x12-Schrauben, Hülle an Schale (3)'),
    'scivolo_v611': ('Chute (into the cap)', 'Scivolo (entra nel fondello)', 'Rutsche (in den Boden)'),
    'labbro_scivolo_v611': ('Chute lip ring (TPU, in the cap)', 'Labbro dello scivolo (TPU, nel fondello)', 'Rutschenlippe (TPU, im Boden)'),
    'viti_scivolo': ('PT K30x10 screws, chute (2)', 'Viti PT K30x10 scivolo (2)', 'PT-K30x10-Schrauben, Rutsche (2)'),
    'viti_m3x40': ('M3x40 stack screws, box-tower-bowl (3)', 'Viti M3x40 pacco scatola-torre-vasca (3)', 'M3x40-Stapelschrauben, Gehäuse-Turm-Schale (3)'),
    'oring_3x1': ('O-rings 3x1 under the stack-screw heads (2)', 'O-ring 3x1 sotto le teste delle viti del pacco (2)', 'O-Ringe 3x1 unter den Stapelschrauben (2)'),
    'albero_v6': ('Shaft (module greased for life)', 'Albero (modulo lubrificato a vita)', 'Welle (dauergeschmiertes Modul)'),
    'oring_albero': ('Shaft O-rings 9x2 (2)', 'O-ring albero 9x2 (2)', 'Wellen-O-Ringe 9x2 (2)'),
    'colonna_v63': ('Tower with 3 pillars', 'Torre a 3 pilastri', 'Turm mit 3 Säulen'),
    'oring_faccia': ('Tower-to-box O-ring 24x2', 'O-ring torre-scatola 24x2', 'O-Ring Turm an Gehäuse 24x2'),
    'mozzo_v6': ('Hub (25T spline)', 'Mozzo (scanalato 25T)', 'Nabe (25T-Verzahnung)'),
    'vite_mozzo': ('M3x8 hub screw', 'Vite M3x8 mozzo', 'M3x8-Nabenschraube'),
    'cavo_12v_alimentazione': ('12 V cable in the tunnel, held by the cable tie', 'Cavo 12 V nel tunnel, fissato con la fascetta', '12-V-Kabel im Tunnel, mit Kabelbinder gesichert'),
    'connettore_ip67': ('M8 IP67 inline connector', 'Connettore M8 IP67 in linea', 'M8-IP67-Kupplung'),
    'servo': ('Standard servo', 'Servo standard', 'Standard-Servo'),
    'viti_servo': ('M3x8 servo screws + washers', 'Viti M3x8 servo + rondelle', 'M3x8-Servoschrauben + Scheiben'),
    'oring_pulsante': ('Button O-ring 14x1.5', 'O-ring pulsante 14x1.5', 'Knopf-O-Ring 14x1.5'),
    'cable_tie': ('Strain-relief cable tie (UV)', 'Fascetta antistrappo (UV)', 'Zugentlastungs-Kabelbinder (UV)'),
    'guscio_v64_basso': ('Pod shell, lower part (module opening)', 'Guscio, parte bassa (apertura del modulo)', 'Hülle, unterer Teil (Modulöffnung)'),
    'guscio_v64_alto': ('Pod shell, upper part', 'Guscio, parte alta', 'Hülle, oberer Teil'),
    'scatola_v64': ('Servo bay with the module holder (2 posts)', 'Vano servo con il supporto del modulo (2 colonnine)', 'Servofach mit Modulhalter (2 Säulen)'),
    'inserti_servo': ('M3 inserts (servo cradle, 4)', 'Inserti M3 (culla del servo, 4)', 'M3-Gewindeeinsätze (Servowiege, 4)'),
    'inserti_supporto': ('M3 inserts (module posts, 2)', 'Inserti M3 (colonnine del modulo, 2)', 'M3-Gewindeeinsätze (Modulsäulen, 2)'),
    'pressacavo': ('M12 cable gland IP68 (round servo cable)', 'Pressacavo M12 IP68 (cavo tondo del servo)', 'Kabelverschraubung M12 IP68 (rundes Servokabel)'),
    'sfiato_patch': ('Adhesive ePTFE vent (servo bay)', 'Sfiato ePTFE adesivo (vano servo)', 'Klebe-ePTFE-Belüftung (Servofach)'),
    'cablaggio_12v': ('Chassis harness: 12 V branch to the top M8 connector', 'Cablaggio del telaio: ramo 12 V al connettore M8 in alto', 'Gehäusekabelbaum: 12-V-Zweig zum oberen M8-Stecker'),
    'cablaggio_servo': ('Chassis harness: round servo branch through the gland', 'Cablaggio del telaio: ramo tondo del servo nel pressacavo', 'Gehäusekabelbaum: runder Servozweig durch die Verschraubung'),
    'cablaggio_coda': ('Chassis harness: 190 mm tail with a service loop on the lid', 'Cablaggio del telaio: coda 190 mm con asola di servizio sul coperchio', 'Gehäusekabelbaum: 190-mm-Ende mit Serviceschlaufe auf dem Deckel'),
    'giunzione_y': ('Y splice (heat-shrink sleeve)', 'Giunzione a Y (guaina termorestringente)', 'Y-Spleiß (Schrumpfschlauch)'),
    'fascetta_cablaggio': ('Cable tie 2.5 x 100 (harness anchor)', 'Fascetta 2,5 x 100 (ancoraggio del cablaggio)', 'Kabelbinder 2,5 x 100 (Kabelbaumanker)'),
    'jr_giunzione': ('JR 3-pin connector (servo and branch, in the bay)', 'Connettore JR 3 poli (servo e ramo, nel vano)', 'JR-Stecker 3-polig (Servo und Zweig, im Fach)'),
    'cavetto_servo': ('Original servo lead (in the bay)', 'Cavetto originale del servo (nel vano)', 'Original-Servokabel (im Fach)'),
    'spina_m8_5p': ('M8 5-pin angled plug (J1)', 'Spina M8 5 poli a 90° (J1)', 'M8-Winkelstecker 5-polig (J1)'),
    'guarnizione_fondello_v64': ('Servo bay lip seal', 'Guarnizione a labbro del vano servo', 'Lippendichtung Servofach'),
    'fondello_v64_fondo': ('Cap (bottom, module opening)', 'Fondello (fondo, apertura del modulo)', 'Boden (Unterseite, Modulöffnung)'),
    'fondello_v64_fianco': ('Cap (side)', 'Fondello (fianco)', 'Boden (Seite)'),
    'fondello_v64_bordo': ('Cap (rim)', 'Fondello (bordo)', 'Boden (Rand)'),
    'pt_k30x12_cap': ('PT K30x12 cap screws (4)', 'Viti PT K30x12 del fondello (4)', 'PT-K30x12-Bodenschrauben (4)'),
    'oring_3x1_cap': ('O-rings 3x1 under the cap screws (4)', 'O-ring 3x1 sotto le viti del fondello (4)', 'O-Ringe 3x1 unter den Bodenschrauben (4)'),
    'modulo_vasca_alto': ('Module: tub (upper part)', 'Modulo: vasca (parte alta)', 'Modul: Wanne (oberer Teil)'),
    'modulo_vasca_fondo': ('Module: tub (bottom, speaker grille)', "Modulo: vasca (fondo, griglia dell'altoparlante)", 'Modul: Wanne (Boden, Lautsprechergitter)'),
    'modulo_vasca_pannello_1': ('Module: control panel (LEDs)', 'Modulo: pannello comandi (LED)', 'Modul: Bedienfeld (LEDs)'),
    'modulo_vasca_pannello_2': ('Module: control panel (button)', 'Modulo: pannello comandi (pulsante)', 'Modul: Bedienfeld (Taster)'),
    'modulo_vasca_pannello_3': ('Module: control panel (knock-out 1)', 'Modulo: pannello comandi (predisposizione 1)', 'Modul: Bedienfeld (Ausbruch 1)'),
    'modulo_vasca_pannello_4': ('Module: control panel (knock-out 2)', 'Modulo: pannello comandi (predisposizione 2)', 'Modul: Bedienfeld (Ausbruch 2)'),
    'modulo_vasca_pannello_5': ('Module: control panel (knock-out 3)', 'Modulo: pannello comandi (predisposizione 3)', 'Modul: Bedienfeld (Ausbruch 3)'),
    'modulo_coperchio_v64': ('Module: lid with the J1 turret', 'Modulo: coperchio con la torretta J1', 'Modul: Deckel mit J1-Turm'),
    'modulo_guarnizione_v64': ('Module: lid lip gasket (TPU)', 'Modulo: guarnizione a labbro del coperchio (TPU)', 'Modul: Lippendichtung des Deckels (TPU)'),
    'modulo_anello_speaker_v64': ('Module: speaker adapter ring', "Modulo: anello adattatore dell'altoparlante", 'Modul: Lautsprecher-Adapterring'),
    'switch_12mm_ip67': ('Panel push-button IP67 Ø12', 'Pulsante del pannello IP67 Ø12', 'Bedientaster IP67 Ø12'),
    'lightpipes_5mm': ('Light pipes Ø5 (2)', 'Guide luce Ø5 (2)', 'Lichtleiter Ø5 (2)'),
    'oring_5x1_lightpipe': ('Light-pipe O-rings 5x1 (2)', 'O-ring guide luce 5x1 (2)', 'Lichtleiter-O-Ringe 5x1 (2)'),
    'leds_3mm': ('3 mm LEDs (status, Wi-Fi)', 'LED 3 mm (stato, Wi-Fi)', '3-mm-LEDs (Status, WLAN)'),
    'speaker_23mm': ('Speaker Ø23 (example)', 'Altoparlante Ø23 (esempio)', 'Lautsprecher Ø23 (Beispiel)'),
    'membrane_acoustic_ip67': ('IP67 ePTFE acoustic membrane', 'Membrana acustica IP67 ePTFE', 'Akustikmembran IP67 ePTFE'),
    'board_70x50_A': ('Perfboard 5x7 cm in slot A (example)', 'Millefori 5x7 cm nello slot A (esempio)', 'Lochraster 5x7 cm in Schlitz A (Beispiel)'),
    'esp32_wrover_stack': ('ESP32-WROVER on socket strips (61x28x25 envelope)', 'ESP32-WROVER su strip (ingombro 61x28x25)', 'ESP32-WROVER auf Buchsenleisten (Hüllmaß 61x28x25)'),
    'reg_6v': ('6 V regulator (example)', 'Regolatore 6 V (esempio)', '6-V-Regler (Beispiel)'),
    'reg_5v': ('5 V regulator (example)', 'Regolatore 5 V (esempio)', '5-V-Regler (Beispiel)'),
    'cap_1000uF': ('1000 µF capacitor', 'Condensatore 1000 µF', 'Kondensator 1000 µF'),
    'socket_m8_5p': ('M8 5-pin panel socket (J1)', 'Presa M8 5 poli da pannello (J1)', 'M8-Einbaubuchse 5-polig (J1)'),
    'pt_k30x10_lid': ('PT K30x10 lid screws (5)', 'Viti PT K30x10 del coperchio (5)', 'PT-K30x10-Deckelschrauben (5)'),
    'oring_3x1_lid': ('O-rings 3x1 under the lid screws (5)', 'O-ring 3x1 sotto le viti del coperchio (5)', 'O-Ringe 3x1 unter den Deckelschrauben (5)'),
    'm3x16_module_lock': ('M3x16 module lock screws (2, from below)', 'Viti M3x16 di blocco del modulo (2, da sotto)', 'M3x16-Modulsicherungsschrauben (2, von unten)'),
}
MATERIALS = {
    'NBR70': ('NBR70', 'NBR70', 'NBR70'),
    'PA nero': ('PA black', 'PA nero', 'PA schwarz'),
    'PA66': ('PA66', 'PA66', 'PA66'),
    'PA66 UV': ('PA66, UV-stable', 'PA66 resistente ai raggi UV', 'PA66, UV-beständig'),
    'PC trasparente': ('clear PC', 'PC trasparente', 'PC transparent'),
    'PETG arancio': ('PETG orange', 'PETG arancione', 'PETG orange'),
    'PETG arancione': ('PETG orange', 'PETG arancione', 'PETG orange'),
    'PETG nero': ('PETG black', 'PETG nero', 'PETG schwarz'),
    'PETG verde': ('PETG green', 'PETG verde', 'PETG grün'),
    'PUR 2x0.34': ('PUR 2x0.34', 'PUR 2x0,34', 'PUR 2x0,34'),
    'PUR 3x0.25 Ø4': ('PUR 3x0.25, Ø4', 'PUR 3x0,25, Ø4', 'PUR 3x0,25, Ø4'),
    'PUR 4x0.34': ('PUR 4x0.34', 'PUR 4x0.34', 'PUR 4x0,34'),
    'PUR 5x0.34 Ø4.5': ('PUR 5x0.34, Ø4.5', 'PUR 5x0,34, Ø4,5', 'PUR 5x0,34, Ø4,5'),
    'TPU 95A giallo': ('TPU 95A yellow', 'TPU 95A giallo', 'TPU 95A gelb'),
    'acciaio': ('steel', 'acciaio', 'Stahl'),
    'acciaio / IP67': ('steel / IP67', 'acciaio / IP67', 'Stahl / IP67'),
    'acciaio A2': ('stainless steel A2', 'acciaio inox A2', 'Edelstahl A2'),
    'acciaio inox A2': ('stainless steel A2', 'acciaio inox A2', 'Edelstahl A2'),
    'acquistato': ('bought', 'acquistato', 'gekauft'),
    'ePTFE': ('ePTFE', 'ePTFE', 'ePTFE'),
    'guaina adesiva': ('adhesive-lined heat shrink', 'guaina termorestringente adesiva', 'Schrumpfschlauch mit Kleber'),
    'ottone': ('brass', 'ottone', 'Messing'),
    'piattina 3 fili': ('3-wire flat lead', 'piattina a 3 fili', '3-adriges Flachkabel'),
}


def tri(table, key):
    if key not in table:
        sys.exit(f'publish_v64: no English/Italian/German text for {key!r}; add it to publish_v64.py')
    en, it, de = table[key]
    return {'en': en, 'it': it, 'de': de}


def reset(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def need(path):
    if not path.exists():
        sys.exit(f'publish_v64: missing {path}; run build_v64.py first')
    return path


def publish_assembly():
    man = json.loads(need(BUILD / 'v64_viewer.json').read_text(encoding='utf-8'))
    out = V64 / 'assembly'
    reset(out)
    used = {}
    parts = []
    for p in man['parts']:
        src = need(Path(p['file']))
        name = src.name
        if name in used and used[name] != src:          # same file name from two build folders
            name = f'{src.parent.name}_{name}'
        used[name] = src
        shutil.copy2(src, out / name)
        q = dict(p)
        q['file'] = name
        q['name'] = tri(NAMES, p['id'])
        q['material'] = tri(MATERIALS, p['material'])
        parts.append(q)
    man.update(title=TITLE, subtitle=SUBTITLE, status_short=STATUS_SHORT, status=STATUS, groups=GROUPS, parts=parts)
    (out / 'v64_viewer.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(parts)


def publish_template():
    out = V64 / 'template'
    reset(out)
    for ext in ('svg', 'pdf'):
        shutil.copy2(need(BUILD / 'template_v64' / f'dima_foratura_v64.{ext}'), out / f'dima_foratura_v64.{ext}')


def publish_module():
    parts = MODULE / 'parts'
    reset(parts)
    for k in MODULE_PARTS:
        for ext in ('stl', '3mf'):
            shutil.copy2(need(BUILD / f'{k}.{ext}'), parts / f'{k}.{ext}')
    inter = MODULE / 'interface'
    reset(inter)
    for ext in ('pdf', 'svg', 'png'):
        shutil.copy2(need(BUILD / 'interface_v64' / f'interfaccia_modulo_v64.{ext}'), inter / f'interfaccia_modulo_v64.{ext}')


def main():
    n = publish_assembly()
    publish_template()
    publish_module()
    for f in ('v64.json', 'check_v64.png'):
        shutil.copy2(need(BUILD / f), CAD / f)
    print(f'published: assembly/ ({n} viewer parts), template/, cad/v64.json, cad/check_v64.png, '
          f'module/case-1.0/parts/ ({len(MODULE_PARTS)} parts) and interface/')


if __name__ == '__main__':
    main()
