#!/usr/bin/env python3
"""
Publish design v6.3 from build/ into the repository folders.

build_v63.py calls this at the end of a full run; it can also run on its own after a build:
    python hardware/v6.3/cad/publish_v63.py

Writes (paths relative to hardware/v6.3/):
  assembly/*.stl              meshes at the assembled position (gate open) for the 3D viewer: colour bodies,
                              reused parts and simple placeholders of the bought parts; not for printing
  assembly/v63_viewer.json    viewer manifest: file names relative to it, names in English, Italian and German
  template/                   1:1 drilling template for the shelf (A4, SVG and PDF)
  cad/v63.json                design data (changes, kit split, checks, load case, grams, print notes, open risks)
  cad/check_v63.png           section and check image
assembly/ and template/ are emptied first, so they always hold exactly one build.
The print-ready files are not published here: the print package in plates/ holds them (plates/tools/run_all.sh rebuilds
it from build/; since 6.3.0 the CAD itself carries the print orientations and the dowel hole).
Only the Python standard library is needed.
"""
import json
import shutil
import sys
from pathlib import Path

CAD = Path(__file__).resolve().parent
V63 = CAD.parent
BUILD = CAD / 'build'

TITLE = 'Kibble Dispenser Outdoor v6.3'
STATUS = 'designed and checked in CAD only: not printed, assembled or tested yet'
SUBTITLE = {'en': 'Design v6.3 · designed, not yet printed or tested',
            'it': 'Progetto v6.3 · progettato, non ancora stampato né provato',
            'de': 'Entwurf v6.3 · konstruiert, noch nicht gedruckt oder getestet'}
STATUS_SHORT = {'en': 'not yet printed or tested', 'it': 'non ancora stampato né provato',
                'de': 'noch nicht gedruckt oder getestet'}
GROUPS = {
    'struttura': {'en': 'Structure', 'it': 'Struttura', 'de': 'Struktur'},
    'dosatore': {'en': 'Dosing', 'it': 'Dosatore', 'de': 'Dosierung'},
    'trasmissione': {'en': 'Drive', 'it': 'Trasmissione', 'de': 'Antrieb'},
    'elettronica': {'en': 'Electronics', 'it': 'Elettronica', 'de': 'Elektronik'},
    'guarnizioni': {'en': 'Seals', 'it': 'Guarnizioni', 'de': 'Dichtungen'},
    'ferramenta': {'en': 'Fasteners', 'it': 'Ferramenta', 'de': 'Befestigung'},
}
# Part names by viewer id: (English, Italian, German). The Italian names of build_v63_report.py are tidied here.
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
    'guscio_v611_basso': ('Pod shell, lower part', 'Guscio, parte bassa', 'Hülle, unterer Teil'),
    'guscio_v611_alto': ('Pod shell, upper part', 'Guscio, parte alta', 'Hülle, oberer Teil'),
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
    'scatola_v63': ('Electronics box (cap-screw bosses)', 'Scatola elettronica (bossoli per le viti del fondello)', 'Elektronikgehäuse (Dome für die Bodenschrauben)'),
    'inserti_scatola': ('M3 inserts (box)', 'Inserti M3 (scatola)', 'M3-Gewindeeinsätze (Gehäuse)'),
    'pressacavo': ('M12 cable gland IP68', 'Pressacavo M12 IP68', 'Kabelverschraubung M12 IP68'),
    'sfiato_eptfe': ('M12 ePTFE vent IP68', 'Sfiato ePTFE M12 IP68', 'ePTFE-Belüftung M12 IP68'),
    'cavo_12v_unita': ('12 V cable, unit side', 'Cavo 12 V lato unità', '12-V-Kabel, Seite Einheit'),
    'cavo_12v_alimentazione': ('12 V cable in the tunnel, held by the cable tie', 'Cavo 12 V nel tunnel, fissato con la fascetta', '12-V-Kabel im Tunnel, mit Kabelbinder gesichert'),
    'connettore_ip67': ('M8 IP67 inline connector', 'Connettore M8 IP67 in linea', 'M8-IP67-Kupplung'),
    'servo': ('Standard servo', 'Servo standard', 'Standard-Servo'),
    'viti_servo': ('M3x8 servo screws + washers', 'Viti M3x8 servo + rondelle', 'M3x8-Servoschrauben + Scheiben'),
    'scheda': ('Perfboard 70x50', 'Scheda millefori 70x50', 'Lochrasterplatine 70x50'),
    'esp32': ('ESP32-WROVER dev board', 'Scheda ESP32-WROVER', 'ESP32-WROVER-Entwicklungsboard'),
    'reg_12v': ('Pololu D36V50F6 regulator', 'Regolatore Pololu D36V50F6', 'Spannungsregler Pololu D36V50F6'),
    'reg_5v': ('5 V logic regulator', 'Regolatore 5 V logica', '5-V-Logikregler'),
    'condensatore': ('1000 µF capacitor', 'Condensatore 1000 µF', 'Kondensator 1000 µF'),
    'guarnizione_fondello_v61': ('Cap lip seal', 'Guarnizione a labbro del fondello', 'Lippendichtung Boden'),
    'fondello_v63_fondo': ('Cap (bottom)', 'Fondello (fondo)', 'Boden (Unterseite)'),
    'fondello_v63_fianco': ('Cap (side)', 'Fondello (fianco)', 'Boden (Seite)'),
    'fondello_v63_bordo': ('Cap (rim)', 'Fondello (bordo)', 'Boden (Rand)'),
    'oring_pulsante': ('Button O-ring 14x1.5', 'O-ring pulsante 14x1.5', 'Knopf-O-Ring 14x1.5'),
    'oring_giunto': ('Shell-to-cap seam O-ring 132x2', 'O-ring giunto guscio-fondello 132x2', 'Fugen-O-Ring Hülle-Boden 132x2'),
    'fondello_v63_pannello': ('Control panel: LEDs', 'Pannello comandi: LED', 'Bedienfeld: LEDs'),
    'fondello_v63_pannello_2': ('Control panel: button and knock-out 1', 'Pannello comandi: pulsante e predisposizione 1', 'Bedienfeld: Taster und Ausbruch 1'),
    'fondello_v63_pannello_3': ('Control panel: knock-out 2', 'Pannello comandi: predisposizione 2', 'Bedienfeld: Ausbruch 2'),
    'fondello_v63_pannello_4': ('Control panel: knock-out 3', 'Pannello comandi: predisposizione 3', 'Bedienfeld: Ausbruch 3'),
    'fondello_v63_pannello_5': ('Control panel: west end', 'Pannello comandi: estremo ovest', 'Bedienfeld: Westende'),
    'switch_12mm_ip67': ('Panel push-button IP67 Ø12', 'Pulsante del pannello IP67 Ø12', 'Bedientaster IP67 Ø12'),
    'lightpipes_5mm': ('Light pipes Ø5 (2)', 'Guide luce Ø5 (2)', 'Lichtleiter Ø5 (2)'),
    'oring_5x1_lightpipe': ('Light-pipe O-rings 5x1 (2)', 'O-ring guide luce 5x1 (2)', 'Lichtleiter-O-Ringe 5x1 (2)'),
    'leds_3mm': ('3 mm LEDs (status, Wi-Fi)', 'LED 3 mm (stato, Wi-Fi)', '3-mm-LEDs (Status, WLAN)'),
    'speaker_20mm': ('Ø20 speaker (meow)', 'Altoparlante Ø20 (miagolio)', 'Lautsprecher Ø20 (Miau)'),
    'membrane_acoustic_ip67': ('IP67 ePTFE acoustic membrane', 'Membrana acustica IP67 ePTFE', 'Akustikmembran IP67 ePTFE'),
    'harness_jst': ('Panel harness JST-XH 8-pin', 'Cablaggio pannello JST-XH 8 poli', 'Bedienfeld-Kabelbaum JST-XH 8-polig'),
    'pt_k30x12_cap': ('PT K30x12 cap screws (3)', 'Viti PT K30x12 del fondello (3)', 'PT-K30x12-Bodenschrauben (3)'),
    'oring_3x1_cap': ('O-rings 3x1 under the cap screws (3)', 'O-ring 3x1 sotto le viti del fondello (3)', 'O-Ringe 3x1 unter den Bodenschrauben (3)'),
    'cable_tie': ('Strain-relief cable tie (UV)', 'Fascetta antistrappo (UV)', 'Zugentlastungs-Kabelbinder (UV)'),
}
MATERIALS = {   # Italian (as written by the checks) -> (English, Italian, German)
    'TPU 95A giallo': ('TPU 95A yellow', 'TPU 95A giallo', 'TPU 95A gelb'),
    'PETG verde': ('PETG green', 'PETG verde', 'PETG grün'),
    'PETG nero': ('PETG black', 'PETG nero', 'PETG schwarz'),
    'PETG arancione': ('PETG orange', 'PETG arancione', 'PETG orange'),
    'PETG arancio': ('PETG orange', 'PETG arancione', 'PETG orange'),
    'acciaio': ('steel', 'acciaio', 'Stahl'),
    'acciaio A2': ('stainless steel A2', 'acciaio inox A2', 'Edelstahl A2'),
    'acciaio inox A2': ('stainless steel A2', 'acciaio inox A2', 'Edelstahl A2'),
    'acciaio A4': ('stainless steel A4', 'acciaio inox A4', 'Edelstahl A4'),
    'ottone': ('brass', 'ottone', 'Messing'),
    'NBR70': ('NBR70', 'NBR70', 'NBR70'),
    'PA nero': ('PA black', 'PA nero', 'PA schwarz'),
    'PUR 4x0.34': ('PUR 4x0.34', 'PUR 4x0.34', 'PUR 4x0,34'),
    'acciaio / IP67': ('steel / IP67', 'acciaio / IP67', 'Stahl / IP67'),
    'PC trasparente': ('clear PC', 'PC trasparente', 'PC transparent'),
    'ePTFE': ('ePTFE', 'ePTFE', 'ePTFE'),
    'PA66 UV': ('PA66, UV-stable', 'PA66 resistente ai raggi UV', 'PA66, UV-beständig'),
    'acquistato': ('bought', 'acquistato', 'gekauft'),
}


def tri(table, key):
    if key not in table:
        sys.exit(f'publish_v63: no English/Italian/German text for {key!r}; add it to publish_v63.py')
    en, it, de = table[key]
    return {'en': en, 'it': it, 'de': de}


def reset(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def need(path):
    if not path.exists():
        sys.exit(f'publish_v63: missing {path}; run build_v63.py first')
    return path


def publish_assembly():
    man = json.loads(need(BUILD / 'v63_viewer.json').read_text(encoding='utf-8'))
    out = V63 / 'assembly'
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
    (out / 'v63_viewer.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(parts)


def publish_template():
    """SVG and PDF as built (the PDF is drawn 1:1 on A4 by the checks, the same file the wizard and the manual ship)."""
    out = V63 / 'template'
    reset(out)
    for ext in ('svg', 'pdf'):
        shutil.copy2(need(BUILD / 'template_v63' / f'dima_foratura_v63.{ext}'), out / f'dima_foratura_v63.{ext}')


def main():
    n = publish_assembly()
    publish_template()
    for f in ('v63.json', 'check_v63.png'):
        shutil.copy2(need(BUILD / f), CAD / f)
    print(f'published: assembly/ ({n} viewer parts), template/, cad/v63.json, cad/check_v63.png')


if __name__ == '__main__':
    main()
