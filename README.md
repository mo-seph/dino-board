# DinoLight

A mosasaurus-shaped light-up circuit board: 18 side-firing addressable LEDs along the spine, a glowing
eye, capacitive touch pads on the bare front face, motion, compass, temperature, light and pressure sensors,
a buzzer, a rechargeable LiPo and USB-C.
The brain is an ESP32-S3 module intended to run CircuitPython. Designed in KiCad 10 for assembly by JLCPCB.

**Status:** work in progress. Read [NOTES.md](NOTES.md) first: it has the current state, every design
decision and its reason, the parts list with stock checks, the review findings, and the pin map.

## What is where

| Path | What it is |
|---|---|
| `NOTES.md` | The running record. Start here |
| `output/schematic.pdf` | The schematic to read (also `schematic_p1..4.png`) |
| `dinolight.kicad_sch`, `mcu.kicad_sch`, `leds.kicad_sch`, `sensors.kicad_sch` | The schematic, generated: do not edit by hand without reading the note below |
| `dinolight.kicad_pcb` | The board, generated from the schematic's netlist and routed by `tools/route_all.sh` |
| `tools/design_spec.py` | Every part and net, declared once. The source of truth |
| `.github/workflows/boardlint.yml` | CI: a design review of the KiCad files with [boardlint](https://github.com/mattvenn/boardlint) on every change to them. Findings show on the run; it does not fail the build unless `BOARDLINT_STRICT` is set to `true` |
| `tools/schematic.py` | Draws the schematic from the spec |
| `tools/build_board.py` | Builds the board: outline, placement, nets |
| `tools/route_all.sh` | Builds and routes the board start to finish (calls the tools below) |
| `tools/route_board.py` | Scripted tracks (LED strip, touch lines), autorouter hand-over, ground pours |
| `tools/patch_route.py`, `tools/trim_dangling.py` | Finish what the autorouter leaves open; tie in ground; tidy |
| `tools/silkscreen.py` | Draws the show face's silkscreen: the mosasaurus, touch pad outlines, LED numbers, the name |
| `tools/title_outline.py`, `art/lettering.json` | The lettering as plain outlines, made once from a font file |
| `tools/freerouting_capped.sh` | Runs the Freerouting autorouter for a set number of passes |
| `routing/route_signals.ses` | The autorouter's last result, kept because it differs run to run |
| `outline/` | The outline generator and its SVG / PNG |
| `lib/` | Project symbols and footprints |
| `datasheets/` | Maker datasheets, named by JLCPCB part number |
| `draft/` | An early quote-only board and its JLCPCB upload files. Not for ordering |

## Regenerating

The schematic and board are written by scripts, so a change is made in `tools/` and the files are
regenerated. Anything edited by hand in KiCad is overwritten the next time a script runs.

```bash
export KICAD_DOCUMENTS_HOME="$PWD/kicad-user"
python3 tools/schematic.py export        # schematic files, PDF and PNGs, and build/sch/netlist.net
tools/route_all.sh                       # the board from that netlist, placed and routed: about 40 minutes
tools/route_all.sh finish                # the same, reusing the saved autorouter result
```

`tools/route_all.sh` needs KiCad 10, Java and Freerouting 2.1.0 at `~/.kicad-mcp/freerouting.jar`. Keep
the computer awake while it runs: the autorouter fails most connections if the machine sleeps part way.
The autorouter's result differs run to run, so check the board the script produces (its last lines
are KiCad's rule-check summary) instead of assuming it matches the last one.

`tools/schematic.py` needs `schdraw.py`, a small drawing library that is not in this repository yet;
`tools/design_spec.py` looks for it in `~/.claude/skills/pcb-for-assembly/scripts`. The board scripts
need KiCad's own Python (for `pcbnew`).
