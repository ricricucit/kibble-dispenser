"""Write print_v64/PRINT_GUIDE.md from summary.json: a step-by-step print procedure (numbers stay in sync with the slicer run)."""
import json
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/v6.4/plates
S = json.load(open(os.path.join(OUT, 'summary.json')))
P = {p['key']: p for p in S['plates']}
T = S['totals']


def g(v):
    return f'{v:.0f} g' if v >= 10 else f'{v:.1f} g'


def tag(p):
    return {'unchanged': 'UNCHANGED since 6.3.0', 'changed': 'CHANGED in 6.4', 'new': 'NEW in 6.4'}[p['status']]


# per-plate text: load / check before printing / supports / look at the finished parts / post-processing
STEPS = {
    'PETG-1': dict(
        load='PETG black in AMS slot 1.',
        check=['Object guscio_v64: 5 walls, 15 % infill, outer brim 6 mm.',
               'Support: enabled, type "tree (manual)", "On build plate only" ticked, threshold angle 45. The object holds three small '
               '"support enforcer" boxes, one under each bowl tab.',
               'After slicing, the preview must show exactly three support trees. They stand on the plate inside the shell and end under '
               'the three tabs at Z 64 mm. Nothing else has support (the button boss and the ribs print without).',
               'If your slicer shows no trees: set the support type to "tree (auto)", keep "On build plate only" and 45 degrees, and '
               'slice again.'],
        supports='Tree, from the build plate only, 45 degrees, under the inner 12 mm of the three bowl tabs. The outer part of each '
                 'tab rests on its own 45 degree corbel.',
        inspect=['The underside of the three tabs is flat and closed (this face sits on the bowl).',
                 'The module opening (the big notch in the wall): the cut edges are blunt, not feathered. A slightly rough start of the '
                 'two return ribs is normal.',
                 'The round bore for the latch button and its O-ring groove are clean.'],
        post=['Break the three support trees out with pliers and scrape the tab faces flat.',
              'Peel the brim off and deburr that edge with a knife (it is a visible edge).']),
    'PETG-2': dict(
        load='PETG black in AMS slot 1.',
        check=['Object chiocciola_v63: 3 walls, 15 % infill.',
               'Support: "tree (auto)", "On build plate only" ticked.'],
        supports='Tree, from the build plate only, under the 3 bayonet lugs.',
        inspect=['The rim groove (3.0 x 2.2 mm) is clean all round: the rim lip seal goes there.',
                 'The three bayonet lugs are solid and their undersides are closed.'],
        post=['Remove the supports under the lugs.',
              'Melt 3 M3 heat-set inserts into the three stack holes (P1, P2, P3). Soldering iron at 230 to 240 C, push straight, stop '
              'flush or 0.2 mm below the surface, let it cool before you touch it.',
              'Do not drill the small 2.5 mm holes for the chute ears and the shell tabs: they are pilots for the PT screws.']),
    'PETG-3': dict(
        load='PETG black in AMS slot 1.',
        check=['Lower flange plate: 3 walls, 25 % infill. Tower: 4 walls, 100 % infill. Hub: 4 walls, 100 % infill.',
               'Shaft (albero_v6): layer height 0.15 mm, 100 % infill, 5 mm brim. This is why the plate has no prime tower.'],
        supports='None.',
        inspect=['Lower flange plate: flat (lay it on a table), the skirt groove is clean, the 4.0 mm dowel hole is round.',
                 'Shaft: both O-ring grooves are clean, the hex and the spline are sharp.',
                 'Hub: it fits the servo spline like the coupon you chose in step 1.'],
        post=['Press the 4 x 6 mm steel dowel into the 4.0 x 2.7 mm hole of the lower flange plate. Use a vice or light hammer taps, keep it '
              'square. It must stand 3.3 mm proud.',
              'Peel the brim off the shaft and deburr its foot.']),
    'PETG-4': dict(
        load='PETG black in AMS slot 1.',
        check=['Upper flange plate: 3 walls, 25 % infill.'],
        supports='None.',
        inspect=['The plate is flat. The three press-fit pins are round and not stringy.',
                 'The cable-tie window is open.'],
        post=['Test the three pins in the holes of the lower plate: they must go in with firm hand pressure. Do not press them home yet.',
              'If a corner of this 180 mm plate lifted, print it again with an outer brim of 5 mm on the object (it prints alone, so the '
              'brim fits).']),
    'PETG-5': dict(
        load='PETG black in slot 1 and PETG green in slot 3.',
        check=['Prime tower enabled (position stored in the project).',
               'Chute: 5 walls, 15 %. Gate blade: 100 % infill, green only. Collar and the two plates: 3 walls, 15 %.'],
        supports='None.',
        inspect=['The green bands on the gate plate (OUT, top side) and the window plate (FOOD IN, bed side) are readable.',
                 'The gate blade is flat and slides freely on the gate plate.',
                 'Collar: the two small 3 x 3 mm pads are attached (in the model they sit 0.1 mm above the body). If one comes off, fix it '
                 'with a drop of cyanoacrylate glue.'],
        post=['Throw the prime tower away. No drilling.']),
    'PETG-6': dict(
        load='PETG black in slot 1 and PETG orange in slot 2.',
        check=['Prime tower enabled. Interlock ring: 4 walls, 15 %, outer brim 5 mm. Disc: 3 walls, 15 %. Latch and button: 100 % infill.',
               'Latch (linguetta_sicura_v63): support "normal (auto)", "On build plate only".'],
        supports='A small bed-only support under the spring tab of the latch. Nothing else.',
        inspect=['The disc label (black, bed side) is readable. The disc pockets are clean.',
                 'The teardrop window of the ring is open and its top is closed without sagging strings.',
                 'The spring tab of the latch flexes and springs back.'],
        post=['Peel the brim off the ring. Remove the small support under the latch tab.']),
    'PETG-7': dict(
        load='PETG black in AMS slot 1. This project has its own filament settings (see the first check).',
        check=['Filament: "Generic PETG @BBL A1" shown as modified. Part cooling fan: minimum 20 %, maximum 40 %; overhang fan threshold 25 %. '
               'Nozzle 255 C. Leave these as they are. With a branded PETG, pick its profile and set the same fan values.',
               'Both objects: 5 walls, line width 0.42 mm, 100 % infill, 5 top and 5 bottom layers, seam "back", flow ratio 1.03.',
               'Servo bay (scatola_v64): ironing "top surfaces". Cap (fondello_v64): elephant foot compensation 0.15 mm.',
               'Support: off for both objects.'],
        supports='None. The slicer gives no warning for this plate (the 6.4 CAD fixes for the bay posts, the harness lug, the C-hook and '
                 'the cap bottom edge work).',
        inspect=['Servo bay: the two holder posts are straight and solid from the roof to their ends. They carry the electronics module.',
                 'Servo bay: the rim face (ironed, on top while printing) is smooth and closed all round. The cap lip seals on it.',
                 'Servo bay: hold it against a bright lamp in a dark room. No light may shine through the walls.',
                 'Servo bay: the pad around the 12 mm cable-gland hole is flat (lay a steel rule on it).',
                 'Servo bay: the small lug bar beside cap boss D (for the harness cable tie) and the C-hook on top of the south post '
                 '(3.8 mm slit) are complete and not cracked.',
                 'Cap: the bottom edge (45 degree chamfer, then the radius) is smooth with no curled layers.',
                 'Cap: the lip-seal groove (2.2 x 1.15 mm) on the upstand is clean.',
                 'Cap: inside the round well, the 1.5 mm ring that holds the chute lip prints as a short overhang at Z 29.3 mm (its inner edge '
                 'is now a 45 degree chamfer). A slightly rough underside there is normal; scrape off any loose strings so the lip seats.'],
        post=['Cap: push a 1.5 mm drill by hand through the 2 drain holes. Check the three 0.8 mm slits next to them with a blade.',
              'Servo bay: melt 4 M3 inserts into the servo cradle and 2 into the ends of the two holder posts (4.0 x 6.5 mm holes; the post '
              'ends point up as printed). 230 to 240 C, straight, flush. Hold the post while it cools so it stays straight.',
              'Servo bay: clear the 2 mm vent hole with a 2 mm drill and stick the ePTFE vent patch over it (clean, dry surface).',
              'Servo bay: try the M12 gland in its hole and file the top of the hole if it is tight. Check that the harness tail (d4.5) '
              'snaps into the C-hook and that a 2.5 mm cable tie passes round the lug bar.',
              'Do not drill the screw holes in the bay bosses: they are 2.5 mm pilots for the PT K30x12 cap screws.']),
    'TPU-1': dict(
        load='TPU 95A on the external spool holder. In the print dialog choose "External spool" (the AMS lite cannot feed TPU).',
        check=['Filament "Generic TPU @BBL A1". All parts: 2 walls, 100 % infill.',
               'Thin lips (rim seal, skirt lip, chute lip, 4 comb lips): wall generator "Arachne", wall speed 15 mm/s.'],
        supports='None.',
        inspect=['Every flap is one continuous line with no gaps or blobs, and it springs back when you bend it.',
                 'The slits of the 4 comb lips are open.',
                 'Strings and bubbles mean wet TPU: dry it again and reprint.'],
        post=['Trim strings with scissors. Do not pull on the flaps.']),
    'TPU-2': dict(
        load='TPU 95A on the external spool holder ("External spool").',
        check=['Cap lip seal (guarnizione_fondello_v64): 2 walls, 100 %, wall speed 20 mm/s.',
               'Module gasket (modulo_guarnizione_v64): wall generator "Arachne", wall speed 15 mm/s.'],
        supports='None.',
        inspect=['Both rings are closed loops with a clean, continuous lip.',
                 'The cap lip seal presses into the groove of the cap upstand and stays there.',
                 'The module gasket presses into the groove on the underside of the module lid (a light press fit).'],
        post=['Trim strings with scissors.']),
    'MOD-1': dict(
        load='PETG black in AMS slot 1. This project has the same low-fan filament settings as the sealed chassis parts.',
        check=['Filament: "Generic PETG @BBL A1" shown as modified. Fan minimum 20 %, maximum 40 %, overhang fan threshold 25 %, nozzle 255 C.',
               'Tub (modulo_vasca_v64): 5 walls, line width 0.42 mm, 100 % infill, seam "back", flow ratio 1.03, elephant foot compensation 0.15 mm.',
               'Tub support: enabled, type "normal (manual)", "On build plate only" not ticked, threshold 45. The object holds 2 small '
               '"support enforcer" boxes at the button recess and 2 mouse ears (thin discs, part of the object) at the back corners.',
               'After slicing, the preview shows exactly two thin support columns. They stand on the plate just outside the panel face and '
               'end at Z 21.5 mm under the two upper corners of the 17 mm button recess. Nothing else has support.',
               'Speaker ring: 3 walls, 100 % infill. It may be any colour (it sits inside the sealed module).'],
        supports='Two thin columns (about 0.5 g) under the two upper corners of the button recess, where the recess rim meets the leaning '
                 'skin and starts in free air. The bottom edge, the rim and the 5 lid-screw bosses need none (45 degree faces; the bosses '
                 'grow on corbels from the wall).',
        inspect=['Lay a steel rule on the flat back wall (2 mm thick, 104 x 67 mm). A bow of more than about 0.3 mm will close the 0.35 mm '
                 'seam to the cap: print again, drier filament and no draught.',
                 'The top face of the tub rim (the land) is smooth and unbroken all round. The lid gasket seals on it.',
                 'The 5 bosses and their corbels are solid and the 2.5 mm pilot holes are open.',
                 'Hold the tub against a bright lamp in a dark room: no light through the walls. The three knock-out marks stay closed.',
                 'Slide a 50 x 70 mm perfboard into slot A from the top. It must go down to the floor of the slot without force.',
                 'The two round sockets at the back corners (10 mm) slide onto the 9 mm posts of the servo bay.'],
        post=['Break the two support columns off the button recess and scrape both corners clean (the button gasket seats in the recess).',
              'Cut the two mouse ears off flush and restore the small 0.4 mm chamfer on the bottom back edge with a knife.',
              'Ream the two light-pipe holes with a 5.1 mm drill by hand (horizontal holes sag at the top).',
              'Clear the 7 speaker grille holes in the floor with a 1.5 mm drill.',
              'Check that the 12 mm push-button fits its 17 mm recess. Do not drill the 5 boss holes (PT K30x10 pilots).',
              'Before electronics go in: close the module (gasket, lid, 5 screws with O-rings, button, light pipes, J1 socket) and hose it. '
              'About 105 mm of the gasket along the back edge has no screw, so this water test is required.']),
    'MOD-2': dict(
        load='PETG black in AMS slot 1 (same project, plate 2).',
        check=['Before you print: take the M8 5-pin panel socket you bought. Measure its thread and its nut. The lid is made for a hole of '
               '8.2 mm and a nut up to 13 mm across flats (bore 16.5 mm). If your socket differs, stop and ask for a changed lid.',
               'Lid: 5 walls, line width 0.42 mm, 100 % infill, seam "back", flow ratio 1.03. Support: off.'],
        supports='None. The J1 hole is closed on top by a skin of one layer (0.2 mm) so the turret roof prints as a 13 mm bridge.',
        inspect=['The gasket groove on the underside is clean. Its outer wall is only 1.2 mm thick: handle it with care.',
                 'The turret roof is closed and flat on the inside (this is the nut seat).',
                 'The ribs and the back fence on the top face are complete (the harness loop lies between the fence and the turret).'],
        post=['Drill the skin of the J1 hole: push an 8.2 mm drill by hand from the underside through the existing hole (the hole guides '
              'the drill). Use the thread size of your socket if it differs. Deburr the nut seat.',
              'Leave the USB-C mark on the top closed.',
              'For a development module that will be opened often: melt 5 M3 inserts into the tub bosses instead of using PT screws.']),
    'MOD-TPU-1': dict(
        load='TPU 95A on the external spool holder ("External spool").',
        check=['Wall generator "Arachne", wall speed 15 mm/s, 2 walls, 100 % infill.'],
        supports='None.',
        inspect=['A closed loop with a clean, continuous lip.'],
        post=['Trim strings with scissors.']),
}
ORDER = ['PETG-1', 'PETG-2', 'PETG-3', 'PETG-4', 'PETG-5', 'PETG-6', 'PETG-7', 'TPU-1', 'TPU-2', 'MOD-1', 'MOD-2', 'MOD-TPU-1']

lines = []
A = lines.append


def plate_facts(p):
    def extra(v):
        e = [f"{lab} {v[k]} g" for k, lab in (('support', 'support'), ('prime_tower', 'prime tower'), ('flush', 'flush')) if v[k] > 0.05]
        return f" (of which {', '.join(e)})" if e else ''
    fil = '; '.join(f"{k} {g(v['grams'])}{extra(v)}" for k, v in p['est_grams_per_filament'].items())
    A(f"- File: `{p['bambu_project']}`, plate {p['plate_in_project']}. Other slicers: `{p['plain_3mf']}`. Picture: `{p['preview_top']}`.")
    A('- Parts on the plate:')
    for pp in p['parts']:
        A(f"  - {pp['id']} x{pp['qty']}: {pp['label']} ({pp['material']} {' + '.join(pp['colours'])}; {pp['status_label']})")
    A(f"- Time and filament: {p['est_time_hm']}; {fil}; colour swaps: {p['colour_swaps']}.")
    if p['prime_tower_xy_mm']:
        A(f"- Prime tower at X {p['prime_tower_xy_mm'][0]:.0f}, Y {p['prime_tower_xy_mm'][1]:.0f}.")
    if p['slicer_warning']:
        A(f"- Slicer warning on this plate: {p['slicer_warning']}")


A('# Kibble Dispenser Outdoor 6.4 - print procedure (Bambu Lab A1 + AMS lite)')
A('')
A('Follow the steps in order. Each step is one plate: what to load, what to check in the slicer, the supports, the time and the '
  'filament, what to look at on the finished parts, and the work to do on them before assembly.')
A('')
A('Hardware 6.4 is two products:')
A('')
A('- **Chassis 6.4**: the dispenser itself with the servo bay and the holder for the electronics module.')
A('- **Electronics module, case 1.0**: a sealed case (tub, lid, speaker ring, lid gasket) that slides into the chassis from below. '
  'It has its own files, so you can print it again later without touching the chassis.')
A('')
A('Every plate and every part is marked **UNCHANGED since 6.3.0**, **CHANGED in 6.4** or **NEW in 6.4**.')
A('')
A('## If you already started with the 6.3 package (print_v63)')
A('')
A('The 21 unchanged part files are byte-identical to 6.3.0, and their plates here have the same parts at the same positions with the same '
  'settings. Parts you already printed from print_v63 stay valid.')
A('')
A('- Keep: everything from print_v63 plates PETG-3, PETG-4, PETG-5 and PETG-6, the bowl from PETG-2, the test pieces from PETG-0 and '
  'TPU-0, and all seals from TPU-1 except the cap lip seal.')
A('- Throw away (obsolete 6.3 parts): the shell guscio_v611 and the electronics box scatola_v63 (print_v63 PETG-1), the cap '
  'fondello_v63 (print_v63 PETG-2) and the cap lip seal guarnizione_fondello_v61 (print_v63 TPU-1).')
todo = S['to_print_if_print_v63_is_done']
A(f"- Still to print: {', '.join(todo['plates'])}. That is {todo['totals']['time_hm']} of printing, "
  f"{g(todo['totals']['grams_PETG'])} of PETG and {g(todo['totals']['grams_TPU'])} of TPU.")
A('- In the steps below, skip a plate marked UNCHANGED when you already have its parts.')
A('')
A('Slicer check of "same as print_v63" (grams, time and layers of the sliced plate):')
for k, v in S['unchanged_plates_vs_print_v63'].items():
    if v['identical_slice']:
        A(f"- {k}: identical to print_v63 {v['print_v63_plate']} ({g(v['grams_v64'])}, {v['time_min_v64']:.0f} min, {v['layers_v64']} layers).")
    else:
        A(f"- {k}: same positions as print_v63 {v['print_v63_plate']}, with the obsolete 6.3 part removed "
          f"({g(v['grams_v63'])} -> {g(v['grams_v64'])}, {v['time_min_v63']:.0f} -> {v['time_min_v64']:.0f} min).")
A('')
A('## Files')
A('')
A('Chassis:')
A('- `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`: plates PETG-0 to PETG-6 (plate numbers as in print_v63). Three colours from the AMS lite.')
A('- `Kibble_Dispenser_v64_chassis_IP66_PETG.bambu.3mf`: plate PETG-7, the two sealed chassis parts (servo bay, cap), black, with '
  'low-fan filament settings stored in the project.')
A('- `Kibble_Dispenser_v64_chassis_TPU.bambu.3mf`: TPU-0 (test), TPU-1 (unchanged seals), TPU-2 (the two 6.4 seals).')
A('')
A('Electronics module, case 1.0:')
A('- `Kibble_Module_case_1.0_PETG.bambu.3mf`: MOD-1 (tub and speaker ring), MOD-2 (lid), black, low-fan filament settings.')
A('- `Kibble_Module_case_1.0_TPU.bambu.3mf`: MOD-TPU-1, the lid gasket alone. Use it only when you reprint the module later: the same '
  'gasket is already on chassis plate TPU-2.')
A('')
A('Also in this folder:')
A('- `plates/*.3mf`: one plain 3MF per plate for other slicers. They carry no settings, supports or enforcers: set them by hand from the steps below.')
A('- `stl/*_print.stl`: every part alone in print orientation. Two-colour parts also come as colour bodies.')
A('- `preview/<plate>_top.png` and `<plate>_iso.png`: pictures of each plate. `summary.json`: all numbers as data. `layout.json`: part positions. '
  '`slice_check/`: slicer statistics. `tools/`: the scripts that made all of this (`tools/run_all.sh`).')
A('')
A('## Step 0: before the first print')
A('')
A('1. Filament. You need about:')
for k, v in T['grams_per_filament'].items():
    A(f'   - {k}: {g(v)}')
A(f"   - That is {g(T['grams_PETG'])} of PETG and {g(T['grams_TPU'])} of TPU for everything, test plates included. Black is "
  f"{T['grams_per_filament'].get('PETG black', 0) / max(T['grams_PETG'], 1) * 100:.0f} % of the PETG, so keep a second black spool ready.")
A('2. Dry the filament. PETG from an open spool: 65 C for 6 to 8 hours. TPU: 65 to 70 C for 6 to 8 hours right before printing, every '
  'time. Wet TPU makes strings and bubbles and the thin sealing lips fail.')
A('3. Load the AMS lite: slot 1 PETG black, slot 2 PETG orange, slot 3 PETG green, slot 4 the spare PETG black. In the AMS settings turn on '
  '"Filament backup" so slot 4 takes over when slot 1 runs out.')
A('4. TPU does not go through the AMS lite. For the TPU plates, feed it from the external spool holder and choose "External spool" in the print dialog.')
A('5. Build plate: Textured PEI. Wash it with dish soap and warm water, dry it, and do not touch the surface. Bed 80 C for PETG, 45 C for TPU '
  '(set by the profiles).')
A('6. Open a project in Bambu Studio. Check: printer "Bambu Lab A1 0.4 nozzle", plate type "Textured PEI Plate", process "0.20mm Standard @BBL A1", '
  'and the filament colours in the right slots. Slice the plate once and look at the preview before you send it.')
A('7. Keep "Bed levelling" and "Flow dynamics calibration" ticked in the print dialog.')
A('8. Tools for the work after printing: flush cutters, long-nose pliers, a deburring knife, drills 1.5, 2.0, 5.1 and 8.2 mm (turned by hand), '
  'a soldering iron with an M3 insert tip, a small vice or hammer, a steel rule, calipers.')
A('')
A('Colour language: black is structure, orange is a touch point, green is the food path, yellow TPU is a seal.')
A('')
A('## Step 1: test coupons (PETG-0, then TPU-0)')
A('')
p = P['PETG-0']
A(f"### Step 1a - PETG-0: {p['name']} [{tag(p)}]")
A('')
plate_facts(p)
A('- Load: PETG black in AMS slot 1. Supports: none. Nothing to change in the settings.')
A('- How to judge the spline test (test_scanalato, 3 coupons with 1, 2 or 3 notches = 0.05, 0.10, 0.20 mm clearance):')
A('  - Push each coupon onto the servo output spline by hand.')
A('  - The right one goes on with firm thumb pressure, has no play when you twist it, and comes off again by hand.')
A('  - The hub (mozzo_v6) is built like the coupon with 2 notches. If 2 notches fits, go on.')
A('  - If only the coupon with 1 or 3 notches fits, stop before PETG-3 and ask for a hub with that clearance (SPL_CLEAR in parts/build_drivetrain.py).')
A('- How to judge the three groove coupons (bowl rim, cap upstand, flange skirt):')
A('  - The grooves are open and clean down to the bottom, with no blobs.')
A('  - Measure the cap coupon wall with calipers: it should be 4.4 mm thick. More than 4.6 mm means too much flow: run the flow '
  'calibration for this filament before the sealed parts.')
A('  - Keep the coupons for step 1b.')
A(f"- Status note: {p['status_note']}.")
A('')
p = P['TPU-0']
A(f"### Step 1b - TPU-0: {p['name']} [{tag(p)}]")
A('')
plate_facts(p)
A('- Load: dried TPU 95A on the external spool. Supports: none.')
A('- How to judge:')
A('  - Each flap is one clean, continuous line: no gaps, no blobs, no hairs. It springs back when you bend it flat.')
A('  - Press each strip into its groove coupon with your thumb (rim lip into the rim coupon, cap lip into the cap coupon, skirt lip into '
  'the skirt coupon). The foot seats fully and stays in when you turn the coupon upside down.')
A('  - If a foot will not go in or falls out, do not print the big PETG parts yet: report which strip and which coupon.')
A('  - Comb lip: all slits are open. A sheet of paper passes through each slit.')
A('  - Strings between the parts or a rough, bubbly surface mean wet TPU. Dry it again and repeat this plate.')
A(f"- Status note: {p['status_note']}.")
A('')
A('## Steps 2 to 13: the plates')
A('')
n = 1
for key in ORDER:
    n += 1
    p = P[key]
    st = STEPS[key]
    prod = 'chassis' if p['product'] == 'chassis' else 'module case 1.0'
    opt = ' - only when the module is reprinted alone' if p.get('duplicate_of') else ''
    A(f"### Step {n} - {key}: {p['name'].split(' - ', 1)[-1].split(' (only')[0]} [{prod}; {tag(p)}]{opt}")
    A('')
    if p.get('duplicate_of'):
        A(f"Skip this step if you printed {p['duplicate_of']}: the module gasket is on that plate too.")
        A('')
    if p['status_note']:
        A(f"Status note: {p['status_note']}.")
        A('')
    plate_facts(p)
    A(f"- Load: {st['load']}")
    A('- Check in the slicer before printing:')
    for c in st['check']:
        A(f'  - {c}')
    A(f"- Supports: {st['supports']}")
    A('- Look at the finished parts:')
    for c in st['inspect']:
        A(f'  - {c}')
    A('- Work after printing:')
    for c in st['post']:
        A(f'  - {c}')
    A('')
    if key == 'TPU-2':
        A('The chassis is now complete. The next steps are the electronics module.')
        A('')

A('## Step 14: final checks before assembly')
A('')
A('1. Tick every part in the check list below.')
A('2. Press the rim lip seal into the bowl groove, the skirt lip into the lower flange plate and the cap lip seal into the cap. Each must '
  'seat all round.')
A('3. Push the cap onto the servo bay without screws: the cap lip touches the bay rim all round.')
A('4. Slide the empty module up into the chassis: it moves freely, the two sockets find the posts over the last 18 mm, and the seams to '
  'the cap and the shell are even (0.35 mm). Hold the module when it leaves the posts on the way out.')
A('5. Drive each PT screw by hand (about 0.6 N m) and open each PT joint at most 5 times. Tighten the M3x40 stack screws to 0.4 N m and '
  'the two M3x16 module screws to 0.5 N m.')
A('6. Hose-test the closed servo bay with the cap, and the closed module, before electronics go inside.')
A('')
A('## Totals')
A('')
for name, key in (('Chassis (PETG-0 to PETG-7, TPU-0, TPU-1)', 'chassis'), ('Module case 1.0 (MOD-1, MOD-2)', 'module')):
    t = S['products'][key]['totals']
    A(f"- {name}: {t['time_hm']}, PETG {g(t['grams_PETG'])}, TPU {g(t['grams_TPU'])}, {t['plates']} plates, {t['colour_swaps']} colour swaps.")
t = S['products']['shared_plate_TPU_2']
A(f"- Shared plate TPU-2 (cap lip seal + module gasket): {t['time_hm']}, TPU {g(t['grams_TPU'])}.")
A(f"- Everything: {T['time_hm']} over {T['plates']} plates, PETG {g(T['grams_PETG'])}, TPU {g(T['grams_TPU'])}, {T['colour_swaps']} colour swaps.")
r = S['products']['module']['totals_reprint_alone']
A(f"- Module reprinted alone later (MOD-1, MOD-2, MOD-TPU-1): {int(r['time_min'] // 60)} h {int(r['time_min'] % 60):02d} min, {g(r['grams'])}.")
A('- Times and grams are slicer estimates. They include supports, the prime tower and flushing.')
A('')
A('## Check list: all printed parts')
A('')
cc = S['cross_check']['count_print_v64']
A(f"Chassis: {cc['chassis']['PETG_parts']} PETG parts ({cc['chassis']['PETG_pieces']} pieces) and {cc['chassis']['TPU_pieces']} TPU pieces. "
  f"Module: {cc['module']['PETG_pieces']} PETG pieces and {cc['module']['TPU_pieces']} TPU piece. Plus {cc['test_pieces']} test pieces.")
A('')
for title, sel in (('Chassis', lambda c: c['kind'] == 'part' and c['product'] == 'chassis'),
                   ('Electronics module, case 1.0', lambda c: c['kind'] == 'part' and c['product'] == 'module'),
                   ('Test pieces', lambda c: c['kind'] == 'test')):
    A(f'### {title}')
    A('')
    for c in S['parts_checklist']:
        if not sel(c):
            continue
        mod = f"; sub-assembly: {c['kit_module']}" if c.get('kit_module') else ''
        stt = '' if c['kind'] == 'test' else f" [{c['status_label']}]"
        A(f"- [ ] {c['id']} x{c['qty']}: {c['label']}; {c['material']} {' + '.join(c['colours'])}; plate {', '.join(c['plates'])}{stt}{mod}")
    A('')
A('## Bought parts (not printed)')
A('')
for title, key in (('Chassis', 'chassis'), ('Electronics module, case 1.0', 'module')):
    A(f'### {title}')
    A('')
    for h in S['bought_parts']:
        if h['product'] == key:
            A(f"- [ ] {h['qty']} x {h['item']}: {h['use']}")
    A('')
A('Changes from 6.3: 9 heat-set inserts instead of 7 (2 new in the holder posts). 4 cap screws with O-rings instead of 3. One O-ring 3x1 on the '
  'stack (P2 only). No seam O-ring 132x2. An adhesive vent patch instead of the M12 vent. A chassis harness made from a cut M8 5-pin angled '
  'cordset, a round 3-core servo branch through the M12 gland with a JR female crimped on inside the bay (the servo and its flat lead are '
  'not cut), a 2-core 12 V branch, heat shrink over the splice and a 2.5 mm cable tie. The panel parts, the speaker and the electronics now '
  'belong to the module.')
A('')
A('Harness (lengths from v64.json interface.electrical_J1.harness):')
A('- Tail: cut the M8 5-pin male angled cordset to 190 mm from the plug body (cable exit) to the centre of the splice.')
A('- Servo branch: 100 mm of round 3-core cable from the splice through the gland; 12 mm inside the bay plus 40 mm spare so the JR pair '
  'can be pulled out under the bay with the cap off. Pass the stripped cable through dome nut, seal and gland body from outside, then '
  'crimp the 3 terminals (open-barrel crimper) and push them into the JR housing: signal, +6 V, GND. Tighten the dome nut to 2.5 N m.')
A('- 12 V branch: 90 mm from the splice up the inside of the shell to the pod-top M8 pair.')
A('- Splice: tail pin 1 to 12 V +, pin 3 to 12 V GND and servo GND, pin 2 to servo signal, pin 4 to servo +6 V, pin 5 not connected. '
  'Solder, cover with the d8 x 20 adhesive heat shrink.')
A('- Tie the tail round the lug bar of the servo bay (2.5 x 100 tie) and snap it into the C-hook on the south post. With the module in, '
  'the service loop lies on the lid between the back fence and the turret.')
A('')
A('## Notes and deviations')
A('')
A('- **Module tub**: the first 6.4 package needed 5 support columns under the lid-screw bosses. In the final 6.4.0 CAD the bosses grow from '
  'the wall on 45 degree corbels and those 5 enforcers are gone. With support off the slicer still reports "floating regions": the cause is '
  'the two upper corners of the 17 mm button recess, where the recess rim meets the leaning outer skin at print Z 21.5 mm (checked by '
  'slicing the tub in bands: below Z 20 and above Z 23 there is no warning). This package supports those two corners only. A CAD change '
  '(a 45 degree or teardrop top on the recess rim) would remove them.')
A('- **Sealed parts, filament settings**: v64.json asks for 245 to 250 C and a fan of 40 % or less. The Generic PETG profile already prints '
  'at 255 C, so the nozzle stays there. The fan is limited to 20 to 40 %. Bridges and overhangs steeper than about 28 degrees still get the '
  'profile overhang fan (90 %): the threshold was raised from 10 % to 25 % so the leaning outer skin of the tub prints with the low fan.')
A('- **Speaker ring colour**: the viewer shows it orange. It is inside the sealed module, so this package prints it black with the tub.')
A('- **Flange plates (unchanged plates PETG-3 and PETG-4)**: the reviewer could not rule out warping of the two 180 mm plates on an open '
  'printer. Their plates are kept exactly as in print_v63 (no brim). If a corner lifts, add an outer brim of 5 mm to that object.')
A('- **Mouse ears and brims**: shell 6 mm brim, interlock ring 5 mm brim, shaft 5 mm brim, tub 2 mouse ears. Nothing else has one.')
A('- **Test coupons**: the cap groove coupon and the cap lip strip are cut from the 6.4 parts. Their section and size are the same as in 6.3.')
A('- **Plain 3MF files** carry no settings, supports or enforcers (the tub mouse ears are in them as geometry).')
A('- The Bambu projects are generated by a script in the Bambu Studio project format (metadata `BambuStudio-02.05.00.00`). The settings come '
  f"from the Bambu system profiles ({S['validation']['bambu_profiles']}). Every plate was opened and sliced with the OrcaSlicer 2.5.0 command "
  'line, but not in Bambu Studio itself. After opening a project in Bambu Studio, check the plate list and the filament mapping and slice once.')
A('- **Final 6.4.0 CAD** (this package): tub bosses on corbels, zero-volume fins gone from all files, cap ledge partly chamfered, harness '
  'tie lug and C-hook on the servo bay, harness fence on the module lid. The 21 unchanged files are still byte-identical to 6.3.0.')
A('- Times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by 5 to 10 %.')
warn = S['review_checks']['all_slicer_warnings']
if warn:
    for w in warn:
        A(f"- Slicer warning ({w['project']}, plate {w['plate']}): {w['warning']}")
else:
    A('- Slicer warnings: none on any plate.')
A('')
open(os.path.join(OUT, 'PRINT_GUIDE.md'), 'w').write('\n'.join(lines) + '\n')
print('PRINT_GUIDE.md written,', len(lines), 'lines')
