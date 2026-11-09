"""Plate plan for Kibble Dispenser Outdoor v6 on a Bambu Lab A1 (+ AMS lite).

Grouping rule: a part's body colour runs through its whole height, so two body colours on one plate
cost a filament swap on every layer. Plates are therefore grouped by body colour; the multicolour
parts only add swaps in their 3 inlay layers (0.6 mm) at the bottom or top.
"""

# Prime tower (A1 default width 35 mm + 3 mm brim). Reserved keep-out per multicolour plate.
TOWER_W = 35.0
TOWER_KEEPOUT = (45.0, 45.0)   # reserved square, tower lower-left corner placed 4 mm inside it

PLATES_PETG = [
    dict(key='PETG-0', name='00 TEST - spline + cover groove', parts=[('test_scanalato', 1), ('test_groove_fondello', 1)],
         tower=False,
         purpose='print first: pick the spline clearance for mozzo_v6 and check the TPU lip strip in the groove'),
    dict(key='PETG-1', name='01 BLACK - bowl + box + shaft + hub', parts=[('chiocciola_v6', 1), ('scatola_v6', 1), ('albero_v6', 1), ('mozzo_v6', 1)],
         tower=False, purpose='single colour (black); the two big supported parts; shaft at 0.15 mm layers needs a plate without prime tower'),
    dict(key='PETG-2', name='02 BLACK+orange - flange + cover + tower', parts=[('flangia_piano_v6', 1), ('fondello_v6', 1), ('colonna_v6', 1)],
         tower=True, purpose='black body; orange cover inlays only in the first 3 layers'),
    dict(key='PETG-3', name='03 GREEN+black - chute + collar + gate + window plates', parts=[('scivolo_v6', 1), ('colletto_v6', 1), ('piastra_finestra_v4b', 1), ('piastra_gate_v4b', 1)],
         tower=True, purpose='food path: green parts + the two 3 mm plates (black body, green bands)'),
    dict(key='PETG-4', name='04 ORANGE+black - disc + latch + 4 buttons', parts=[('disco_v6', 1), ('linguetta_sicura', 1), ('nottolino_v6', 4)],
         tower=True, purpose='orange parts; black disc label only in the first 3 layers'),
]

PLATES_TPU = [
    dict(key='TPU-0', name='00 TEST - TPU lip seal strip', parts=[('test_lip_strip', 1)], tower=False,
         purpose='print first: check lip shape, fit in the groove coupon, deflection'),
    dict(key='TPU-1', name='01 TPU 95A - all seals', parts=[('guarnizione_baionetta', 1), ('guarnizione_piano_v5', 1), ('guarnizione_fondello_v6', 1),
                                                         ('labbro_uscita_1', 1), ('labbro_uscita_2', 1), ('labbro_finestra_1', 1), ('labbro_finestra_2', 1)],
         tower=False, purpose='all 7 TPU pieces, external spool'),
]

# Alternative documented in the guide: split PETG-3 into green-only + black/green plates (fewer swaps, one more plate).
