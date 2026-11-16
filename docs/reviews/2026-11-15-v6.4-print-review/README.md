# Print review of design v6.4 (2026-11-15)

An independent review of every printed part of hardware 6.4 (chassis 6.4 and electronics module case 1.0) before the first print on a Bambu Lab A1, made on the CAD files of 2026-11-15. The report is [REVIEW.md](REVIEW.md): 0 blocker, 3 major and 19 minor findings.

What happened next: the 6.4.0 CAD answers every finding; the answers are recorded finding by finding in `hardware/cad/v64.json` (`review_2026_11_15`) and summarised in [hardware/README.md](../../../hardware/README.md). One major finding stays partly open by design: the inner 12 mm of the three bowl tabs of the shell still need tree supports from the build plate, which the print package sets up.

Evidence in this folder, as it was produced:

- `audit.json`, `layers_*.json`, `layers_reused.txt`, `thin_*.json`, `thick_*.txt`, `xf.json`: mesh audit, layer-by-layer support analysis, thin features and wall thickness of the print files;
- `sec_*.png`, `zoom_*.png`, `guscio_*.png`: cross-sections of the assembled parts;
- `slice/out_*`: OrcaSlicer 2.5 statistics of the trial slices without and with build-plate-only supports (`result.json` per run); the trial Bambu projects and the G-code are not kept, `slice_v64.py` rebuilds them;
- `*.py`: the scripts that made the evidence. They ran in the designer's working folders, so their absolute paths point there; adapt the paths to rerun them against `hardware/cad/build/` and `hardware/plates/`.

The review describes the files before the fixes. Status of the design: designed and checked in CAD only, not printed, assembled or tested.
