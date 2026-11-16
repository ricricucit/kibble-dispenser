# Independent review of v6.4 before printing on a Bambu Lab A1

Reviewed 2026-11-15. Scope: all 29 printed part files (21 reused from 6.3.0, 4 changed chassis parts, 4 module parts), `v64.json`, the 6.4 build order. Nothing outside this folder was changed.

**Verdict: 0 BLOCKER, 3 MAJOR, 19 MINOR.** The 21 reused parts and the two TPU seals can go to the printer. Three parts (`scatola_v64`, `guscio_v64`, `modulo_vasca_v64`) and the cap must not be printed with the "no support" notes as written: either turn on build-plate-only supports or make the small CAD changes below. The slicer (OrcaSlicer 2.5, A1 0.4 presets, 6.3 package settings) confirms the first two with its own warnings.

Coordinates are assembly coordinates (mm, Z up) unless marked "print z".

## How it was checked

- Mesh audit of every print STL (watertight, bodies, footprint, down-facing area): `audit.py`, `audit.json`, `comps.py`.
- Layer-by-layer support analysis at 0.2 mm (region of each layer not carried by the layer below grown 0.25 mm, i.e. flatter than about 51 degrees): `layers.py`, `layers_*.json`, `layers_reused.txt`.
- Thin features per layer (< 0.8 and < 0.42 mm) and ray-cast wall thickness: `thin.py`, `thick.py`, `thick_*.txt`.
- Cross-sections of the assembled parts: `sec_*.png`, `zoom_*.png` (`lib.py`, `s*.py`).
- Hole diameters and ledges: `holes.py`, `h2.py`.
- Real slices of the 8 new parts, one per plate, with the settings `v64.json` states (no supports) and again with build-plate-only supports: `slice/out_PETG_nosup`, `slice/out_PETG_sup`, `slice/out_TPU_nosup` (`result.json` and per-plate statistics; the G-code was deleted to save space, `slice_v64.py` rebuilds the projects).
- Module displaced against the chassis to find its real stops (boolean intersections).

## MAJOR

### M1. `scatola_v64`: both holder posts start in mid-air (CAD or slicer)

- Measured: the post and its web end flat at z -48. In the stated orientation (roof on the bed) that face is at print z 18.0 and faces down: 2 regions of 98.8 mm2 (9.0 x 14.3 mm), only 14 % of the outline touches the layer below. See `sec_y45.5_post.png`, `sec_z-60.png`.
- Slicer, settings as stated: "It seems object scatola_v64 has a floating cantilever". With build-plate-only supports the warning goes (support 7.5 g, up to print z 38.8).
- Why it matters: these two posts carry the M3 inserts that hold the whole module. A 14 mm one-sided cantilever in PETG on a bed-slinger droops for several layers, so the post root is the weakest, worst-fused zone exactly where the bending load is highest.
- Smallest fix, CAD: continue post and web straight up to z -30 (the bed plane), inside the plan of the module corner notch (x 17.4..29.6, |y| 38..52). The notch is open through the tub and the lid (`sec_z-38.5_lid.png`), so nothing collides, the overhang disappears and the bed contact grows. Alternative: a 45 degree corbel under the web.
- Slicer-only fix: supports "normal, on build plate only, 45 degrees" for this part (the 6.3 guide says "no support at all" for the box: that note must not be carried over).

### M2. `guscio_v64`: the three bowl tabs print as unsupported shelves (slicer, or CAD)

- Measured: the shell prints top edge on the bed, so the tab faces at z 0 face down at print z 64.0: 378, 378 and 298 mm2 (14 x 28 mm visible, tab thickness 6 mm), 15 to 17 % anchored. See `guscio_tab_y0.png`, `guscio_tabs_z-0.5.png`.
- Slicer, 5 walls + 6 mm brim, no supports: "guscio_v64 has floating regions".
- Inherited: the tabs are identical in `guscio_v611` (the boolean difference between the two shells is only the opening and the two ribs), and the 6.3 guide also says "no supports". It was never printed, so it is still open.
- Why it matters: the tabs take the 3 PT K30x12 screws that hold the shell on the bowl; a sagging underside is the screw-head/bowl contact face.
- Fix, slicer: tree supports, on build plate only, for the shell (the column under each tab is free down to the bed, about 64 mm tall). Fix, CAD: a 45 degree gusset from the wall on the print-down side covers only x 62..72 (the bowl is at x < 62), so supports are still needed for the inner part; supports are the practical answer.
- Same part, small: each return rib starts abruptly at print z 100.6 (z -36.65) as a 2.0 x 11.5 mm fin, 12 % anchored. Add a 45 degree lead-in to the rib end, or accept a rough start (it points away from the module).

### M3. `modulo_vasca_v64` and `fondello_v64`: rounded bottom edge needs a support ring, the notes say none (slicer / v64.json)

- Measured on the tub: the first layers grow outward by 1.27 mm at print z 0.2 (81 degrees from vertical), 0.55 mm at z 1.0 (70 degrees), 0.37 mm at z 2.0 (62 degrees), 0.29 mm at z 3.0 (55 degrees), along 95 to 104 mm of the visible front edge. The cap does the same from z 0.2 to 2.4 along 113 to 124 mm.
- Slicer: the tub without supports gives "modulo_vasca_v64 has floating regions"; with build-plate-only supports no warning, 4.0 g of support (cap: 3.9 g). I did not isolate which region triggers the warning; the bottom edge and the rim stairs (m4) are the candidates.
- Why it matters: this is the outer skin beside the 0.35 mm bottom seam. Curled first layers there are visible and make the seam uneven.
- Fix: in `v64.json` print notes and the print guide, give both parts the 6.3 cap setting (normal supports, on build plate only, threshold 45 degrees). `v64.json` currently says nothing about supports for the cap and "bridges: none > 8 mm" for the tub.

## MINOR, CAD should change (small edits)

- **m1. Module has no defined vertical stop.** Raising the module, the first contact is the post end in the socket floor at +0.30 mm, the second the shell edge on the module shoulder at +0.35 mm. The lock screws therefore pull the module 0.3 mm above nominal and leave about 0.05 mm at the top seam; with normal tolerances either part becomes the stop. Fix: make the post end the stop at nominal (socket floor at z -89.0) and open the top seam to 0.5 to 0.6 mm.
- **m2. Board against the lid: 0.3 mm.** Slot floor z -90.5, lid underside z -40.2, board 50.0 mm (the demo board model is drawn touching the lid). A 50.3 mm board or a blob in the slot holds the lid off its four bosses. Fix: slot floor at z -91.5. See `sec_y34.6_slot.png`.
- **m3. Lid screws engage 4.8 mm.** PT K30x8 through the 3.2 mm lid leaves 4.8 mm in the boss (1.6 d). The pilot is 8.5 mm deep. Fix: PT K30x10 (6.8 mm engagement, 1.7 mm spare) in the hardware list; no geometry change. Pilots are Ø 2.49, bosses about Ø 7.5: fine.
- **m4. Rim corbel of the tub is modelled as stairs, not a slope.** Flat ledges of 0.86, 1.09, 1.24 mm (3.1 mm beside boss 4) every 0.8 to 0.85 mm of height, 98 mm long, plus 0.8 mm stairs on the back wall. Each is an unsupported flat ledge. Fix: a true 45 degree face. Same idea for the 1.0 mm flat step behind the bay rim of `scatola_v64` (print z 39, 4.6 x 24 mm regions). See `zoom_rim_y0.png`.
- **m5. Slot B front jaw is 0.75 mm thick**, 1.3 mm deep, 50 mm tall (x 32.75..33.5, |y| 34..35.3): one extrusion line that snaps when a board is pushed in. Fix: lengthen the guide wall so the jaw is at least 1.6 mm. See `zoom_z-60_slots.png`.
- **m6. Lid groove outer wall is 0.85 mm** x 1.2 mm high all round, and the gasket base is a 0.05 mm per side press fit against it. Printable (2 lines), fragile. Fix: 1.2 mm.
- **m7. J1 turret ceiling.** Printed lid-underside down, the turret roof is a flat ring Ø 14.6 with the Ø 8.2 hole in it at print z 12.2 (103 mm2): the hole edge prints in air and this is the nut seat. Fix: close the hole with a 0.2 mm sacrificial layer (drill after), or use bed-only supports for the lid (1.0 g, reachable through the bore).
- **m8. J1 nut access.** The nut sits 12 mm up a Ø 14.6 bore. Fine for a 10 mm AF nut with a thin-wall socket, impossible for a 13 mm AF nut (15 mm across corners). I could not verify the bought connector. Fix: bore Ø 16.5 (turret OD 19 allows it) or check the part first.
- **m9. Bottom seam edges are square on both parts** (module x 17.4, cap x 17.05, down to z -104) and both parts print with that edge on the bed, so both elephant feet land in the same 0.35 mm seam. Fix: 0.4 mm x 45 degree chamfer on both edges and on the vertical module corners at (17.4, ±52). Keep elephant-foot compensation at 0.15 mm.
- **m10. Feather edges.** The top lip of the tub ends in a zero-thickness point at (41.4, ±52, -36); the cut edges of shell and cap meet the skin at about 45 degrees (`guscio_rib_z-38.png`), measured 0.04 to 0.3 mm thick near the edge. They print as whiskers and are the edges a claw meets. Fix: blunt them with a 0.8 mm flat; stop the lip 3 mm before its ends.
- **m11. Drain holes Ø 0.8** (4 holes at (-52, 27), webs 0.76 mm) in the first layer of the cap will print closed on textured PEI. Inherited; the 6.3 guide says to drill them. Fix: Ø 1.5 or one 1.2 mm slot. If they stay closed the cap floor holds about 2.4 mm of water before it spills over the dam into the bottom seam.
- **m12. Post sockets Ø 9.7 on Ø 9.0 posts** (0.35 mm radial) are the tightest locating fit on the module and are vertical holes that print small. Workable; Ø 10.0 costs nothing because the side seams and the top lip already locate the module.
- **m13. `colletto_v6` (reused): two 3 x 3 x 0.4 mm pads float 0.1 mm above the body** (separate shells, print z 15.6 vs body top 15.5). They print, but they are not joined in the model. Inherited.
- **m14. Lock screw heads stand 1.4 mm proud** of the curved bottom on the outer side of their counterbores (head to z -103.6, skin at z -102.2). A small ledge only; deepen the counterbore by 1.5 mm if wanted.

## MINOR, slicer or print guide only

- **m15. TPU `modulo_guarnizione_v64`:** lip is about 0.5 mm thick, modelled as 0.28 mm stairs. With classic walls the slicer adds gap fill (131 mm3); with Arachne at 15 mm/s it prints as one line (no gap fill). State "Arachne, 15 mm/s" for it, as for the other thin lips. `guarnizione_fondello_v64` (0.55 mm lip) slices cleanly with the 6.1 settings.
- **m16. Horizontal holes** print with a sagging top and slightly small: gland Ø 12, vent Ø 2, light pipes Ø 5.2, button recess Ø 17. Plan to ream the light-pipe holes and check the gland pad for flatness (vertical face, cannot be ironed).
- **m17. Large thin walls on an open printer:** the tub back wall is 2.0 x 104 x 67 mm and flat, and runs 0.35 mm from the cap edge. Use the IP66 temperature and fan settings (245 to 250 C, fan 40 % or less) and check it for bow before fitting.

## MINOR, consistency of v64.json with the files

- **m18. Hardware:** "3x1 (stack 2, cap 4)" and two O-rings are drawn under P2 and P3, but `decisions` says only P2 is inside the bay (P3 is outside). The P3 O-ring seals nothing: list 1, or say why it stays.
- **m19. Other wording:** (a) `pod_seams.largest_gap_a_claw_meets_mm` is 0.4, but the cap-to-shell seam is 0.6 mm (shell edge z -72.0, cap shoulder z -72.6, inherited); (b) gram estimates use 15 % infill while the print notes ask for 100 %: slicer gives tub 87 g (json 73.1), bay 84 g (55.3), cap 110 g (100.3), shell 153 g (173.1); (c) `checks.watertight_exported_stl_reload` is true, but `fondello_v64_print.stl` reloads non-watertight after vertex merge because of 4 zero-area fins on the spigot (3 reused print files have the same); the slicer accepts them; (d) the shell note "top edge on the bed" matches the file, the 6.3 guide wording "seam edge on the bed" does not.

## Assembly logic

- The 6.4 build order is physically possible: tool access, insert and pilot sizes and the module sweep hold up against my own sections.
- Module removal: the sockets engage the posts only over the last 17.8 mm of travel. At the 30 mm "plug access" position the module is off the posts and hangs on your hand or on the M8 cable. Advice: add a note to hold it, or a detent at 30 mm.
- Refitting is blind: the 35 mm harness loop has to fold above the lid with 1.0 mm between the lid and the P3 pad and 0.4 mm between top lip and shell. A cable clip on the lid would remove the pinch risk.
- Servo service needs the cap off and the three crimps pulled out of the JR housing to pass the gland (already noted in the json).

## Checked and found fine

- All 29 print files load, are manifold for the slicer, and match their assembly files (rigid transform error 0.000 mm); the 21 reused files match the stated hashes; all STL/3MF pairs have equal volume; viewer references all exist.
- Bed fit: largest footprint is the shell at Ø 164 mm (176 with brim); flange plates 180 mm; all inside 256 x 256 with margin.
- No unsupported islands in any new part; reused parts show only what the 6.3 guide already supports (bowl lugs, latch tab).
- Walls: tub skin and floor 2.5, back 2.0, knock-out skins 1.64 under the engraving, bay walls 1.8 to 2.0, cap groove walls 1.15. Nothing under 0.8 mm where it seals.
- Screw and insert features: PT pilots Ø 2.49 in Ø 7.5 to 8 bosses, cap screws engage 8 mm; insert holes Ø 3.99 with 2.5 mm wall; M3 clearance Ø 3.39; grille 7 x Ø 1.5 with an outside chamfer.
- Seals: lid lip sits on an unbroken land (`sec_z-41.2_land.png`), 1.2 mm nominal interference, lid seats on its 4 bosses with a 0.5 mm gap elsewhere; cap lip groove 2.2 x 1.15 for a 2.15 base.
- Module sweep: no contact on the way out; side play ±0.35 mm, top lip 0.4 mm.
- Water: counterbores, button recess and grille face down; the lid top drains to the back and sides into the unsealed pod.

## Could not verify

- Sealing of the lid: about 150 mm of gasket (the whole back edge and both notches) has no screw, and the lip tips point inward, so outside pressure does not press them on. Needs the water test the json already asks for.
- Fits that depend on your spool and printer: 0.35 mm seams, 0.25 mm radial cap spigot in the shell (Ø 139, inherited), lid drop-in 0.3 mm. Print the shell-edge, cap-edge and tub-corner region as test cuts first.
- Bought parts: M8 socket nut size, speaker, switch body, light pipes.
- Warping of the 180 mm flange plates and the shell (inherited, not printed yet), and the firmware side.
