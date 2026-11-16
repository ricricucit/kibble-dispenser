#!/bin/bash
# Rebuild the 6.4 print package, slice the five Bambu projects with the OrcaSlicer CLI, refresh summary.json + PRINT_GUIDE.md.
#   PY=/path/to/python-with-trimesh-manifold3d ORCA=/path/to/OrcaSlicer/AppRun ./run_all.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$HERE")"
PY="${PY:-python3}"
ORCA="${ORCA:?set ORCA to the OrcaSlicer AppRun or binary (2.5.0 or newer)}"
WORK="${WORK:-$(mktemp -d)}"
cd "$HERE"
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  rm -rf "$OUT/stl" "$OUT/plates" "$OUT/preview"
  "$PY" build_print_v64.py
fi
for P in chassis_PETG:Kibble_Dispenser_v64_chassis_PETG chassis_IP66:Kibble_Dispenser_v64_chassis_IP66_PETG \
         chassis_TPU:Kibble_Dispenser_v64_chassis_TPU module_PETG:Kibble_Module_case_1.0_PETG module_TPU:Kibble_Module_case_1.0_TPU; do
  ID="${P%%:*}"; F="${P#*:}"
  rm -rf "$WORK/$ID"; mkdir -p "$WORK/$ID"
  "$ORCA" --slice 0 --export-statistics --outputdir "$WORK/$ID" "$OUT/$F.bambu.3mf" > "$WORK/$ID/orca.log" 2>&1 || echo "slicer returned an error for $ID (see $WORK/$ID/orca.log)"
done
"$PY" make_summary.py "$WORK"
"$PY" make_guide.py
echo "slicer output kept in $WORK"
