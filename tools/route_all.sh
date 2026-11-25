#!/bin/bash
# Build and route the board from the schematic's netlist, start to finish. About an hour.
#   tools/route_all.sh            everything
#   tools/route_all.sh finish     skip the autorouter: use its saved result, routing/route_signals.ses
#                                 (only valid while the placement and scripted tracks are unchanged)
# The autorouter is not repeatable run to run, so its result is kept (routing/route_signals.ses) and
# the board that goes out is whatever this script last produced: check it, do not assume it.
set -e
cd "$(dirname "$0")/.."
export KICAD_DOCUMENTS_HOME="$PWD/kicad-user"
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
quiet() { grep -v "wxApp\|Debug\|memory leak\|^$" || true; }
W=build/pcb

mkdir -p $W routing
python3 tools/schematic.py export | tail -1                     # also writes build/sch/netlist.net
"$KPY" tools/build_board.py 2>&1 | quiet                        # placement, nets, electrodes
"$KPY" tools/route_board.py strip 2>&1 | quiet                  # LED strip, touch block, touch lanes
cp dinolight.kicad_pcb $W/strip.kicad_pcb                       # what counts as "scripted" from here on
if [ "$1" != "finish" ]; then
    "$KPY" tools/route_board.py dsn 2>&1 | quiet
    rm -f $W/route.ses
    # 80 passes, about 35 minutes on four layers: it gains almost nothing after pass 50, and the patch router finishes
    # what is left. Keep the Mac awake (lid open): the autorouter's time limits expire during sleep and
    # it then fails most connections.
    caffeinate -is tools/freerouting_capped.sh ${PASSES:-80} $W/route.dsn $W/route.ses > $W/freerouting.log 2>&1
    cp $W/route.ses routing/route_signals.ses
else
    cp routing/route_signals.ses $W/route.ses
fi
"$KPY" tools/route_board.py ses 2>&1 | quiet
"$KPY" tools/patch_route.py --rounds 14 2>&1 | quiet            # what the autorouter left open, and its rule breaks
"$KPY" tools/clear_touch_neighbours.py 2>&1 | quiet             # what the autorouter laid too near a touch line
"$KPY" tools/patch_route.py --rounds 8 2>&1 | quiet             # ...laid again at the touch lines' spacing
"$KPY" tools/patch_route.py --tidy 2>&1 | quiet                 # dead ends, including unused scripted stubs
"$KPY" tools/patch_route.py --rounds 6 2>&1 | quiet             # anything the tidying opened
"$KPY" tools/patch_route.py --ground --rounds 6 2>&1 | quiet    # every ground pad tied in by track
"$KPY" tools/patch_route.py --rounds 6 2>&1 | quiet             # anything the ground tracks pushed aside
"$KPY" tools/patch_route.py --plane-vias 1.5 2>&1 | quiet       # a via to the ground plane beside every ground pad
"$KPY" tools/patch_route.py --rounds 4 2>&1 | quiet             # anything those took the room of
"$KPY" tools/patch_route.py --fatten 2>&1 | quiet                # wider supply tracks on the half-ounce inner layer
"$KPY" tools/patch_route.py --rounds 3 2>&1 | quiet             # in case widening left anything to re-lay
"$KPY" tools/clear_touch_neighbours.py 2>&1 | quiet             # should report nothing: a check
"$KPY" tools/trim_dangling.py 2>&1 | quiet                      # KiCad's own list of dead ends, safely
cp dinolight.kicad_pcb $W/before_pour.kicad_pcb
"$KPY" tools/route_board.py pour 2>&1 | quiet                   # ground plane, pours on the other layers, stitching vias
"$KPY" tools/silkscreen.py 2>&1 | quiet                         # the show face's drawing, pad outlines, LED numbers and name
"$K" pcb drc --format json --severity-all --schematic-parity -o $W/drc.json dinolight.kicad_pcb > /dev/null
python3 tools/drc_summary.py $W/drc.json
rm -f ./~*.lck
