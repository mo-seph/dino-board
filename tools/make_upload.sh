#!/bin/bash
# Export the JLCPCB upload set from dinolight.kicad_pcb into fab/<name>/:
#   <name>_gerbers.zip, bom_jlcpcb.csv, cpl_jlcpcb.csv
# Usage: tools/make_upload.sh <name>       e.g. tools/make_upload.sh v0.1        (four copper layers)
# The placement file comes from JLCPCB's own footprints (jlc_cpl.py from the pcb-for-assembly skill).
set -e
cd "$(dirname "$0")/.."
NAME="${1:?give the upload set a name, e.g. draft2}"
export KICAD_DOCUMENTS_HOME="$PWD/kicad-user"
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
JLC_CPL="$HOME/.claude/skills/pcb-for-assembly/scripts/jlc_cpl.py"
OUT="fab/$NAME"
rm -rf "$OUT"
mkdir -p "$OUT/gerbers"
"$K" pcb export gerbers --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
    --subtract-soldermask --no-x2 -o "$OUT/gerbers/" dinolight.kicad_pcb > /dev/null
"$K" pcb export drill --format excellon --excellon-separate-th --excellon-units mm --excellon-zeros-format decimal \
    -o "$OUT/gerbers/" dinolight.kicad_pcb > /dev/null
rm -f "$OUT"/gerbers/*.gbrjob
(cd "$OUT/gerbers" && zip -q "../${NAME}_gerbers.zip" *.g* *.drl)
python3 tools/make_bom.py "$OUT/bom_jlcpcb.csv"
"$KPY" "$JLC_CPL" dinolight.kicad_pcb "$OUT/bom_jlcpcb.csv" -o "$OUT/cpl_jlcpcb.csv" --cache draft/.jlc_cache 2>&1 \
    | grep -v "wxApp\|^$" | grep "CHECK\|wrote" || true
# U9 (SHT40): JLCPCB's footprint has a centre pad that ours leaves out, so jlc_cpl.py cannot pair the pads and
# puts the part 0.16 mm off. Its four pads are symmetric about the footprint origin in both libraries (checked
# by the layout re-read, 2026-11-23, which also confirmed rotation 0 from the pin names), so use the origin.
"$KPY" - "$OUT/cpl_jlcpcb.csv" <<'PY' 2>&1 | grep -v "wxApp\|^$" || true
import csv, sys, pcbnew
ORIGIN = ('U9',)
board = pcbnew.LoadBoard('dinolight.kicad_pcb')
rows = list(csv.reader(open(sys.argv[1])))
for r in rows[1:]:
    if r[0] in ORIGIN:
        p = board.FindFootprintByReference(r[0]).GetPosition()
        new = ['%.3fmm' % pcbnew.ToMM(p.x), '%.3fmm' % -pcbnew.ToMM(p.y)]
        print('%s placed at its footprint origin: %s, %s (was %s, %s)' % (r[0], new[0], new[1], r[1], r[2]))
        r[1], r[2] = new
csv.writer(open(sys.argv[1], 'w', newline='')).writerows(rows)
PY
rm -f ./~*.lck
ls -la "$OUT" | awk 'NR>1 {print $5, $9}'
