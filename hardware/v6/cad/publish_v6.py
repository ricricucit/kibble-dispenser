#!/usr/bin/env python3
"""
Publish design v6 from build/ into the repository folders.

build_v6.py calls this at the end of a full run; it can also run on its own after a build:
    python hardware/v6/cad/publish_v6.py

Writes (paths relative to hardware/v6/):
  stl/<part>.stl             print-ready, oriented for the bed (whole part)
  stl/<part>_<colour>.stl    one body per filament colour, for the multi-colour parts
  3mf/<part>.3mf             print-ready, oriented for the bed, one object per filament colour
  assembly/*.stl             assembled position in the v6 frame, for the 3D viewer: colour bodies,
                             reused parts and simple placeholders of the bought parts
  assembly/v6_viewer.json    viewer manifest: file names relative to it, names in English, Italian
                             and German, without the ghost DN50 pipe
  cad/v6.json                design data, with "files" pointing at the published paths
  cad/check_v6.png           section check image
stl/, 3mf/ and assembly/ are emptied first, so they always hold exactly one build.
Only the Python standard library is needed.
"""
import json
import shutil
import sys
from pathlib import Path

CAD = Path(__file__).resolve().parent
V6 = CAD.parent
BUILD = CAD / 'build'

# v4b and v5 parts that v6 reuses unchanged (printed from the same files)
REUSED = ['piastra_gate_v4b', 'piastra_finestra_v4b', 'linguetta_sicura', 'guarnizione_baionetta',
          'labbro_uscita_1', 'labbro_uscita_2', 'labbro_finestra_1', 'labbro_finestra_2', 'guarnizione_piano_v5']
NOT_PARTS = {'assembled_position_copies', 'check', 'viewer'}
DROP_FROM_VIEWER = {'tubo_dn50'}       # optional pipe, drawn as a ghost; the forest scene draws its own

STATUS = 'designed and checked in CAD only: not printed, assembled or tested yet'

TITLE = 'Kibble Dispenser Outdoor v6'
SUBTITLE = {'en': 'Design v6 · designed, not yet printed or tested',
            'it': 'Progetto v6 · progettato, non ancora stampato né provato',
            'de': 'Entwurf v6 · konstruiert, noch nicht gedruckt oder getestet'}
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
# Part names: Italian from build_v6_checks.py, English and German here (by viewer id).
NAMES = {
    'guarnizione_piano': ('Shelf gasket (TPU)', 'Regalbrett-Dichtung (TPU)'),
    'colletto_v6': ('Funnel collar', 'Trichterkragen'),
    'flangia_piano_v6': ('Shelf flange', 'Regalflansch'),
    'viti_legno': ('Wood screws 5x25', 'Holzschrauben 5x25'),
    'guarnizione_baionetta': ('Bayonet gasket', 'Bajonett-Dichtung'),
    'piastra_finestra_nero': ('Window plate (black)', 'Fensterplatte (schwarz)'),
    'piastra_finestra_verde': ('Window plate (green)', 'Fensterplatte (grün)'),
    'labbri': ('Plate lips (4)', 'Plattenlippen (4)'),
    'disco_v6_arancio': ('Dosing disc', 'Dosierscheibe'),
    'disco_v6_nero': ('Dosing disc (label)', 'Dosierscheibe (Beschriftung)'),
    'piastra_gate_nero': ('Gate plate (black)', 'Auslassplatte (schwarz)'),
    'piastra_gate_verde': ('Gate plate (green)', 'Auslassplatte (grün)'),
    'chiocciola_v6': ('Dosing bowl', 'Dosierschale'),
    'linguetta_sicura': ('Safety latch', 'Sicherungslasche'),
    'inserti_vasca': ('M3 inserts (bowl)', 'M3-Gewindeeinsätze (Schale)'),
    'scivolo_v6': ('55° chute with hood', '55°-Rutsche mit Haube'),
    'viti_scivolo': ('M3x10 screws, chute', 'M3x10-Schrauben, Rutsche'),
    'tubo_dn50': ('DN50 pipe (optional)', 'DN50-Rohr (optional)'),
    'viti_torre_vasca': ('M3x12 screws, tower to bowl', 'M3x12-Schrauben, Turm an Schale'),
    'albero_v6': ('Shaft', 'Welle'),
    'oring_albero': ('Shaft O-rings 9x2 (2)', 'Wellen-O-Ringe 9x2 (2)'),
    'colonna_v6': ('Tower (shaft bushing)', 'Turm (Wellendurchführung)'),
    'oring_faccia': ('Tower-to-box O-ring 24x2', 'O-Ring Turm an Gehäuse 24x2'),
    'viti_torre_scatola': ('M3x10 screws, tower to box', 'M3x10-Schrauben, Turm an Gehäuse'),
    'mozzo_v6': ('Hub (25T spline)', 'Nabe (25T-Verzahnung)'),
    'vite_mozzo': ('M3x8 hub screw', 'M3x8-Nabenschraube'),
    'scatola_v6': ('Electronics box', 'Elektronikgehäuse'),
    'inserti_scatola': ('M3 inserts (box)', 'M3-Gewindeeinsätze (Gehäuse)'),
    'pressacavo': ('M16 cable gland', 'Kabelverschraubung M16'),
    'servo': ('Standard servo', 'Standard-Servo'),
    'viti_servo': ('M3x8 servo screws + washers', 'M3x8-Servoschrauben + Scheiben'),
    'breadboard': ('Breadboard 165x55', 'Steckbrett 165x55'),
    'esp32': ('ESP32-WROVER dev board', 'ESP32-WROVER-Entwicklungsboard'),
    'reg_12v': ('Pololu D36V50F6 regulator', 'Spannungsregler Pololu D36V50F6'),
    'reg_5v': ('5 V logic regulator', '5-V-Logikregler'),
    'condensatore': ('1000 µF capacitor', 'Kondensator 1000 µF'),
    'silica': ('Silica gel 10 g', 'Silicagel 10 g'),
    'guarnizione_fondello_v6': ('Cover lip seal', 'Lippendichtung Deckel'),
    'fondello_v6_nero': ('Bottom cover', 'Bodendeckel'),
    'fondello_v6_arancio': ('Bottom cover (lettering)', 'Bodendeckel (Beschriftung)'),
    'nottolini_v6': ('Quarter-turn buttons', 'Vierteldrehknöpfe'),
}
MATERIALS = {
    'TPU 95A giallo': ('TPU 95A yellow', 'TPU 95A gelb'),
    'PETG verde': ('PETG green', 'PETG grün'),
    'PETG nero': ('PETG black', 'PETG schwarz'),
    'PETG arancione': ('PETG orange', 'PETG orange'),
    'acciaio': ('steel', 'Stahl'),
    'acciaio A2': ('stainless steel A2', 'Edelstahl A2'),
    'ottone': ('brass', 'Messing'),
    'NBR70': ('NBR70', 'NBR70'),
    'PA nero': ('PA black', 'PA schwarz'),
    'PP-HT': ('PP-HT', 'PP-HT'),
    'acquistato': ('bought', 'gekauft'),
}


def tri(it, table, key):
    """{'en', 'it', 'de'} from the Italian text and a table of (English, German)."""
    if key not in table:
        sys.exit(f'publish_v6: no English/German text for {key!r}; add it to publish_v6.py')
    en, de = table[key]
    return {'en': en, 'it': it, 'de': de}


def reset(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def need(path):
    if not path.exists():
        sys.exit(f'publish_v6: missing {path.relative_to(V6)}; run build_v6.py first')
    return path


def publish_parts(names):
    """Copy print-ready STL, colour bodies and 3MF of each part; return the published paths per part."""
    files = {}
    for name in names:
        out = {'stl': f'stl/{name}.stl', '3mf': f'3mf/{name}.3mf'}
        shutil.copy2(need(BUILD / f'{name}_print.stl'), V6 / out['stl'])
        shutil.copy2(need(BUILD / f'{name}_print.3mf'), V6 / out['3mf'])
        colours = sorted(BUILD.glob(f'{name}_print_*.stl'))
        if colours:
            out['stl_colours'] = []
            for f in colours:
                colour = f.stem[len(f'{name}_print_'):]
                dst = f'stl/{name}_{colour}.stl'
                shutil.copy2(f, V6 / dst)
                out['stl_colours'].append(dst)
        files[name] = out
    return files


def publish_viewer():
    man = json.loads(need(BUILD / 'v6_viewer.json').read_text(encoding='utf-8'))
    parts, seen = [], {}
    for p in man['parts']:
        if p['id'] in DROP_FROM_VIEWER:
            continue
        src = Path(p['file'])
        if not src.is_absolute():
            src = BUILD / src
        if src.name in seen and seen[src.name] != src:
            sys.exit(f'publish_v6: two viewer meshes are both called {src.name}')
        seen[src.name] = src
        shutil.copy2(need(src), V6 / 'assembly' / src.name)
        q = dict(p, file=src.name, name=tri(p['name'], NAMES, p['id']))
        q['material'] = tri(p['material'], MATERIALS, p['material'])
        parts.append(q)
    man.update(title=TITLE, subtitle=SUBTITLE, status_short=STATUS_SHORT, status=STATUS, parts=parts,
               groups={g: GROUPS[g] for g in man['groups']})
    (V6 / 'assembly/v6_viewer.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(parts)


def main():
    doc = json.loads(need(BUILD / 'v6.json').read_text(encoding='utf-8'))
    v6_parts = [k for k in doc['files'] if k not in NOT_PARTS]
    for sub in ('stl', '3mf', 'assembly'):
        reset(V6 / sub)
    files = publish_parts(v6_parts)
    reused = publish_parts(REUSED)
    n_view = publish_viewer()
    shutil.copy2(need(BUILD / 'check_v6.png'), CAD / 'check_v6.png')
    doc['status'] = STATUS
    doc['files'] = files | {'assembly': 'assembly/', 'viewer': 'assembly/v6_viewer.json', 'check': 'cad/check_v6.png',
                            'note': 'paths relative to hardware/v6/; stl/ and 3mf/ are print-ready, assembly/ is at the assembled position'}
    doc['files_reused_parts'] = reused
    (CAD / 'v6.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    n = sum(1 for d in ('stl', '3mf', 'assembly') for f in (V6 / d).iterdir())
    print(f'published v6: {len(v6_parts)} new parts, {len(REUSED)} reused parts, {n_view} viewer meshes, {n} files '
          f'in stl/, 3mf/ and assembly/, plus cad/v6.json and cad/check_v6.png')


if __name__ == '__main__':
    main()
