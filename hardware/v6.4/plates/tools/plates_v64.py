"""Plate plan for Kibble Dispenser Outdoor hardware 6.4.0 on a Bambu Lab A1 (+ AMS lite).

Two products, each with its own Bambu projects, so the electronics module can be reprinted alone:
  chassis  PETG project (plates PETG-0..PETG-6, same plate numbers as print_v63), IP66 PETG project (PETG-7), TPU project
  module   "case 1.0": PETG project (MOD-1, MOD-2), TPU project (MOD-TPU-1)

Plates with from_v63=<key> take the part positions of that print_v63 plate (print_v63/layout.json), so the plates of the
21 unchanged parts are exactly the print_v63 plates. status: 'unchanged' (same parts, positions and settings as print_v63),
'changed' (holds a 6.4 chassis part), 'new' (module).
"""
import os

TOWER_W = 35.0
TOWER_KEEPOUT = (45.0, 45.0)
V63_LAYOUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'v6.3', 'plates', 'layout.json')   # 6.3.0 package

CH_PETG = [
    dict(key='PETG-0', name='00 TEST - spline + rim, cap and skirt grooves', from_v63='PETG-0', status='unchanged',
         parts=[('test_scanalato', 1), ('test_groove_rim', 1), ('test_groove_cap', 1), ('test_groove_skirt', 1)],
         tower=False, purpose='print first: spline clearance for mozzo_v6; groove coupons for the TPU test strips',
         status_note='same coupons as print_v63 PETG-0 (the cap coupon is now cut from the 6.4 cap: same groove section, same size). '
                     'If you printed and judged the 6.3 test plate, do not print it again'),
    dict(key='PETG-1', name='01 BLACK - pod shell 6.4', status='changed',
         parts=[('guscio_v64', 1)],
         tower=False, purpose='the 6.4 shell with the module opening; 6 mm brim; tree supports under the 3 bowl tabs only',
         status_note='replaces print_v63 PETG-1 (shell 6.1.1 + electronics box 6.3): both of those parts are obsolete'),
    dict(key='PETG-2', name='02 BLACK - bowl', from_v63='PETG-2', status='unchanged',
         parts=[('chiocciola_v63', 1)],
         tower=False, purpose='single colour (black); bowl lugs on bed-only supports',
         status_note='the bowl at its print_v63 position; print_v63 PETG-2 also held the 6.3 cap, which is obsolete: '
                     'if you printed that plate, keep the bowl and do not print this plate'),
    dict(key='PETG-3', name='03 BLACK - lower flange + tower + shaft + hub', from_v63='PETG-3', status='unchanged',
         parts=[('flangia_piano_v63', 1), ('colonna_v63', 1), ('albero_v6', 1), ('mozzo_v6', 1)],
         tower=False, purpose='single colour (black); the shaft at 0.15 mm layers needs a plate without prime tower'),
    dict(key='PETG-4', name='04 BLACK - upper flange', from_v63='PETG-4', status='unchanged', parts=[('flangia_alta_v63', 1)],
         tower=False, purpose='single colour (black); the second d180 plate cannot share a plate with another big part'),
    dict(key='PETG-5', name='05 GREEN+black - chute + collar + gate blade + gate + window plates', from_v63='PETG-5', status='unchanged',
         parts=[('scivolo_v611', 1), ('colletto_v6', 1), ('saracinesca_v63', 1), ('piastra_finestra_v62', 1), ('piastra_gate_v62', 1)],
         tower=True, purpose='food path and gate: green parts + the two 3 mm plates (black body, green bands)'),
    dict(key='PETG-6', name='06 ORANGE+black - interlock ring + disc + latch + button', from_v63='PETG-6', status='unchanged',
         parts=[('anello_saracinesca_v63', 1), ('disco_v61', 1), ('linguetta_sicura_v63', 1), ('pulsante_v611', 1)],
         tower=True, purpose='orange parts; the disc prints inside the ring; black disc label only in the first 3 layers'),
]
CH_IP66 = [
    dict(key='PETG-7', name='07 BLACK IP66 - servo bay + pod cap 6.4', status='changed',
         parts=[('scatola_v64', 1), ('fondello_v64', 1)],
         tower=False, purpose='the two sealed chassis parts; IP66 object settings and the low-fan filament settings of this project; no supports',
         status_note='replaces the electronics box of print_v63 PETG-1 and the cap of print_v63 PETG-2'),
]
CH_TPU = [
    dict(key='TPU-0', name='00 TEST - rim, cap, skirt and comb lips', from_v63='TPU-0', status='unchanged',
         parts=[('test_rim_lip', 1), ('test_cap_lip', 1), ('test_skirt_lip', 1), ('test_comb_lip', 1)],
         tower=False, purpose='print first: the thin TPU flaps (0.5 rim, 0.5 skirt, comb slits, cap lip)',
         status_note='same strips as print_v63 TPU-0 (the cap strip is cut from the 6.4 seal: same section, same size)'),
    dict(key='TPU-1', name='01 TPU 95A - seals unchanged since 6.3.0', from_v63='TPU-1', status='unchanged',
         parts=[('labbro_ombra_v611', 1), ('guarnizione_baionetta_v61', 1), ('guarnizione_piano_v5', 1), ('labbro_scivolo_v611', 1),
                ('labbro_pettine_v62', 4), ('passacavo_v63', 1)],
         tower=False, purpose='the 9 unchanged TPU pieces, external spool',
         status_note='print_v63 TPU-1 without the 6.1 cap lip seal (obsolete); all other pieces at their print_v63 positions. '
                     'If you printed print_v63 TPU-1, do not print this plate'),
    dict(key='TPU-2', name='02 TPU 95A - 6.4 seals: cap lip seal + module gasket', status='changed',
         parts=[('guarnizione_fondello_v64', 1), ('modulo_guarnizione_v64', 1)],
         tower=False, purpose='the only two TPU parts that are new in 6.4, on their own small plate'),
]
MOD_PETG = [
    dict(key='MOD-1', name='M1 BLACK IP66 - module tub + speaker ring', status='new',
         parts=[('modulo_vasca_v64', 1), ('modulo_anello_speaker_v64', 1)],
         tower=False, purpose='the sealed tub (pod skin, control panel, board slots) and the speaker ring; no supports; 2 mouse ears on the tub'),
    dict(key='MOD-2', name='M2 BLACK IP66 - module lid', status='new',
         parts=[('modulo_coperchio_v64', 1)],
         tower=False, purpose='the lid on its own plate: check the bought M8 socket (thread and nut size) before printing it'),
]
MOD_TPU = [
    dict(key='MOD-TPU-1', name='M3 TPU 95A - module gasket (only when the module is reprinted alone)', status='new',
         parts=[('modulo_guarnizione_v64', 1)], duplicate_of='TPU-2',
         tower=False, purpose='the module gasket alone, for reprinting the module later; it is also on chassis plate TPU-2'),
]

PROJECTS = [
    dict(id='chassis_PETG', product='chassis', material='PETG', file='Kibble_Dispenser_v64_chassis_PETG.bambu.3mf', plates=CH_PETG,
         title='Kibble Dispenser Outdoor 6.4 chassis - PETG', filaments='ams3',
         description='Kibble Dispenser Outdoor 6.4.0 chassis, PETG plates for Bambu Lab A1 + AMS lite (slot 1 black, 2 orange, 3 green)'),
    dict(id='chassis_IP66', product='chassis', material='PETG', file='Kibble_Dispenser_v64_chassis_IP66_PETG.bambu.3mf', plates=CH_IP66,
         title='Kibble Dispenser Outdoor 6.4 chassis - sealed parts (IP66)', filaments='black_ip66',
         description='Kibble Dispenser Outdoor 6.4.0 chassis, sealed parts (servo bay, cap): PETG black with the part fan limited to 40 %'),
    dict(id='chassis_TPU', product='chassis', material='TPU', file='Kibble_Dispenser_v64_chassis_TPU.bambu.3mf', plates=CH_TPU,
         title='Kibble Dispenser Outdoor 6.4 chassis - TPU', filaments='tpu',
         description='Kibble Dispenser Outdoor 6.4.0, TPU 95A plates (external spool); plate 3 holds the two 6.4 seals'),
    dict(id='module_PETG', product='module', material='PETG', file='Kibble_Module_case_1.0_PETG.bambu.3mf', plates=MOD_PETG,
         title='Kibble electronics module case 1.0 - PETG', filaments='black_ip66',
         description='Electronics module case 1.0 for Kibble Dispenser Outdoor 6.4+: tub, speaker ring, lid; PETG black, part fan limited to 40 %'),
    dict(id='module_TPU', product='module', material='TPU', file='Kibble_Module_case_1.0_TPU.bambu.3mf', plates=MOD_TPU,
         title='Kibble electronics module case 1.0 - TPU', filaments='tpu',
         description='Electronics module case 1.0: lid gasket, TPU 95A (external spool)'),
]
ALL_PLATES = [p for pr in PROJECTS for p in pr['plates']]
for pr in PROJECTS:
    for i, p in enumerate(pr['plates']):
        p['project'] = pr['id']
        p['product'] = pr['product'] if p['key'] not in ('PETG-0', 'TPU-0') else 'chassis'
        p['material'] = pr['material']
        p['plate_in_project'] = i + 1
