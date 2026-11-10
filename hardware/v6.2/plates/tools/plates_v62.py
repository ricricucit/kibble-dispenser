"""Plate plan for Kibble Dispenser Outdoor v6.2 on a Bambu Lab A1 (+ AMS lite).

Same rule as before: group by body colour (a body colour runs through the whole height); multicolour parts
only add swaps in their inlay layers. v6.2 adds a second d180 flange plate, an orange d176 interlock ring and
black cable-channel parts, so black needs four plates; the disc prints inside the interlock ring.
"""
TOWER_W = 35.0
TOWER_KEEPOUT = (45.0, 45.0)

PLATES_PETG = [
    dict(key='PETG-0', name='00 TEST - spline + rim, cap and skirt grooves',
         parts=[('test_scanalato', 1), ('test_groove_rim', 1), ('test_groove_cap', 1), ('test_groove_skirt', 1)],
         tower=False, purpose='print first: spline clearance for mozzo_v6; groove coupons for the TPU test strips'),
    dict(key='PETG-1', name='01 BLACK - pod shell + electronics box', parts=[('guscio_v611', 1), ('scatola_v62', 1)],
         tower=False, purpose='single colour (black); shell with brim; box with the IP66 settings and one support enforcer (C cup)'),
    dict(key='PETG-2', name='02 BLACK - bowl + pod cap', parts=[('chiocciola_v62', 1), ('fondello_v62', 1)],
         tower=False, purpose='single colour (black); bowl lugs and cap bottom edge on bed-only supports'),
    dict(key='PETG-3', name='03 BLACK - lower flange + cable channel',
         parts=[('flangia_piano_v62', 1), ('canalina_base_v62', 2), ('canalina_coperchio_v62', 2), ('canalina_tappo_v62', 1)],
         tower=False, purpose='single colour (black); the lower flange plate (pivot pin as a dowel) and all cable-channel parts'),
    dict(key='PETG-4', name='04 BLACK - upper flange + tower + shaft + hub',
         parts=[('flangia_alta_v62', 1), ('colonna_v62', 1), ('albero_v6', 1), ('mozzo_v6', 1)],
         tower=False, purpose='single colour (black); the shaft at 0.15 mm layers needs a plate without prime tower'),
    dict(key='PETG-5', name='05 GREEN+black - chute + collar + gate + window plates',
         parts=[('scivolo_v611', 1), ('colletto_v6', 1), ('piastra_finestra_v62', 1), ('piastra_gate_v62', 1)],
         tower=True, purpose='food path: green parts + the two 3 mm plates (black body, green bands)'),
    dict(key='PETG-6', name='06 ORANGE+green+black - interlock ring + disc + gate blade + latch + button + 3 thumb-turns',
         parts=[('anello_saracinesca_v62', 1), ('disco_v61', 1), ('saracinesca_v62', 1), ('linguetta_sicura', 1),
                ('pulsante_v611', 1), ('nottolino_v611', 3)],
         tower=True, purpose='orange parts; the disc prints inside the ring; the gate blade (green, orange arm) adds swaps in its 15 layers'),
]

PLATES_TPU = [
    dict(key='TPU-0', name='00 TEST - rim, cap, skirt and comb lips',
         parts=[('test_rim_lip', 1), ('test_cap_lip', 1), ('test_skirt_lip', 1), ('test_comb_lip', 1)],
         tower=False, purpose='print first: the thin TPU flaps (0.5 rim, 0.5 skirt, comb slits, cap lip)'),
    dict(key='TPU-1', name='01 TPU 95A - all seals',
         parts=[('labbro_ombra_v611', 1), ('guarnizione_baionetta_v61', 1), ('guarnizione_piano_v5', 1), ('labbro_scivolo_v611', 1),
                ('guarnizione_fondello_v61', 1), ('labbro_pettine_v62', 4), ('passacavo_v62', 1)],
         tower=False, purpose='all 10 TPU pieces, external spool'),
]
