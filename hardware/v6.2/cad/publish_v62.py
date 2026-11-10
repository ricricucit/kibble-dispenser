#!/usr/bin/env python3
"""
Publish design v6.2 from build/ into the repository folders.

build_v62.py calls this at the end of a full run; it can also run on its own after a build:
    python hardware/v6.2/cad/publish_v62.py

Writes (paths relative to hardware/v6.2/):
  assembly/*.stl              meshes at the assembled position (gate open) for the 3D viewer: colour bodies,
                              reused parts and simple placeholders of the bought parts; not for printing
  assembly/v62_viewer.json    viewer manifest: file names relative to it, names in English, Italian and German
  template/                   1:1 drilling template for the shelf (A4, SVG and PDF)
  cad/v62.json                design data (changes, kit split, checks, load case, grams, print notes, open risks)
  cad/check_v62.png           section and check image
assembly/ and template/ are emptied first, so they always hold exactly one build.
The print-ready files are not published here: the print package in plates/ is the authoritative print set
(it corrects several CAD print orientations and replaces the printed pivot pin of the lower flange with a dowel);
plates/tools/run_all.sh rebuilds it from build/.
Only the Python standard library is needed (plus rsvg-convert, optional, for the template PDF).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CAD = Path(__file__).resolve().parent
V62 = CAD.parent
BUILD = CAD / 'build'

TITLE = 'Kibble Dispenser Outdoor v6.2'
STATUS = 'designed and checked in CAD only: not printed, assembled or tested yet'
SUBTITLE = {'en': 'Design v6.2 · designed, not yet printed or tested',
            'it': 'Progetto v6.2 · progettato, non ancora stampato né provato',
            'de': 'Entwurf v6.2 · konstruiert, noch nicht gedruckt oder getestet'}
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
# Part names by viewer id: (English, Italian, German). The Italian names of build_v62_checks.py are tidied here.
NAMES = {
    'guarnizione_piano': ('Shelf gasket (TPU)', 'Guarnizione del ripiano (TPU)', 'Regalbrett-Dichtung (TPU)'),
    'colletto_v6': ('Funnel collar', 'Colletto imbuto', 'Trichterkragen'),
    'flangia_piano_v62': ('Lower flange plate (bayonet)', 'Flangia inferiore (baionetta)', 'Unterer Flansch (Bajonett)'),
    'saracinesca_lama': ('Gate blade (open)', 'Lama della saracinesca (aperta)', 'Schieberblatt (offen)'),
    'saracinesca_braccio': ('Gate blade arm (open)', 'Braccio della saracinesca (aperta)', 'Arm des Schieberblatts (offen)'),
    'anello_saracinesca': ('Gate ring with window', 'Anello della saracinesca con finestra', 'Schieberring mit Fenster'),
    'flangia_alta_v62': ('Upper flange plate (gate pocket)', 'Flangia superiore (sede della saracinesca)', 'Oberer Flansch (Schiebertasche)'),
    'viti_unione_flangia': ('ST2.9x9.5 flange join screws (3)', 'Viti ST2.9x9.5 unione flange (3)', 'Flansch-Verbindungsschrauben ST2.9x9.5 (3)'),
    'labbro_ombra_v611': ('Skirt lip (TPU, closes the gap)', 'Labbro ombra (TPU, chiude la fessura)', 'Schürzenlippe (TPU, schließt den Spalt)'),
    'passacavo_v62': ('Cable grommet in the flange tunnel (TPU)', 'Passacavo nel tunnel della flangia (TPU)', 'Kabeltülle im Flanschtunnel (TPU)'),
    'viti_legno': ('Wood screws 5x35', 'Viti da legno 5x35', 'Holzschrauben 5x35'),
    'guarnizione_baionetta_v61': ('Bayonet rim lip seal', 'Guarnizione a labbro della baionetta', 'Bajonett-Lippendichtung'),
    'piastra_finestra_nero': ('Window plate (black)', 'Piastra finestra (nero)', 'Fensterplatte (schwarz)'),
    'piastra_finestra_verde': ('Window plate (green)', 'Piastra finestra (verde)', 'Fensterplatte (grün)'),
    'labbri': ('Comb lips (4, all the same)', 'Labbri a pettine (4 uguali)', 'Kammlippen (4 gleiche)'),
    'disco_v61_arancio': ('Self-cleaning dosing disc', 'Disco dosatore autopulente', 'Selbstreinigende Dosierscheibe'),
    'disco_v61_nero': ('Dosing disc (label)', 'Disco dosatore (etichetta)', 'Dosierscheibe (Beschriftung)'),
    'piastra_gate_nero': ('Outlet plate (black)', 'Piastra gate (nero)', 'Auslassplatte (schwarz)'),
    'piastra_gate_verde': ('Outlet plate (green)', 'Piastra gate (verde)', 'Auslassplatte (grün)'),
    'chiocciola_v62': ('Dosing housing (bowl)', 'Chiocciola (vasca dosatore)', 'Dosiergehäuse (Schale)'),
    'linguetta_sicura': ('Safety latch', 'Linguetta di sicurezza', 'Sicherungslasche'),
    'inserti_vasca': ('M3 inserts (bowl)', 'Inserti M3 (vasca)', 'M3-Gewindeeinsätze (Schale)'),
    'guscio_v611_basso': ('Pod shell, lower part', 'Guscio, parte bassa', 'Hülle, unterer Teil'),
    'guscio_v611_alto': ('Pod shell, upper part', 'Guscio, parte alta', 'Hülle, oberer Teil'),
    'pulsante_v611': ('Release button (O-ring)', 'Pulsante di sgancio (O-ring)', 'Entriegelungsknopf (O-Ring)'),
    'viti_guscio': ('M3x12 screws, shell to bowl', 'Viti M3x12 guscio-vasca', 'M3x12-Schrauben, Hülle an Schale'),
    'scivolo_v611': ('Chute (into the cap)', 'Scivolo (entra nel fondello)', 'Rutsche (in den Boden)'),
    'labbro_scivolo_v611': ('Chute lip ring (TPU, in the cap)', 'Labbro dello scivolo (TPU, nel fondello)', 'Rutschenlippe (TPU, im Boden)'),
    'viti_scivolo': ('M3x10 screws, chute', 'Viti M3x10 scivolo', 'M3x10-Schrauben, Rutsche'),
    'viti_m3x40': ('M3x40 stack screws, box-tower-bowl (3)', 'Viti M3x40 pacco scatola-torre-vasca (3)', 'M3x40-Stapelschrauben, Gehäuse-Turm-Schale (3)'),
    'oring_3x1': ('O-rings 3x1 under the screw heads (2)', 'O-ring 3x1 sotto le teste (2)', 'O-Ringe 3x1 unter den Köpfen (2)'),
    'albero_v6': ('Shaft (module greased for life)', 'Albero (modulo lubrificato a vita)', 'Welle (dauergeschmiertes Modul)'),
    'oring_albero': ('Shaft O-rings 9x2 (2)', 'O-ring albero 9x2 (2)', 'Wellen-O-Ringe 9x2 (2)'),
    'colonna_v62': ('Tower with 3 pillars', 'Torre a 3 pilastri', 'Turm mit 3 Säulen'),
    'oring_faccia': ('Tower-to-box O-ring 24x2', 'O-ring torre-scatola 24x2', 'O-Ring Turm an Gehäuse 24x2'),
    'mozzo_v6': ('Hub (25T spline)', 'Mozzo (scanalato 25T)', 'Nabe (25T-Verzahnung)'),
    'vite_mozzo': ('M3x8 hub screw', 'Vite M3x8 mozzo', 'M3x8-Nabenschraube'),
    'scatola_v62': ('Electronics box (ear and sealed holes)', 'Scatola elettronica (orecchia e fori stagni)', 'Elektronikgehäuse (Lasche und dichte Bohrungen)'),
    'inserti_scatola': ('M3 inserts (box)', 'Inserti M3 (scatola)', 'M3-Gewindeeinsätze (Gehäuse)'),
    'pressacavo': ('M12 cable gland IP68', 'Pressacavo M12 IP68', 'Kabelverschraubung M12 IP68'),
    'sfiato_eptfe': ('M12 ePTFE vent IP68', 'Sfiato ePTFE M12 IP68', 'ePTFE-Belüftung M12 IP68'),
    'cavo_12v_unita': ('12 V cable, unit side', 'Cavo 12 V lato unità', '12-V-Kabel, Seite Einheit'),
    'cavo_12v_alimentazione': ('12 V cable in the tunnel and the channel', 'Cavo 12 V nel tunnel e in canalina', '12-V-Kabel im Tunnel und im Kanal'),
    'connettore_ip67': ('M8 IP67 inline connector', 'Connettore M8 IP67 in linea', 'M8-IP67-Kupplung'),
    'servo': ('Standard servo', 'Servo standard', 'Standard-Servo'),
    'viti_servo': ('M3x8 servo screws + washers', 'Viti M3x8 servo + rondelle', 'M3x8-Servoschrauben + Scheiben'),
    'scheda': ('Perfboard 70x50', 'Scheda millefori 70x50', 'Lochrasterplatine 70x50'),
    'esp32': ('ESP32-WROVER dev board', 'Scheda ESP32-WROVER', 'ESP32-WROVER-Entwicklungsboard'),
    'reg_12v': ('Pololu D36V50F6 regulator', 'Regolatore Pololu D36V50F6', 'Spannungsregler Pololu D36V50F6'),
    'reg_5v': ('5 V logic regulator', 'Regolatore 5 V logica', '5-V-Logikregler'),
    'condensatore': ('1000 µF capacitor', 'Condensatore 1000 µF', 'Kondensator 1000 µF'),
    'guarnizione_fondello_v61': ('Cap lip seal', 'Guarnizione a labbro del fondello', 'Lippendichtung Boden'),
    'fondello_v62_fondo': ('Cap (bottom, Ø24 dishes)', 'Fondello (fondo, conche Ø24)', 'Boden (Unterseite, Mulden Ø24)'),
    'fondello_v62_fianco': ('Cap (side)', 'Fondello (fianco)', 'Boden (Seite)'),
    'fondello_v62_bordo': ('Cap (rim)', 'Fondello (bordo)', 'Boden (Rand)'),
    'nottolino_v611_A': ('Thumb-turn A (O-ring)', 'Nottolino A (O-ring)', 'Drehknebel A (O-Ring)'),
    'nottolino_v611_B': ('Thumb-turn B (O-ring)', 'Nottolino B (O-ring)', 'Drehknebel B (O-Ring)'),
    'nottolino_v611_C': ('Thumb-turn C (O-ring)', 'Nottolino C (O-ring)', 'Drehknebel C (O-Ring)'),
    'oring_nottolini': ('Thumb-turn O-rings 8x1.5 (3)', 'O-ring nottolini 8x1.5 (3)', 'Drehknebel-O-Ringe 8x1.5 (3)'),
    'oring_pulsante': ('Button O-ring 14x1.5', 'O-ring pulsante 14x1.5', 'Knopf-O-Ring 14x1.5'),
    'oring_giunto': ('Shell-to-cap seam O-ring 132x2', 'O-ring giunto guscio-fondello 132x2', 'Fugen-O-Ring Hülle-Boden 132x2'),
    'chiavette': ('Stainless keys 3x3x18 (3)', 'Chiavette 3x3x18 inox (3)', 'Edelstahl-Passfedern 3x3x18 (3)'),
    'canalina_base_1': ('Cable channel: base 1', 'Canalina: base 1', 'Kabelkanal: Unterteil 1'),
    'canalina_coperchio_1': ('Cable channel: cover 1', 'Canalina: coperchio 1', 'Kabelkanal: Deckel 1'),
    'canalina_base_2': ('Cable channel: base 2 (cut to length)', 'Canalina: base 2 (tagliata)', 'Kabelkanal: Unterteil 2 (gekürzt)'),
    'canalina_coperchio_2': ('Cable channel: cover 2', 'Canalina: coperchio 2', 'Kabelkanal: Deckel 2'),
    'canalina_tappo': ('Cable channel: end cap', 'Canalina: tappo di testa', 'Kabelkanal: Endkappe'),
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
    'acquistato': ('bought', 'acquistato', 'gekauft'),
}


def tri(table, key):
    if key not in table:
        sys.exit(f'publish_v62: no English/Italian/German text for {key!r}; add it to publish_v62.py')
    en, it, de = table[key]
    return {'en': en, 'it': it, 'de': de}


def reset(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def need(path):
    if not path.exists():
        sys.exit(f'publish_v62: missing {path}; run build_v62.py first')
    return path


def publish_assembly():
    man = json.loads(need(BUILD / 'v62_viewer.json').read_text(encoding='utf-8'))
    out = V62 / 'assembly'
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
    (out / 'v62_viewer.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(parts)


def publish_template():
    """SVG as built; the PDF is rendered from the SVG with rsvg-convert (cairo) when it is installed, as the wizard and
    the manual ship it, otherwise the matplotlib PDF of the checks is copied. Both are A4 at 1:1."""
    out = V62 / 'template'
    reset(out)
    svg = need(BUILD / 'template_v62' / 'dima_foratura_v62.svg')
    shutil.copy2(svg, out / svg.name)
    pdf = out / 'dima_foratura_v62.pdf'
    if shutil.which('rsvg-convert'):
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(pdf), str(svg)], check=True)
    else:
        shutil.copy2(need(BUILD / 'template_v62' / pdf.name), pdf)


def main():
    n = publish_assembly()
    publish_template()
    for f in ('v62.json', 'check_v62.png'):
        shutil.copy2(need(BUILD / f), CAD / f)
    print(f'published: assembly/ ({n} viewer parts), template/, cad/v62.json, cad/check_v62.png')


if __name__ == '__main__':
    main()
