# Electronics module, case 1.0

**Version 1.0.0 (tag `case-v1.0.0`), fits hardware 6.4. Status: designed and checked in CAD only, not printed, assembled or tested.** Page: <https://ricricucit.github.io/kibble-dispenser/module/>

One sealed case that slides into the chassis from below. Its outer wall is the missing piece of the pod skin and carries the control panel; the lid on top carries the interface connector J1. Four printed pieces:

- `modulo_vasca_v64`: tub (outer skin with the control panel, board slots, lid-screw bosses, speaker collar), PETG black, about 90 g;
- `modulo_coperchio_v64`: lid with the J1 turret and the gasket groove, PETG black, about 16 g;
- `modulo_guarnizione_v64`: lip gasket of the lid, TPU 95A, about 1.2 g;
- `modulo_anello_speaker_v64`: speaker ring (for a Ø23 speaker), PETG, about 0.6 g.

Files in this folder, published by `hardware/v6.4/cad/publish_v64.py` from the same CAD run as the chassis:

- `parts/`: the four parts as exported by the CAD, at the assembled position (STL and 3MF). The print-ready files, oriented and on plates, are in the 6.4 print package: `hardware/v6.4/plates/` (projects `Kibble_Module_case_1.0_PETG.bambu.3mf` and `Kibble_Module_case_1.0_TPU.bambu.3mf`, plates MOD-1, MOD-2 and MOD-TPU-1, steps 11 to 13 of [PRINT_GUIDE.md](../../v6.4/plates/PRINT_GUIDE.md)).
- `interface/`: the dimensioned drawing of the interface between chassis and module (PDF, SVG, PNG).

All dimensions in mm, in the frame of the CAD: Z up, shaft axis at x = y = 0, Z = 0 at the underside of the bowl base. The numbers come from `hardware/v6.4/cad/v64.json` (`interface`, `module`).

## Interface to the chassis (fixed from hardware 6.4)

A new case must respect all of this; the chassis is not touched when the electronics change.

- **Opening** in the shell and the cap: the prism x ≥ 17.05, |y| ≤ 52.35 (104.7 wide), from the cap at z -104.0 … -72.6 up through the shell at z -72.0 … -36.5 (67.5 tall). Return ribs 2.0 × 6.0 at the cut edges.
- **Module envelope**: back face at x 17.4, width 104.0 (|y| ≤ 52.0), from z -104.0 to -37.0. The outer face is the pod skin inside the prism, flush; the control panel band is a module feature, not part of the interface.
- **Clearance**: 0.35 all round, top seam 0.5 (the posts are the vertical stop, the top seam stays open).
- **Top lip**: 4.0 high, 2.0 thick, behind the shell wall at z -37 … -33, 0.4 gap.
- **Corner notches** at the back: x 17.4 … 29.6, |y| 38.0 … 52.0, open above z -89.0 (room for the posts and their webs).
- **Posts** (on the servo bay): Ø9.0 at (24.0, ±45.5), z -89.0 … -30.0, M3 heat-set insert (Ø4.0 × 6.5 hole) in the lower end.
- **Sockets** (in the module): Ø10.0, z -89.0 … -71.5; the post ends stop on the socket floors.
- **Lock**: 2 × M3 × 16 ISO 4762 A2 from below, head seat at z -99.1, counterbore Ø6.5, hex 2.5, 0.5 N·m by hand. The screws stay with the module.
- **Insertion**: straight up, 67 mm of travel. The removal sweep is free all the way.
- **Sealing**: the module is sealed on its own (lid gasket on the tub land, panel parts, J1 and lid screws sealed); between module and chassis there is no seal, only the 0.35 mm seams, the top lip and the return ribs.
- **Keep-out above the lid**: z -37.0 … -10, x > 23.4 (J1 turret, angled plug and harness loop); the P3 stack-screw pad at (17.6, 14.0), r 6.0, down to z -36.0; behind the back face (x < 17.4) the cap upstand and the bay wall.

## Connector J1

- M8 5-pin A-coded panel socket (female), front mount, in a turret on the module lid at (45.0, -24.0), mating face at z -25.0, lid hole Ø8.2, turret bore Ø16.5 for the nut (10 to 13 mm across flats assumed: **verify on the bought part before printing the lid**).
- Pinout as specified for case 1.0:
  1. +12 V in (from the M8 connector in the pod top)
  2. servo PWM (3.3 V logic, 50 Hz)
  3. GND (12 V return and servo return)
  4. servo +6 V out (from the regulator in the module)
  5. spare
- M8 5-pin contacts are about 3 A: enough for a standard servo (stall about 2.5 A at 6 V). A stronger servo would need the 4-pin 4 A version plus the PWM on a separate M8.

## Chassis harness

Part of the chassis, described here because the module plugs into it:

- **Tail**: angled M8 5-pin male cordset, PUR Ø4.5 (a ready-made 0.5 m cordset, cut), 190 from the plug body to the centre of the Y splice. Parked as a service loop on the module lid (184.5 of path: over the south rim, north along the back fence, U-turn R 11.5, back and up into the plug), anchored with a 2.5 × 100 cable tie on the lug bar of the bay and guided by the C-hook on the south post. It lets the module down up to 120 (5 spare); lowering it 80 needs 145.5.
- **12 V branch**: 90 of 2-core PUR (or the pigtail of an M8 4-pin field connector) to the M8 IP67 pair in the pod top.
- **Servo branch**: 100 of round PUR 3 × 0.25 mm², Ø4.0, through the M12 gland into the servo bay, ending in a crimped JR/Futaba 3-pin female (signal, +6 V, GND); the servo plugs into it in the dry room of the bay.
- **Y splice**: soldered, under adhesive-lined heat shrink Ø8 × 20; tail pin 1 → 12 V +, 3 → GND of both, 2 → servo signal, 4 → servo +6 V, 5 not connected.
- **Service**: take the two lock screws out and let the module down; at 80 its top is 13 below the pod bottom and the plug ring is free in the hand. Refit: plug, lay the loop on the lid between the back fence and the turret, push up.

## Inside (generic, provisional)

**The inside of the case is generic. The board, its wiring and the firmware are a separate, evolving project: they are documented separately and are provisional** (bench notes: [docs/PROTOTYPE_BENCH.md](../../../docs/PROTOTYPE_BENCH.md); one-button firmware: [issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2); camera later: [issue #3](https://github.com/ricricucit/kibble-dispenser/issues/3)).

- Walls: skin 2.5, panel band 3.0, back 2.0, sides 2.5, floor 2.5, lid 3.2.
- Usable space: 60.8 high from the floor to the lid land (48.2 under the rim), 68.0 wide between the board guides (70.6 in the slots, 99.0 across the front lobes), 44.0 deep on the centre line at the top down to 20.0 at the bottom corners (the outer wall follows the pod), about 150 cm³ free.
- Two board slots for a 50 × 70 perfboard standing (70 across, 50 tall), sliding in from the top; board bottom edge at z -91.5. Slot A (board back face at x 22.4, 3.0 behind it for the pins) takes the green 5 × 7 cm board with the ESP32-WROVER on socket strips (stack about 61 × 28 × 25) and no extension board. Slot B (x 30.0) only when the stack on the board in A is at most 6.0 (12.8 to 19.2 in front of B).
- Speaker Ø20 to Ø24 in a printed ring on the floor collar (this ring: Ø23), behind a 7 × Ø1.5 grille in the floor, facing down, with an IP67 ePTFE acoustic membrane Ø15 inside. Speakers Ø26 to 28 would need a tall ring and a notch in the board.
- Control panel on the outer face (band z -98.0 … -74.6): IP67 12 mm push-button in a Ø17 × 8 recess (a fingertip reaches it, a paw pad or a snout does not), two flush Ø5 light pipes for the status and Wi-Fi LEDs, three flush knock-outs (2.0 skin) for future switches.
- A blind USB-C position engraved on the lid top, to drill for a sealed panel USB-C when needed.
- Not possible in this pod: an 80 × 60 × 45 box.

## Bought parts of the module

2 × M3 × 16 ISO 4762 A2 (lock), 5 × PT K30 × 10 (lid) with 5 × O-ring 3 × 1, the M8 5-pin panel socket (J1), the IP67 12 mm short-body push-button, 2 × light pipe Ø5 with O-ring 5 × 1, 2 × LED 3 mm, the IP67 acoustic membrane Ø15, a speaker Ø23, and the electronics (5 × 7 cm perfboard, ESP32-WROVER on socket strips, 6 V servo regulator, 5 V logic regulator, 1000 µF capacitor). Full list in three languages: [docs/BOM.md](../../../docs/BOM.md).

## Open points

- J1 socket and nut size are assumed: verify the bought part before printing the lid.
- About 105 of the lid gasket (back edge and notch edges) has no screw nearby: water-test the closed module before any electronics go in.
- PT screws in the lid bosses allow about 5 to 10 openings; for a development module melt 5 M3 inserts into the bosses (Ø7.5) instead.
- Knock-out 3 is shallow (guide wall behind it).
- The module hangs on two M3 inserts in printed posts (safety factor 4.8 at 250 N): do not hang anything from it.
