#!/bin/bash
# Rebuild the v6.2 print package, slice both Bambu projects with the OrcaSlicer CLI, refresh summary.json + README.md (the print guide).
# Needs the v6.2 CAD build first (python hardware/v6.2/cad/build_v62.py writes hardware/v6.2/cad/build/; set KD_V62_BUILD to use
# another folder). The Bambu system profiles are fetched from the BambuStudio repository on the first run (not committed).
#   PY=/path/to/python-with-trimesh-manifold3d ORCA=/path/to/OrcaSlicer/AppRun ./run_all.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$HERE")"
PY="${PY:-python3}"
ORCA="${ORCA:?set ORCA to the OrcaSlicer AppRun or binary (2.5.0 or newer)}"
WORK="${WORK:-$(mktemp -d)}"
cd "$HERE"
if [ ! -f bbl_profiles_resolved.json ]; then
  "$PY" fetch_bbl_profiles.py "Bambu Lab A1 0.4 nozzle" "0.20mm Standard @BBL A1" "Generic PETG @BBL A1" "Generic TPU @BBL A1"
fi
rm -rf "$OUT/stl" "$OUT/plates" "$OUT/preview"
"$PY" build_print_v62.py
for M in PETG TPU; do
  mkdir -p "$WORK/$M"
  "$ORCA" --slice 0 --export-statistics --outputdir "$WORK/$M" "$OUT/Kibble_Dispenser_v62_$M.bambu.3mf"
done
"$PY" make_summary.py "$WORK/PETG" "$WORK/TPU"
"$PY" make_guide.py
echo "slicer output kept in $WORK"
