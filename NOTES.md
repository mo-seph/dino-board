# DinoLight v0.1 (started 2026-11-22), about 212 x 74 mm

Mosasaurus-shaped light-up PCB, a toy for a young child.
18 side-emitting addressable LEDs along the spine, a one-LED eye on the parts side shining through a hole in the printed case, ESP32-S3 module running CircuitPython,
12 capacitive touch zones on the bare front face read by an MPR121 touch controller, LiPo, USB-C.
Sensors for science games (added 2026-11-22 at the owner's request): accelerometer + gyroscope, compass,
temperature + humidity on the tail tip, light at the nose, barometer; and a buzzer.
JLCPCB Standard assembly, parts on one side. 4 layers (changed from 2 on 2026-11-23): parts side, ground
plane, inner signal layer, show face.

Decisions marked "owner" are the owner's; those marked "mine" were made by the AI assistant doing the
design work and are open to change.

## State

2026-11-26: ORDERED AS `fab/v0.1` STANDS IN THIS REPOSITORY, WITH THE 2 MB MODULE. The history: first
uploaded on 2026-11-25 from the first v0.1 package (Gerber zip md5 da43ef1e..., the set the release review
read, without the cell-polarity marks and with the ACC_INT1 stub). The owner then changed the order
(2026-11-25: "I've changed the order, so we will have the 2M ram"; 2026-11-26: "Gerbers were changed").
What is being made is therefore `fab/v0.1`: Gerber zip md5 15493355..., with the polarity marks and
without the stub, and the BOM line for U4 naming C3013941. `dinolight.kicad_pcb` is the board as ordered.
Quantity, price, board options and what JLCPCB's placement preview showed are not recorded here yet. See
"When the boards arrive".

The module change, 2026-11-25: U4 is ESP32-S3-MINI-1-N4R2, C3013941: 4 MB flash and 2 MB PSRAM in place
of the N8's 8 MB flash and none. The reason: the firmware plan (a web page served by the board,
behaviours uploaded over Wi-Fi) is tight in the N8's 512 KB.

- JLCPCB's part page, read 2026-11-25: 6,219 in stock, $5.0128 (the N8 is $4.7163), extended, Standard
  Only, X-ray, MSL 3: the same classes as the N8.
- JLCPCB's footprint for it is the same footprint record as the N8's (73 pads, same origin).
- The module datasheet (v1.7, in `datasheets/`): the two versions "only vary in flash and PSRAM size"; on
  the N4R2, IO26 belongs to the PSRAM. IO26 (pad 26) has no connection on this board.
- Changed: `tools/design_spec.py`, the schematic (regenerated: 86 nets, 0 differences), U4's value on the
  board (a text field on the fabrication layer, nothing else), and one line of `fab/v0.1/bom_jlcpcb.csv`.
- Checked by script: a fresh Gerber and drill export equals all 13 files in `fab/v0.1/v0.1_gerbers.zip`
  (md5 unchanged, 15493355...); the placement file derived again from the new BOM equals
  `fab/v0.1/cpl_jlcpcb.csv` (U4 at 177.000, -57.050, rotation 180, as before). Not read by anyone else.
- Not known: the PSRAM's draw in deep sleep (the datasheet says only that current "might be higher", and
  gives 40 uA for light sleep); which CircuitPython build to use (4 MB flash, 2 MB PSRAM).

2026-11-24: PACKAGED FOR ORDERING AT THE OWNER'S WORD ("repackage and I'll get it made"): `fab/v0.1/`.
Routed on four layers. The layout has had an independent review and, after the owner's changes and a fresh
route, an independent re-read with no blocker. Changed since that re-read and not yet independently read:
its own three fixes, the regulator and two capacitors, and the show-face silkscreen: all read by the
independent release review of 2026-11-24, with `fab/v0.1` itself (see Reviews): no blocker, two should-fix,
both acted on. After that review, and read by nobody else: a dead stub of ACC_INT1 removed (13 pieces, one
via; pours refilled) and the cell-polarity marks added to the parts side; `fab/v0.1` was rebuilt after
them and checked by script against the board. Still open at the time of packaging: see NOT DONE below.

- 2026-11-24, after the boardlint review the owner sent: regulator U3 is now an XC6220B331MR-G (lower
  dropout, same pads), C3 and C5 are 22 uF. Parts and values only, no copper moved; rule check unchanged;
  the upload set regenerated (U3's placement line changed with the part: check it in the preview). Not
  independently read. See "boardlint review" under Reviews.
- Architecture agreed by the owner (2026-11-22). Parts chosen and checked at JLCPCB; the sensors and buzzer
  were added on 2026-11-22 at the owner's request and checked the same way.
- Schematic: `tools/design_spec.py` drawn by `tools/schematic.py`, 4 pages, 155 parts, 86 declared nets.
  KiCad's netlist matches the declared nets with 0 differences. ERC: 2 findings, accepted (U5 pins 1 and 2
  tied to ground, as the datasheet asks; KiCad dislikes their pin type). Pages rendered and looked at.
  THE OWNER HAS NOT READ THE SCHEMATIC.
- Reviews of the netlist against datasheets: 1 and 3 with their re-reviews, and review 4 (sensors, buzzer).
  No blocker open. Changes made after review 4 (pull-downs to 4.7k, buzzer drive parts, guard track) have
  not been independently re-read. See Reviews.
- Board: `dinolight.kicad_pcb`, built and routed by `tools/route_all.sh` (see "Routing"). KiCad DRC with
  schematic parity: 0 unconnected items, no shorts, no clearance errors. `board_audit.py` run; see
  "Routing" for what it found and what was done.
- Layout review (the skill's review 2) by an independent reader: done on the first four-layer route, 16
  findings, all decided. Re-read of the re-routed board and of `fab/draft3`: done, no blocker, three
  should-fix, acted on (see Reviews).
- Changes asked for by the owner on 2026-11-23 and made: eye LED is an ordinary top-emitting part; 18 spine
  LEDs, slider shortened to match; no tail mounting hole; Qwiic socket opens into the case; compass inside
  the case. None of these has had an independent netlist or layout read.
- JLCPCB quote on the first draft (2 layers, before the touch chip and sensors): EUR 143 before tax and
  shipping for 5 assembled, Standard assembly only.
- Second quote, 2026-11-23, on the `fab/draft2` set (2 layers, touch chip, no sensors or buzzer): EUR 246
  for 5 with EUR 30 shipping and EUR 50 tax. JLCPCB's costed BOM for it: parts USD 68.29 for 5 (module
  23.68, touch chip 13.45, side LEDs 9.40, old accelerometer 4.44, charger 3.90); 14 extended part lines.
  The eye LED was flagged twice: advanced part, and baking. The current board (4 layers, five more
  extended lines) has NOT been quoted and will cost more. `draft/` and `fab/draft2/` are old quote-only sets
  and must not be ordered.
- `fab/v0.1/` (2026-11-24): THE UPLOAD SET, made by `tools/make_upload.sh v0.1` after the last change to
  the board (it replaces `fab/draft3`, which was for a quote): Gerbers for four copper layers, mask, paste and silkscreen, drill files, BOM
  (42 lines, 122 parts), placement file from JLCPCB's own footprints. `jlc_cpl.py` asks for a look in
  the preview at: D23 (polarised); J1, J2, J3, SW1, SW2, U4 (matched by position); and U9, where
  JLCPCB's footprint has a fifth, centre pad that the KiCad footprint (Sensirion's no-centre-pad pattern)
  leaves out, so its rotation could not be confirmed from the pads. The new eye LED D21 matched without
  comment. U9 is placed at its footprint origin. Checked by script on 2026-11-24: every
  file in the zip is the same as a fresh export of the board (dates aside); 42 BOM lines, 122 parts, each
  netlist part with a part number in the BOM once with that number; 122 placement lines, the same
  designators. The re-read of 2026-11-23 checked the first version of this set (layers, drill, BOM, every
  rotation); U3's rotation has changed since (new part: 0, was 270).
- Git: branch `main`, remote `origin`.
- Tools: kicad-cli 10.0.8 runs with `KICAD_DOCUMENTS_HOME=<project>/kicad-user`.
- NOT DONE: the owner's read of the schematic; mechanical sign-off of the placement and the mounting-hole
  positions (placeholders); a read of the fixes made after the re-read; the owner's view of the show-face
  artwork (first version drawn 2026-11-24, see Decisions) and the parts-side silkscreen, which still says
  DRAFT; JLCPCB's edge rails and tab positions; the release review; JLCPCB's placement preview.

## Deadline

- The finished toy is needed in the second half of December 2026, with a slow outbound shipping leg
  after assembly and testing.
- Target order date Fri 27 Nov; latest sensible Mon 30 Nov. Standard assembly is 4 days or more after
  2 to 3 days of fabrication (JLCPCB lead-time article).
- No second spin. Module not bare chip, test points, hard switch as well as soft sleep.

## Decisions

| Decision | Why | Whose |
|---|---|---|
| Mosasaurus, head left on the show face, about 212 x 74 mm | The recipient's favourite; no thin legs, so robust | owner |
| Bare PCB front is the show face: artwork and touch pads, no cover | "Clearly a made thing" | owner |
| Show-face silkscreen, 2026-11-24: a line drawing of the mosasaurus (eye, brow, teeth, belly line, the backbone turning down into the lower tail lobe, tail bands and rays), an outline round every touch pad, a number by each spine LED from 1 at the head (D1, the first LED firmware addresses), and "Mosasauraboard" 9.3 mm high. Printed reversed: white ink over 84 % of the face, the drawing left as bare solder mask, a 0.5 mm bare rim at the edge | The owner asked for exactly this, and for it reversed "if that is allowed". It is: JLCPCB's capabilities page lists hollow-carved lettering and puts no limit on printed area (see Check before ordering). Made by `tools/silkscreen.py`, which reads the touch copper and mask openings from the board; `tools/silkscreen.py lines` gives the ordinary white-on-green version. Nothing printed is under 0.2 mm wide and nothing bare under 0.25 mm. Lettering: Arial Rounded Bold, as outlines in `art/lettering.json` | owner; drawing mine, for the owner to look at |
| CircuitPython | Easy to change later: edit `code.py` on the USB drive | owner |
| Battery bought locally at the destination, not shipped with the toy | Lithium cells are restricted in the post | owner |
| ESP32-S3-MINI-1-N8 module | Native USB (no bridge chip), deep sleep, Bluetooth, in stock. Cheaper modules checked 2026-11-22: ESP32-S2-MINI-2 ($2.89) loses Bluetooth and the two LED data pins; ESP32-C3-MINI-1 ($3.05) is no better. Saving about $9 on five boards: not worth it | mine, open |
| Dedicated touch controller U7 (MPR121, 12 channels, I2C 0x5C), not the module's own touch pins | The owner has not had good results with the ESP32's built-in touch. The MPR121 has a CircuitPython library, an interrupt that can wake the module, and gives per-electrode readings, so the eight spine pads can be read as a slider. Others checked at JLCPCB on 2026-11-22: AT42QT2120 (in-chip slider, but only across three channels, SOIC-20, no library), CAP1188 / CAP1298 (8 channels, low stock), Azoteq IQS7222 (none in stock) | owner |
| The touch slider runs the whole length of the LED run | So a light can follow the finger: touch with no LED above it, or LEDs with no touch below, would spoil that | owner |
| Touch controller address 0x5C: ADDR tied to SDA | The datasheet allows ADDR on VSS, VDD, SDA or SCL. SDA is the neighbouring pin, so the tie is a 0.4 mm bridge instead of a ground connection threaded out between other pins; it also keeps clear of 0x5A, which several Qwiic add-ons use. Changed 2026-11-22 after review 3, which had checked it grounded: this one net is unreviewed | mine, open |
| Slider electrodes interleave with long teeth: 8 segments, each with one central tooth reaching to the next segment's centre between two half-teeth of its neighbour | Atmel AT11805 (in `datasheets/`) calls this spatial interpolation: touch area passes linearly from one electrode to the next, so position can be interpolated. Its figures followed here: tooth sections 3 to 4 mm tall (3 mm used), tips no thinner than 0.25 mm (0.3 used). The note's own long-slider circuits are mutual-capacitance designs for Atmel's PTC, and its resistor-interpolated version does not apply to a self-capacitance chip like the MPR121; the electrode shape does. Segment pitch is 18.5 mm (20.7 mm before the run was shortened to 18 LEDs), wider than the 8 mm keys the note's standard slider uses, which is what the long teeth compensate for | mine, open |
| 470R in series with each touch electrode | Static and noise protection; electrodes are under solder mask only | mine, open |
| Eye = one ordinary top-emitting LED (D21, OPSCO SK6812MINI-012, 3.7 x 3.5 mm) on the parts side, shining away from the board through a hole in the printed case. No hole in the board | The owner, 2026-11-23: "the eye should shine through the case - we'll make a 3d printed face with a hole for the eye... It's not a reverse light thing." Until then the board carried a reverse-mount SK6812MINI-E (C5149201) in a slot, shining through the board to the bare face: my misreading of the brief, and the part JLCPCB charged for twice (advanced part, baking) in the second quote. Chosen from JLCPCB's in-stock addressable LEDs on 2026-11-23: same maker and family as the spine LEDs, MSL 3 and no difficulty flag on its page. Others looked at: XL-5050RGBC-2812B (C2843785, MSL 6), WS2812B-B/T (C2761795, 1 in stock, difficulty high), SK6812MINI-EA (C5378731: sits recessed in a 3.8 x 3.4 mm opening in the board, per its datasheet's land pattern, so it needs a cut-out too). NOT CONFIRMED with the owner: that the printed face with the eye hole is on the parts side of the board. If it is on the bare-PCB side, this part cannot reach it | owner |
| LEDs powered from the battery only, never from USB 5 V | LED input high threshold is 0.65 x VDD (datasheet): 2.73 V at 4.2 V, fine for 3.3 V logic; 3.25 V at 5 V, not fine. Avoids a level shifter | mine, open |
| LED rail behind a P-FET switch (Q2, driven by Q3), off by default | 0.6 mA per LED when dark (datasheet), 19 LEDs = 11 mA standing drain | mine, open |
| Slide switch works the regulator's enable pin, not the battery current | The switch is rated 50 mA. Off state is regulator shutdown (0.1 uA typ) with the LED rail off | mine, open |
| USB plugged in also enables the regulator (D23, then R4 / R5, 200k each) | Plugging in wakes it to show charging and makes it programmable whatever the switch says. 200k, not 1M: with 1M a 10 M leak across the switch (its own after-humidity spec) would reach the enable threshold and the toy would not turn off. Costs about 21 uA while switched on. D23 (1N4148W) stops the battery feeding back onto VBUS through R4, which otherwise leaves VBUS_DET at an undefined level and may stop a USB-C charger from starting | mine, after reviews |
| Supervisor U6 (TLV803S, 2.93 V, open drain) on the module's EN through R32 1k; EN pull-up R16 100k, C32 100 nF | Below 2.79 V the charger only trickles 21 mA, less than an awake module draws, so a deeply flat cell would never recover with USB always waking the module. U6 keeps the module off until the rail is up, and supplies the 200 ms start-up delay. R32 keeps U6's output within its 5 mA limit when it discharges C32. Adds about 12 uA | mine, after reviews |
| Fuse F1 in series with the battery connector pin, ahead of the polarity jumpers | A half-done or blobbed jumper change would otherwise short the cell with no fuse in the path | mine, after review 1 |
| C10 from gate to drain of Q2 (was gate to source) | Sets the LED rail's rise to about 1.5 ms and the inrush to about 60 mA, instead of an estimated 2 A spike that could dip the battery and reset the module when the LEDs come on | mine, after review 1 |
| CHG_STAT and VBUS_DET dividers 100k over 200k (2/3) | Half of a sagging 4.4 V USB supply is 2.2 V, under the module's guaranteed high level of 2.475 V | mine, after review 1 |
| C3, C4 at the regulator are 10 uF 0805 (were 1 uF 0402) | A 1 uF 0402 loses much of its value with 3 to 4 V across it; the regulator wants 1 uF effective | mine, after review 1 |
| No USB power path: board runs from the battery, charger tops it up | Fewer parts; needs a battery fitted to run | mine, open |
| XC6220B331MR-G regulator (was RT9080-33), 2026-11-24 | The owner, after the boardlint review: "see if we can find a lower dropout regulator". Same pins and pads. Pass transistor 0.2 ohm typ against about 0.5: at a 356 mA transmit peak it drops 113 mV at most where the RT9080 could drop 314 mV, so the module stays above 3.0 V down to a 3.36 V cell (was 3.56 V, above the 3.5 V at which firmware sleeps). Costs: 8 uA quiescent in place of 2 (sleep total about 80 to 86 uA), $0.48 in place of $0.12, enable threshold 1.2 V in place of 0.9 V (USB alone gives 1.9 to 2.4 V) | owner asked, mine chosen |
| C3 (regulator input) and C5 (at the module) are 22 uF 0805, were 10 uF | C3: the XC6220's table wants 10 uF of real input capacitance for a 4.7 uF output capacitor (with 4.7 uF in, 47 uF out), and a 10 uF 0805 gives less than 10 with 4 V across it. C5: the 22 uF the module datasheet shows. Same pads, basic part | mine |
| MCP73831 charger at 213 mA (4.7k) | Gentle on a 500 mAh cell | mine, open |
| Charger STAT through a 100k / 100k divider | STAT is three-state and drives to VBUS (5 V) when charge completes; the module's pins are 3.3 V | mine |
| Polarity jumpers SJ1, SJ2 on the battery connector | JST-PH LiPos come in both polarities and the cell is bought separately, unseen. Default: J2 pin 1 = + (SparkFun's stated convention; whether that is the footprint's pad 1 is unverified) | mine, open |
| Reverse-polarity P-FET Q1 and a 1.1 A polyfuse F1 at the battery | A wrong-way cell then does nothing rather than damage; a child's toy | mine, open |
| Eye LED on its own data pin (IO48), spine on IO11 | IO48 is the status-LED pin of the DevKitM-1 board, whose stock CircuitPython build should run on this module (from memory, unverified). The spine moved from IO47 to IO11 on 2026-11-22: IO11 is the module pad nearest the first LED, and its series resistor R14 now sits beside that LED, so the line no longer crosses the module twice. Not a strapping pin; unreviewed | mine, open |
| The three long touch lines (tail, rear flipper, front flipper) run in scripted lanes on the parts side, beside the slider's eight, for the length of the body | Left to the routers they came out 100 to 180 mm long, wandering, partly on the show face, where a touch line answers to a finger anywhere along it; and every other route kept pushing them aside. In lanes they are fixed, short, and behind the slider's own copper. The module moved 1.2 mm away from the spine to make room | mine, open |
| Touch channel order: ELE8 snout, ELE9 tail, ELE10 rear flipper, ELE11 front flipper | So the three long lines leave the controller nested and none crosses another: the tail line is outermost and stays in its lane longest. Firmware needs a table, not arithmetic | mine, open |
| Every ground pad is tied in by track before the pours go on, and every surface ground pad has a ground via within 1.5 mm | The first routing pass left 79 ground pads hanging on fragments of pour. Now the plane and pours add to the ground instead of being the only thing holding it together; the four pours are stitched on a 4 mm grid. Three pads could not take a via of their own (SW2.2, SW3.2, C8.2) and rely on their tracks | mine, open |
| Decoupling capacitors are placed with their chip as one block (regulator, charger, accelerometer, supervisor) | The first placement packed parts by size, which left these capacitors 6 to 10 mm from the pins they serve (found by `board_audit.py`) | mine |
| No copper within 2.8 mm of a mounting hole's centre, either face | Room for an M2.5 screw head or a case boss. The hole positions are still placeholders | mine, open |
| Sensors added: LSM6DS3TR-C (accelerometer + gyroscope, replaces the LIS2DH12), QMC5883P (compass), SHT40 (temperature + humidity), LTR-303ALS (light), BMP580 (pressure), and an MLT-5020 buzzer | The owner, 2026-11-22: "add them all - worst case, we can not place them". Nine motion axes from two chips for $2.90; single-chip nine-axis parts at JLCPCB are $10 to $20 or out of stock | owner |
| Temperature sensor on the tip of the tail, compass in the tail stem inside the case, light sensor at the nose, buzzer in the jaw | Owner: the tail sticks out of the case as a thermometer; only the temperature sensor and the tail touch pad are outside it (2026-11-23: "compass inside the case, I think that's better and safer"); the light sensor goes at the nose. Mine: the compass sits between the end of the LED run and the Qwiic socket, at board (61.7, 57.65): the far end of the LED rail, where its current is smallest (the last two LEDs at full white would add about 1.4 uT there, against the Earth's 25 to 65 uT), about 50 mm from the battery and 145 mm from the buzzer's magnet. It was on the upper tail lobe until then. No vias and no show-face or In2 tracks within 2 mm of its centre; the ground plane carries on under it, since a hole there would cut the tail's ground off | owner / mine |
| Buzzer: 5 mm MLT-5020 from 3.3 V through R35 and R37 in parallel (50 ohms), switched by an AO3400A, 1N4148W across it | The 8.5 mm buzzer does not fit anywhere far from the compass. The resistors cap the current at 53 mA if firmware leaves the pin high (71 mW in each 125 mW part); two basic 0805s because no 1206 of a useful value is a basic part. The 2N7002 is not specified below 5 V gate drive | mine, after review 4 |
| Gate pull-downs R12 (LED rail switch) and R36 (buzzer) are 4.7k, were 100k | CircuitPython puts a 45k pull-up on every pin the program has not claimed (at start-up, at the prompt, after a crash). Against 100k that puts 2.3 V on the gate: the LED rail and the buzzer would be half on. 4.7k holds it at 0.3 V | mine, after review 4 |
| I2C pull-ups 2.2k, were 4.7k | The bus now runs nose to tail with six devices and the Qwiic socket | mine |
| A grounded guard track below the touch lanes, the length of the body | Keeps the I2C bus and anything else the routers lay along the body off the long touch lines | mine, after review 4 |
| Qwiic connector on the I2C bus, in the tail stem, opening towards the body | Add-on projects later; part used before. The owner, 2026-11-23: it must not open downwards (nothing should dangle from the toy); an add-on goes inside the case, which is then closed again; and it can be dropped if it becomes a routing problem. 5.6 mm in front of it is free of parts for the plug | owner |
| 18 spine LEDs (D1 to D18), not 20; the touch slider and the LED ground strip stop with them | The owner, 2026-11-23: the tail sticks out of the case, and the case ends about where the last two LEDs were. The slider is shortened with the LEDs because the owner wants touch and LEDs to cover the same run. The 18 keep the positions and 7.72 mm pitch they had; D19, D20, C29 and C30 no longer exist (the eye keeps the names D21 and C31) | owner |
| No mounting hole in the tail; two holes left (snout H1, belly H2) | The owner, 2026-11-23: the tail has nothing to mount to | owner |
| The battery is held by the printed case, not tied to the board; no slots in the board | Mine, offered to the owner on 2026-11-23 when he asked (zip-tie or case); not yet answered. Slots would show on the bare face and get in the way of routing. The 36 x 26 mm area stays free of parts so the cell can lie on the board; tracks run under it on every layer, touch lines excepted | mine, open |
| 4 layers: F.Cu parts and tracks, In1 ground plane, In2 tracks and ground fill, B.Cu show face (touch copper, LED ground strip, ground pour) | Changed from 2 layers on 2026-11-23, after the owner said the extra cost was acceptable. On 2 layers with the sensors added, the area beside the module would not close (one connection open after every attempt, tracks taking turns to displace each other), ground under the radio module was 0.2 to 0.3 mm tracks through chopped-up pour, and the show face was covered in tracks. The earlier objection (a plane 0.2 mm behind the touch electrodes would swamp them) is met by cutting the inner layers away behind the touch copper: In1 from 0.3 mm outside it, In2 (the layer 0.2 mm behind it) from 1.5 mm outside it. Cost and build time on 4 layers are NOT priced: see "Check before ordering" | owner / mine |
| The show face takes a track only as a last resort | It is the face people look at. The autorouter is given the parts side and In2 only; the patch router may use the show face at four times the cost of the parts side. Result: 48 mm of signal track on the show face in total | mine |

## Parts

Stock read from each JLCPCB part page on 2026-11-22. Datasheets are in `datasheets/<C-number>.pdf`.
The owner's upload on 2026-11-22 matched every line by C-number.

| Part | C-number | Stock | Class | Lib | Price | KiCad footprint | Unverified |
|---|---|---|---|---|---|---|---|
| OPSCO SK6812SIDE-A side LED x18 | C5378721 | 137,956 | Economic and Standard | ext | $0.11 | DinoLight:LED_SK6812SIDE-A_4.0x1.6mm (own; matches JLCPCB's to 0.02 mm) | page says MSL 3, linked datasheet is the -012 variant and says MSL 5a |
| ESP32-S3-MINI-1-N4R2 (from 2026-11-25; was the N8 below) | C3013941 | 6,219 (2026-11-25) | Standard Only, X-ray | ext | $5.01 | RF_Module:ESP32-S2-MINI-1 (JLCPCB uses one footprint record for both versions) | antenna keepout; IO26 is the PSRAM's |
| ESP32-S3-MINI-1-N8 | C2913206 | 14,793 | Standard Only, X-ray | ext | $4.73 | RF_Module:ESP32-S2-MINI-1 (73 of 73 pads match JLCPCB's, 0.03 mm) | antenna keepout |
| OPSCO SK6812MINI-012 top-emitting LED (eye) | C2886570 | 32,223 (2026-11-23) | Standard Only; no difficulty flag; MSL 3 on the page | ext | $0.097 | DinoLight:LED_SK6812MINI-012_3.7x3.5mm (own, from the datasheet's land pattern; JLCPCB's pads are in the same places with the same numbers, 0.2 to 0.4 mm longer at the toes) | its datasheet says MSL 5a against the page's MSL 3, so baking may still be charged; pin 1 (the chamfered corner, DIN) in the preview |
| LSM6DS3TR-C accelerometer + gyroscope | C967633 | 24,969 | Standard Only | ext | $1.32 | LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y (centres and numbering match the package drawing) | pin 1 in the preview; ST's own land-pattern note not read |
| QMC5883P magnetometer | C2847467 | 2,731 | Standard Only | ext | $1.58 | LGA-16_3x3mm_P0.5mm (pads 0.025 mm further in than the datasheet's, 0.05 larger) | stock is modest and the part page shows 0 available to pre-order: re-check before ordering. Fallback IST8310 (C2683055) needs a new symbol |
| SHT40-AD1B temperature + humidity | C2909890 | 12,766 | Economic and Standard | ext | $1.31 | Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad (exact) | |
| LTR-303ALS-01 light sensor | C364577 | 10,174 | Economic and Standard | ext | $0.55 | Lite-On_LTR-303ALS-01 (exact) | moisture level 3 |
| BMP580 pressure sensor | C22391138 | 11,146 | Standard Only | ext | $1.21 | DinoLight:Bosch_LGA-10_2x2mm_P0.5mm_BMP580 (own: Bosch's pad centres, pads 0.375 x 0.25) | compare with JLCPCB's own footprint at release |
| MLT-5020 buzzer | C94598 | 110,169 | Economic and Standard | ext | $0.39 | DinoLight:Buzzer_MLT-5020 (own, pad for pad as JLCPCB's) | + pad and rotation in the preview; loudness through 50 ohms is an estimate |
| AO3400A N-FET (buzzer) | C20917 | 1,496,353 | Economic and Standard | basic | $0.08 | SOT-23 | |
| 100R 0805 x2, 2.2k 0402 x2, 1 uF 0402, 4.7 uF 0603 | C17408, C25879, C52923, C19666 | millions | Economic and Standard | basic | | | |
| TYPE-C-31-M-12 USB-C, 16 pin | C165948 | 482,527 | Economic and Standard | ext | $0.19 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 (0.12 mm) | board-edge line |
| MCP73831T-2ACI/OT charger | C424093 | 4,058 | Economic and Standard | ext | $0.79 | SOT-23-5 | |
| XC6220B331MR-G regulator | C86534 | 7,846 (2026-11-23) | Economic and Standard | ext | $0.48 | SOT-23-5 (KiCad's pads are the same as its TSOT-23-5; JLCPCB's pads for this part lie inside them) | start-up and wake from sleep on the real board |
| 22 uF 0805 25 V X5R (C3, C5) | C45783 | 4,724,905 (2026-11-23) | Economic and Standard | basic | $0.11 | 0805 | |
| AO3401A P-FET x2 | C15127 | 1,198,551 | Economic and Standard | basic | $0.08 | SOT-23 (0.28 mm) | pinout G1 S2 D3 from the KiCad symbol, not yet from the datasheet |
| 2N7002 N-FET | C8545 | 6,087,828 | Economic and Standard | basic | $0.02 | SOT-23 | same |
| MSK12C02 slide switch | C431540 | 178,549 | Economic and Standard | ext | $0.05 | SW_SPDT_Shouhan_MSK12C02 (0.20 mm) | |
| JST S2B-PH-SM4-TB battery connector | C295747 | 14,733 | Economic and Standard | ext | $0.20 | JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal | which pad is +, against the cell bought |
| USBLC6-2SC6 ESD | C7519 | 41,992 | Economic and Standard | ext | $0.16 | SOT-23-6 | |
| TS-1187A-B-A-B tact switch x2 | C318884 | 712,048 | Economic and Standard | basic | $0.02 | SW_Push_1P1T_XKB_TS-1187A | |
| JST SM04B-SRSS-TB (Qwiic) | C160404 | 4,603 | Economic and Standard | ext | $0.21 | JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal | used before |
| Polyfuse 1.1 A 1812 | C21000 | 38,340 | Economic and Standard | ext | $0.15 | Fuse_1812 (0.28 mm) | used before |
| TLV803SDBZR supervisor | C132016 | 31,902 | Economic and Standard | ext | $0.19 | SOT-23 (0.08 mm) | |
| MPR121QR2 touch controller | C91322 | 662 | Economic and Standard | ext | $2.69 | UQFN-20_3x3mm_P0.4mm (20 of 20 pads, 0.00 mm) | stock is modest: re-check before ordering |
| 75k 1 % 0603 (MPR121 reference) | C23242 | 630,247 | Economic and Standard | basic | | 0603 | 75k in 0402 is an extended part |
| 1N4148W diode | C81598 | 4,479,389 | Economic and Standard | basic | $0.01 | D_SOD-123 | which pad is the cathode, KiCad against JLCPCB (polarised: check in the preview) |
| 0402 R: 330R, 470R, 1k, 4.7k, 5.1k, 10k, 100k, 200k, 1M | C25104, C25117, C11702, C25900, C25905, C25744, C25741, C25764, C26083 | millions | Economic and Standard | basic | | 0402 | 150k, 470k, 68k in 0402 are extended parts: avoided |
| 100 nF 0402, 10 uF 0805 | C1525, C15850 | millions | Economic and Standard | basic | | 0402 / 0805 | |

Not used any more: LIS2DH12TR (C110926), replaced by the LSM6DS3TR-C.

Avoid: SK6812SIDE-A-RVS
C2890037 (Standard Only, MSL 5a); LIS3DHTR C15134 (pre-order).

Cost: the owner's quote for the draft on 2026-11-22: EUR 143 before tax and shipping, 5 assembled. Parts were
$51.78 of that (ESP32 $23.67, side LEDs $9.40, accelerometer $4.44, charger $3.95). The rest is fees.
14 extended part types now (the eye LED, supervisor and touch controller are each one; the diode and new resistor values
are basic parts). The breakdown between board, setup
and extended-part fees is not known.

**TLV803SDBZR (C132016).** TI datasheet: DBZ package 1 GND, 2 RESET (open drain, active low), 3 VDD.
Threshold 2.93 V, hysteresis 40 mV typ, 200 ms delay, 9 uA typ. Drawn with KiCad's TPS3839DBZ symbol
(same pin numbers).

**MPR121QR2 (C91322).** NXP datasheet (rev 4): QFN-20, no exposed pad, 1 IRQ (open collector, active low), 2 SCL, 3 SDA,
4 ADDR (VSS, VDD, SDA or SCL give 0x5A, 0x5B, 0x5C, 0x5D; here tied to SDA = 0x5C), 5 VREG (0.1 uF to VSS when VDD is 2.0 to 3.6 V), 6 VSS, 7 REXT (75k 1 %
to VSS), 8 to 19 ELE0 to ELE11, 20 VDD (0.1 uF). VDD 1.71 to 3.6 V. Supply current (datasheet table 5,
read by the reviewer): 3 uA stopped, which is its state after power-on; 8 / 11 / 17 / 29 uA running at
128 / 64 / 32 / 16 ms sample intervals. Electrode capacitance range 10 pF to over 2000 pF.

**AO3401A (C15127), 2N7002 (C8545).** Both 1 gate, 2 source, 3 drain (AOS datasheet read by the reviewer;
Changjing datasheet text read by me). 2N7002 threshold 1 to 2.5 V.

### Ground truth, per part

**SK6812MINI-012 (C2886570), the eye.** Datasheet SK6812MINI-012 Rev B/0 (`datasheets/C2886570_SK6812mini-012.pdf`),
read 2026-11-23. Body 3.7 x 3.5 x 1.1 mm, lens up. Pins 1 DIN, 2 VDD, 3 DOUT, 4 GND; seen from above: 3 top
left, 2 top right, 4 bottom left, 1 bottom right at the chamfered corner. Land pattern section 6: four unequal
pads (1.5 x 1.3, 2.2 x 1.2, 2.4 x 0.8, 1.3 x 0.9) with 0.6 and 0.5 mm gaps; the footprint follows it. VDD 3.7 to
5.5 V, input high threshold 0.7 x VDD (2.94 V at a full 4.2 V cell: 0.36 V under the 3.3 V logic level; the
spine LEDs' is 0.65 x VDD), 12 mA per colour, 0.6 mA when dark, MSL 5a (JLCPCB's page says MSL 3). Like the
spine LEDs it is run below its 3.7 V minimum as the cell empties: not characterised by the maker.

**SK6812SIDE-A (C5378721).** Datasheet SK6812SIDE-A-012 rev B/2. Body 4.0 long, 1.6 deep, 2.0 tall; it
stands on the board and fires sideways out of the 4.0 x 2.0 face. Pads in a row: 1 DIN, 2 VDD, 3 DOUT,
4 GND. Looking down on the board with the light firing towards you (down the page), the pads read
DIN, VDD, DOUT, GND from left to right, and sit behind the emitting face. JLCPCB's footprint
(LED-SMD_4P-L4.0-W1.6-L) agrees: pads at x = -1.80, -0.45, +0.575, +1.80, body from 0.24 behind the pad
centres to 1.36 in front, window drawn on the front. So with the LEDs firing up out of the spine edge,
data runs right to left in the component-side view. VDD 3.7 to 5.5 V; VIH 0.65 VDD; 12 mA per colour;
0.6 mA static; maker says use 70 % when all three colours are lit. Not verified: operation below 3.7 V
(a LiPo spends much of its life at 3.6 to 3.8 V; expect blue to fade first).

**ESP32-S3-MINI-1-N4R2 (C3013941; the N8, C2913206, until 2026-11-25: same datasheet, same pins except IO26, which the N4R2 keeps for its PSRAM).** Espressif datasheet v1.7 (`datasheets/ESP32-S3-MINI-1_en.pdf`).
65 pins. TOUCH1 to 14 are GPIO1 to 14. ADC1 is GPIO1 to 10. RTC (wake-capable) GPIOs are 0 to 21.
USB D- is GPIO19, D+ is GPIO20. Strapping: GPIO0 (pull-up, boot), GPIO3 (floating), GPIO45, GPIO46
(pull-down). EN must not float. Deep sleep 7 to 8 uA; 18 uA with touch wake at 1 % duty.

The six parts below were read from their datasheets by an independent reader on 2026-11-22 (page
references in its report; PDFs in `datasheets/`), then checked again pin by pin in review 4.

**LSM6DS3TR-C (C967633).** LGA-14, pin 1 top-left, counter-clockwise: 1 SDO/SA0 (GND = 0x6A; no pull-up,
must not float), 2 SDx and 3 SCx (tie to GND), 4 INT1, 5 VDDIO, 6 and 7 GND, 8 VDD, 9 INT2, 10 and 11 NC
(soldered, no net, never grounded), 12 CS (high = I2C), 13 SCL, 14 SDA. 1.71 to 3.6 V; 100 nF on each
supply pin. Interrupts push-pull, active high, driven low at reset. 3 uA powered down, 9 uA in 12.5 Hz
low-power accelerometer mode (can wake the module), 0.9 mA with the gyroscope running. With pin 1 top-left:
+X to the right, +Y up, +Z out of the top.

**QMC5883P (C2847467).** LGA-16, pin 1 top-left, counter-clockwise: 1 SCK, 2 VDD (100 nF), 9 and 11 GND,
10 C1 (4.7 uF low-ESR to GND, mandatory), 16 SDA; all other pads NC. Not the same as the QMC5883L.
2.5 to 3.6 V. Fixed address 0x2C, chip ID 0x80 at register 0. No interrupt pin. 22 uA suspended (there is
no lower state). Datasheet: no copper under or near it on any layer; no ferrous parts nearby on either
side. With pin 1 top-left: +X to the left, +Y down (signs also depend on a register write).

**SHT40-AD1B (C2909890).** DFN-4: 1 SDA, 2 SCL, 3 VDD (100 nF), 4 VSS; the centre die pad is not soldered.
1.08 to 3.6 V. Address 0x44. No copper under it except its pads. No clock stretching: it does not answer
while measuring. 0.1 uA idle. Its heater draws 75 mA: do not use it.

**LTR-303ALS-01 (C364577).** 1 VDD (1 uF), 2 NC, 3 GND, 4 SCL, 5 INT (open drain, unused, open), 6 SDA.
2.4 to 3.6 V, absolute maximum 3.8 V. Address 0x29. 5 uA standby. Wait 100 ms after power-up.

**BMP580 (C22391138).** LGA-10, counter-clockwise from pin 1 top-left: 1 VDDIO, 2 SCK, 3 VSS, 4 SDI (SDA),
5 SDO (GND = 0x46; must not float), 6 CSB (to VDDIO: low at power-up locks I2C out until the next power
cycle), 7 INT (grounded; disabled at reset), 8 and 9 VSS, 10 VDD. 100 nF on each supply. 1.71 to 3.6 V.
0.55 uA in deep standby. Vent in the lid: no wash, nothing over it.

**MLT-5020 (C94598).** Passive magnetic buzzer, 12 +/- 3 ohms, 3 V rated (2 to 4 V), 100 mA max, 4 kHz,
75 dB at 10 cm at rated drive. Pad 1 +, pad 2 -, third terminal unlabelled and left without a net. The
corner with no terminal is chamfered. Sound port on top.

**AO3400A (C20917).** AOS datasheet: threshold 0.65 to 1.45 V, under 48 milliohms at 2.5 V gate drive,
gate limit +/-12 V. SOT-23, 1 gate, 2 source, 3 drain (KiCad symbol; the datasheet drawing agrees).

**XC6220B331MR-G (C86534), from `datasheets/C86534_XC6220.pdf`.** SOT-25: 1 VIN, 2 VSS, 3 CE, 4 NC,
5 VOUT. VIN 1.6 to 6.0 V (absolute max 6.5 V). 1 A. Dropout at 3.0 to 3.5 V out: 60 mV typ, 95 mV max at
300 mA. CE on from 1.2 V, off below 0.4 V; the B type has no pull-down on CE (R5 is ours) and discharges
the output through about 460 ohms when off. Supply current 8 uA typ (18 max) below about 1 mA of load,
50 uA typ (108 max) above 5 to 10 mA: it changes mode by itself. Stand-by 0.01 uA typ, 0.1 max. Output
capacitor for 3.0 to 3.5 V out: 4.7 uF with 10 or 22 uF at the input, 47 uF with 4.7 uF at the input.
Inrush limited to 700 mA; fold-back limit, about 180 mA into a short. Replaced the RT9080-33GJ5 (C841192:
dropout 0.31 V typ, 0.53 V max at 600 mA; `datasheets/C841192.pdf`) on 2026-11-24.

**MCP73831T-2ACI/OT (C424093).** SOT-23-5: 1 STAT, 2 VSS, 3 VBAT, 4 VDD, 5 PROG. 4.7 uF minimum on VDD.
Charge current 1000 V / RPROG. STAT is a three-state output (datasheet section 3).

**MSK12C02 (C431540).** Maker's drawing: pin 2 is the common, joined to 1 or 3 by the slider; 4 is the
frame. Signal pins are on the side away from the knob. Rated 50 mA at 12 V.

## Check before ordering

| Item | What to check |
|---|---|
| Four layers: price and build time | Not priced. The owner's EUR 143 quote was for a 2-layer draft. On the order form choose 4 layers, 1.6 mm; the upload quote shows the price and the build time, which matters against the deadline |
| Four layers: JLCPCB's limits | Read from jlcpcb.com/capabilities/pcb-capabilities on 2026-11-23: multilayer track and gap 0.09 mm minimum (board uses 0.15); via hole 0.3 mm in a 0.5 mm pad carries no surcharge (surcharge is for 0.25 mm holes and under, or pads under 0.45 mm); via hole to inner-layer copper 0.2 mm minimum (board: 0.25 or more); via hole to hole 0.2 mm (board: 0.25); inner copper 0.5 oz by default. The stack-up choice on the order form was not looked at: the board needs no controlled impedance |
| Show-face silkscreen | JLCPCB's silkscreen limits, read from its capabilities page ("Legend") on 2026-11-24: line 0.15 mm or wider, text 1.0 mm or taller, stroke to height 1:6 preferred, the same for "hollow-carved" characters, 0.15 mm from a pad. Look at the back in JLCPCB's Gerber viewer: white with the drawing in green. Not verified: how evenly a flood this large prints, and how the 444 tented via holes look under it (expect small dimples) |
| Order form, from the release review | Via covering: tented, as the Gerbers are. If JLCPCB queries the USB socket's two short slots (1.2 mm long, 0.6 mm wide), they are as the connector's drawing asks |
| Order number on the board | JLCPCB prints its order number somewhere in the silkscreen unless the order form says otherwise. On the form choose to leave the mark off, or to place it (then a marker text goes on the parts side). From memory, not read from the form |
| New parts in the placement preview | Pin 1 and rotation of U5, U8, U9, U10, U11; the buzzer's + pad (BZ1); D24's cathode; Q4 |
| QMC5883P stock | 2,731 on 2026-11-22 but the page showed 0 available to pre-order: look again on the day |
| No-wash parts | SHT40, BMP580 and the buzzer have openings: confirm JLCPCB's process does not wash or coat the board |
| Parts matched by position | J1, J2, J3, SW1, SW2, SW3, U4 in the placement preview (pad names differ between the libraries) |
| Side LED direction | In JLCPCB's placement preview: every spine LED's window faces off the board. The eye LED D21: its chamfered corner (pin 1, DIN) is at the pad marked with the silkscreen dot |
| Parts at the edge of an irregular board | From a web search of JLCPCB's help pages on 2026-11-22 (figures differ between their pages; not read in full): Standard assembly requires edge rails and fiducials; JLCPCB adds 5 mm rails if asked; part bodies should be 2.5 mm or more from the board edge unless rails provide the clearance; irregular outlines are held to the rails by tabs or mouse bites (4 to 5 mm wide); parts overhanging the outline need a slot in the rail. Consequences to settle at placement: where the tabs may attach (not on the spine edge between LEDs, not at the USB socket or switch), whether to draw our own panel to control that, and which order-form option the owner picks for rails. the owner's draft upload raised nothing he mentioned |
| LiPo connector polarity | The cell actually bought, against the + pad of the footprint. Jumpers SJ1, SJ2 swap it. Silkscreen + and - at J2, and "unplug cell; cut both, then bridge both" at the jumpers |
| The cell itself | Must be a protected cell (its own cut-off circuit), JST-PH 2 mm, 500 mAh or more: the charger's 213 mA is too much for cells under about 250 mAh |
| Qwiic pin 1 | Footprint pad 1 against a real Qwiic cable: 1 GND, 2 3V3, 3 SDA, 4 SCL |
| Antenna | Module antenna end at a board edge with the keepout the datasheet asks for |
| FET pinouts | AO3401A and 2N7002 gate, source, drain against their datasheets |

## Reviews

### Review 1, 2026-11-22: netlist against datasheets (independent reader)

Verdict: no blocker. Every IC and connector pin matched its datasheet; every netlist pin has a pad.

Fixed:

| Finding | Fix |
|---|---|
| A deeply flat cell could never recharge: the charger trickles 21 mA below 2.79 V and USB always wakes the module, which draws more | U6 TLV803S holds EN low below 2.93 V; R16 to 100k so that state draws 30 uA |
| Polarity jumpers could short the cell ahead of the fuse (one changed and not the other, or three pads blobbed) | F1 moved to the connector pin, ahead of the jumpers |
| CHG_STAT and VBUS_DET highs not guaranteed at low USB voltage (VBUS / 2 against VIH 2.475 V) | R9, R19 to 200k: 2.93 V at 4.4 V, 3.5 V at 5.25 V |
| LED rail turn-on: estimated 2 A, 100 us inrush with C10 gate to source | C10 moved gate to drain: about 60 mA over 1.5 ms |
| Off state held by 1M against switch leakage | R4, R5 to 200k (reviewer suggested 470k, which is an extended part) |
| C3, C4 1 uF 0402 under bias give less than the regulator's 1 uF | Both to 10 uF 0805 |
| Few test points for a board with no second spin | TP12 EN, TP13 LED_EN, TP14 LDO_EN, TP15 CHG_STAT, TP16 EYE_DIN |
| 2N7002 pinout unverified | Read from the datasheet: 1 G, 2 S, 3 D |

Left as is:

| Finding | Why |
|---|---|
| No hardware under-voltage cut-off; over-discharge protection is firmware plus the cell's own circuit | U6 stops the module below about 2.95 V but the cell can rebound and restart it, so it is not a true cut-off. The cell must be a protected one: now a purchase requirement |
| Reversed cell with USB plugged in is drained at 21 mA through Q1 rather than blocked | No cheap fix. Nothing is damaged. Silkscreen + and - at J2; check with a meter before the first USB plug |
| Full-white current (about 0.8 A plus the module) is at the fuse's hold rating and sags VLED by 0.3 to 0.5 V | Firmware cap: about 0.3 A total for the LEDs |
| Charger dissipates about 0.5 W at the start of fast charge and will fold back | Harmless; give U2 pin 2 copper and keep it away from the cell (layout) |
| VBAT_SENSE feeds about 4 uA into GPIO10 when the regulator is off | Harmless |
| VBUS_DET stays high 1 to 2 s after unplugging | Firmware debounce |

Needs a decision: none. The owner approved the supervisor U6 on 2026-11-22.

Not verified by the reviewer: Qwiic pad-1 side against a cable; polyfuse figures (from the LCSC page);
module current between 2.4 and 2.8 V; the inrush figure (hand estimate); CircuitPython behaviours.

### Review 3, 2026-11-22: the touch controller change (same reviewer, changed items only)

Verdict: no blocker and no should-fix. U7 is wired as the datasheet's 2.0 to 3.6 V circuit; its package has
no exposed pad and matches the footprint; address 0x5A does not clash with the accelerometer (0x19); 470R
in series is negligible to a constant-current measurement; D23, R32 and C32 were applied correctly and
VBUS_DET now reads a clean low with the switch on and no USB.

Fixed:

| Finding | Fix |
|---|---|
| No test point on TOUCH_IRQ | TP17 added |

Left as is:

| Finding | Why |
|---|---|
| IRQ stays low until the touch status is read; sleeping with it low draws 33 uA through R34 and wakes at once | Firmware: read the status before sleeping; wake on GPIO1 low |
| MPR121 scans on its own clock, so it cannot be synchronised with LED frames; supply steps out of regulation can look like touches | Firmware: 10 or more first-filter samples, debounce, ignore touch when the battery is low. Layout: keep LED data and VLED tracks from running under or beside electrode tracks |
| Unplugging USB takes 1.6 to 3.7 s to read low on VBUS_DET (C1 discharging through 300k) | Firmware debounce. Lower divider values would need extended parts |
| Several Qwiic add-ons also use 0x5A | Settled after the review: ADDR is now tied to SDA, the pin beside it, giving 0x5C. That also removed the one awkward connection in the chip's fan-out |
| U7 has no reset pin | Firmware sends the soft reset (register 0x80) at start-up |
| The module's former touch pins are open pads | Harmless; firmware can park them with a pull |
| Electrode tracks up to 150 mm are themselves touch-sensitive, and a moving LiPo pouch next to an electrode reads as touch | Layout: thin electrode tracks away from other zones, electrodes and their tracks clear of the battery area |

Not verified by the reviewer: electrode capacitance (hand estimates); the supply-step and LED-coupling
effects (reasoning, not measured); CircuitPython's wake rules.

### Re-review of the changes above, 2026-11-22 (same reviewer, changed items only)

Fixed:

| Finding | Fix |
|---|---|
| Regression from my own change: with SW1 on and no USB, R4 (200k) fed the battery back onto VBUS, leaving VBUS at about 2 V and VBUS_DET between the module's guaranteed low and high. "USB present" could read true with nothing plugged in, and a USB-C charger might refuse to start | D23 1N4148W in series with R4, anode on VBUS. USB alone still gives about 1.9 to 2.4 V on LDO_EN against a 0.9 V threshold |
| U6 discharged C32 (1 uF) through its open-drain output on every trip: estimated 10 to 25 mA peak against a 5 mA limit | C32 to 100 nF, R32 1k in series with U6's output (peak 3.3 mA). EN now rises in about 10 ms after U6's own 200 ms delay |

Left as is:

| Finding | Why |
|---|---|
| Standing current with SW1 on and the module asleep is about 45 to 50 uA (was about 22 to 25 uA before the review fixes) | Buys a firm off state and the supervisor. About a year from a full 500 mAh cell. 470k for R4 / R5 would save 12 uA but is an extended part |
| U6 now decides where the toy cuts out under load: about 3.0 to 3.1 V idle, 3.2 to 3.45 V in a Wi-Fi burst, higher with bright LEDs. Hysteresis is only 40 mV, so a firmware that re-applies the load reboots about 3 times a second | Firmware: read VBAT_SENSE at start-up before lighting anything and sleep below about 3.5 V; keep the LED cap |
| Plugging the cell in (or USB with no cell) turns Q2 on for 40 to 50 ms through C10 | Harmless; a brief random flash is possible because the data pins float then |
| Rail turn-off is slow (about 60 ms) with Q2 in its linear region | About 15 mJ worst case, fine for SOT-23. Firmware: blank the LEDs first |
| VBUS_DET and CHG_STAT reach 3.67 V at a 5.5 V supply, 70 mV over the module's limit | Through 67k: under 1 uA |
| TP13 (LED_EN) is the gate of Q3 behind 100k while the module is asleep | Keep it on the parts side under the cover (all test points are) |

Checked and found correct by the reviewer: TLV803 DBZ pinout and open-drain output from its datasheet;
the moved fuse covers every jumper state; C10 gate-to-drain in every transition; 2N7002 and AO3401A
pinouts from their datasheets; pad names for all parts.

Not verified: how real USB-C chargers react to voltage on VBUS (now moot with D23); the Q2 transition
figures are hand calculations; SK6812 behaviour during the plug-in blip; the last three edits (D23, R32,
C32) have not had a third independent pass.

### Review 4, 2026-11-22: the sensors, buzzer and other changes of the day (fresh independent reader)

Scope: the six new parts and their support parts, the buzzer drive, the 2.2k pull-ups, spine data on IO11,
the touch channel order, and the touch controller's address tie (unreviewed until now). Read against the
datasheets in `datasheets/`. Verdict: no blocker; every pin of U5, U8, U9, U10, U11, BZ1, Q4 and D24
matches its datasheet; six distinct I2C addresses.

| Finding | Severity | Decision |
|---|---|---|
| Gate pull-downs of 100k (R36 new, R12 existing) lose to the 45k pull-up CircuitPython puts on unclaimed pins: buzzer and LED rail half on at start-up, at the prompt and after a crash | should-fix | Fixed: both 4.7k (0.3 V at the gate) |
| Buzzer through 100R gets about 0.35 V, well under its 2 V minimum, so quiet; and a lower resistor for "louder" would overheat an 0805 if the pin stuck high; the 2N7002 is not specified at 3.3 V gate drive | should-fix | Fixed: two 100R 0805 in parallel (53 mA and 71 mW each if stuck), AO3400A. Loudness is still an estimate until built |
| Placement rules the new parts bring: compass away from the buzzer, LED rail, cell and steel; I2C off the touch lanes; no pour under the SHT40; openings in the cover | should-fix | Done in placement and routing: compass on the tail lobe 180 mm from the buzzer with no copper round it; guard track below the touch lanes; pour and show-face tracks kept away from U8 and U9. The cover openings are in "For the case" |
| BMP580 INT is grounded: a driver that enables it as push-pull would short the output | note | Left grounded as the datasheet allows; firmware note added |
| BMP580 leaves I2C if it ever sees address 0x7E | note | Firmware note |
| BMP580 footprint: stock ST footprint leaves 0.125 mm between corner pads; own footprint is right, pads could reach further out | note | Own footprint used, pads lengthened outward by 0.075 mm |
| Sleep current: the additions add 26 to 31 uA (22 of it the compass), about 75 to 80 uA in all | note | Accepted: about nine months from a 500 mAh cell |
| After a brown-out the sensors keep their state while the module resets | note | Firmware: soft-reset every sensor at start-up and clock SCL nine times first |
| A Qwiic add-on with its own 2.2k pull-ups halves the bus pull-up; two take it below the light sensor's 1k minimum | note | Recorded under "For firmware" |
| ACC_INT pins are driven low by U5 while CircuitPython pulls unclaimed pins up: 73 uA each wasted | note | Firmware: claim them as inputs with no pull |
| E10 and E12 value texts were swapped (nets right) | note | Fixed |
| C40 loses 20 to 30 % under bias (from memory) | note | Left at 4.7 uF 0603: a bigger capacitor is more nickel beside the compass |

Not verified by the reviewer: the QMC5883P's sink current (not in its datasheet); the ESP32-S3's pin state
in reset; whether CircuitPython's pull-ups persist in deep sleep; what the CircuitPython drivers do by
default; the buzzer's inductance and real loudness. The changes made after this review (the 4.7k
pull-downs, the buzzer resistors and FET) were made as the reviewer specified and checked by the
netlist comparison, not by another independent pass.

### Layout review (the skill's review 2), 2026-11-23: the routed four-layer board (fresh independent reader)

Read the board file of 14:59 on 2026-11-23 (the first complete four-layer route) with the notes, read-only.
Verdict: not ready to order; nothing found that stops the board working. Its numbers were measured on a
copy of the board; I have checked the cause of findings 1, 2, 9 and 13 in the tools, not re-measured the rest.

| # | Level | Finding | Decision |
|---|---|---|---|
| 1 | BLOCKER | Three ground vias in or against J1's plated shell slots: (120.46, 76.78) inside a slot, (128.85, 72.20) 0.02 mm from one, (128.46, 76.78) 0.41 mm from one. KiCad's DRC does not test same-net holes | Fixed in the tools: the stitcher keeps 1 mm from the pad of any drilled hole; the patch router keeps a new via 0.25 mm off the copper of its own net's plated pads and hole-to-hole from its own vias |
| 2 | SHOULD | The tail touch line was no longer in its lane: `patch_route.py --tidy` took the scripted lane out (a line that joins a lane part-way made the whole lane look like a dead end) and the router re-ran it 200 mm through the body, across the battery area and beside EYE_DIN, SCL and SDA | Fixed: tidying keeps a scripted track that anything joins part-way. The tail line now runs by script all the way from its lane to the tail pad's plated hole, with a 0.6 mm parts-side keep-out either side (other tracks cross on In2). The front flipper's line leaves its lane 2 mm further towards the head, 1 mm clear of the battery area |
| 3 | SHOULD | Battery and LED current through single vias and 0.4 mm tracks on In2 (half-ounce): BAT_RAW 4.5 mm, +BATT 16.8 mm, VLED 24.9 mm, with no parallel path. Fine at 0.3 A; at 0.8 A the IPC formula gives about 55 C rise | Partly fixed in the tools: supply nets now pay 10 mm for a via (was 3), so they stay on the parts side where they can; supply tracks on In2 are widened to 0.8 or 0.6 mm wherever DRC allows (`--fatten`). Vias are not doubled. Open for the owner: 1 oz inner copper on the order form would halve what is left; firmware should cap LED current (see For firmware) |
| 4 | SHOULD | SCL test point TP10 and its track sat behind the rear-flipper pad with no plane between | Fixed: TP9 moved into the charger cluster and TP10 into the regulator cluster |
| 5 | SHOULD | Outside the lanes, SDA runs beside the snout pad's line for about 8 mm at 0.2 to 0.5 mm, and BUZZ beside a touch line for 1.5 mm at 0.18 mm; the snout line passes H1 at 2.82 mm | Left: the routes will differ after the re-route; no rule keeps other nets off the snout and flipper lines. To look at again on the final board; otherwise tune thresholds in firmware. A metal screw at H1 would add to the snout channel |
| 6 | NOTE | Pour-free areas stopped flush with the two ends of the slider (In1 and In2 fill at 0 mm instead of 0.3 and 1.5) | Fixed: the areas and the routers' keep-outs now run on past both ends |
| 7 | NOTE | The LED ground strip on the show face is 0.45 mm from the slider's upper edge for its whole length | Left: by design. The strip is the LEDs' ground return and sits between the LEDs and the slider; it adds the same standing capacitance to all eight segments |
| 8 | NOTE | 11 mm2 of the front-flipper pad lay inside the module's antenna keep-out | Fixed: touch copper is clipped 0.3 mm outside the keep-out. The pad loses that corner |
| 9 | NOTE | No stitching vias in the tail lobe or the front flipper: the stitcher wanted ground on all four layers | Fixed: a via goes where the plane and the show-face pour are present and the other two layers have ground or no copper nearby |
| 10 | NOTE | Four pieces of ground fill (three on In2, one on the parts side) hung on one via each | Expected to go with fix 9; to check on the final board |
| 11 | NOTE | The 3.3 V feed to the module was 121.6 mm, 204 milliohm, through 12 vias (the notes said 0.12 ohm) | Notes corrected. 71 mV at 350 mA; C5 and C6 are at the module's pin. Fix 3 should shorten it |
| 12 | NOTE | USB D+ 64.9 mm / 7 vias, D- 61.8 mm / 6 vias, together for 20 mm: fine at full speed. The protection array U1 hangs on a 10 mm stub with one ground via | Left |
| 13 | NOTE | About 30 of the new plane vias touched the edge of their own pad | Fixed: a via stands 0.1 mm off the pad it serves |
| 14 | NOTE | U5's corner pads 5 (+3V3) and 6 (GND) are 0.15 mm apart (library footprint) | Left; look at that corner in JLCPCB's preview and on the boards |
| 15 | NOTE | R19 and U5 are 0.55 to 0.68 mm from the outline at the rear flipper root | Left; keep panel tabs away from board (86 to 90, 64 to 70) |
| 16 | NOTE | The two "does not match library" warnings (C21, D8) are a pad angle stored as 360 instead of 0 | Harmless |

Checked and found fine by the reviewer: the In1 plane is one piece with nothing but plane on it, 92 % cover
under the module with 25 ground vias; every net one piece on an independent check; all 147 surface ground
pads reach a via by track; hole spacings (apart from finding 1); no In2 or show-face tracks behind touch
copper; supplies on the parts side; the LED ground return; the quiet areas at U8 and U9; no courtyard clashes;
test points reachable. Not checked by anyone: Gerbers and placement file (none yet), part heights and case
fit, paste and mask-dam handling, antenna performance, silkscreen. The touch-coupling figures are hand
estimates. Reviewer's facts from memory, not looked up: 0.2 mm prepreg in JLCPCB's standard 4-layer stack,
the IPC-2221 formula, MPR121 behaviour.

The board was re-routed from scratch after these fixes (placement changed), so the result needs its own
rule check, audit and a re-read of what changed: see State.

### boardlint review, sent by the owner 2026-11-24

An automated design check (github.com/mattvenn/boardlint) with its findings triaged by an AI model, run
on commits 4da182c and eb2fd13: the schematic of the present design, but the two-layer routing of the day
before. Its layout findings are therefore checked here against the present four-layer board. It reproduced
every pin assignment and I2C address from the design files.

| # | Finding | On the present board | Decision |
|---|---|---|---|
| 1 | 3.3 V at the module falls below 3.0 V at a 356 mA transmit peak unless the cell is well charged (3.06 V from a 3.6 V cell; its figures: 0.45 ohm from cell to regulator, RT9080 at its maximum dropout, 185 milliohm of track) | True. The feed is 243 milliohm today | Regulator changed to the XC6220B331 and C5 to 22 uF (see Decisions). With the review's own source resistance and both parts at their datasheet maximum, the module gets 3.21 V from a 3.6 V cell (was 3.04 V) and stays above 3.0 V down to a 3.36 V cell (was 3.56 V). Not changed: the regulator's position and the feed's width |
| 2 | Fuse F1 holds 1.1 A; full white while transmitting could draw 1.27 A (21 LEDs) | 19 LEDs now: 0.83 A + 0.36 A = 1.18 A | Firmware limit on LED current, already required (see For firmware) |
| 3 | 0.4 mm battery-path tracks for up to 1.27 A | Re-routed: +BATT from Q1 to the regulator computes to 17 milliohm. The LED feed still has 0.4 mm pieces on the 0.5 oz inner layer (see Routing) | Same firmware limit; 1 oz inner copper on the order form is the owner's choice |
| 4 | Nearest 100 nF 8 to 11 mm from U5, U6, U7 | Gone: capacitors are placed with their chips; `board_audit.py` finds no such case (its two decoupling findings are U1's VBUS pin and the battery-sense pin) | None needed |
| 5 | USB D+ / D- beside touch lines for 25 to 33 mm, down to 0.6 mm | Re-routed: closest 0.72 mm edge to edge; 4 mm of run within 1 mm and 12 mm within 2 mm, all beside the front-flipper line | Left. Matters only while USB is active |
| 6 | SK6812 specified from 3.7 V; the rail goes to 3.0 V | Known | Firmware sleeps at about 3.5 V; dim or off-colour LEDs below 3.7 V accepted |
| 7 | Spine LED data line had no ground under half its length | In1 is now a ground plane | None needed |
| 8 | Buzzer gets about 0.63 V at DC (50 ohms in series with its 12 ohm coil); it is specified from 2 V | True; loudness was already an estimate | Left as designed, for the owner: R35 and R37 could be a lower value on the same pads (two 47 ohm: about 1.1 V, 96 mA if the pin sticks high, at the edge of the parts' ratings). Louder only by measurement |
| 9 | Its description of the board named the module ESP32-S2-MINI-1 | The part is ESP32-S3-MINI-1-N8; the KiCad footprint is named ESP32-S2-MINI-1 (same pads, checked against JLCPCB's) | None needed |

The regulator change is a part and value change on unchanged pads: schematic regenerated (86 nets, no
differences), board values updated in place, rule check with parity unchanged (0 unconnected, no value or
footprint mismatch). Not verified: the XC6220's behaviour at start-up into this board's capacitance, on wake
from sleep (it is in its low-current mode while the module sleeps), and with the cell at the end of 150 mm
of lead; none of this has had an independent read.

### Re-read of the re-routed board and the draft3 upload set, 2026-11-23 (fresh independent reader)

Read the board as pushed in commit e8cc24e (third four-layer route) and `fab/draft3` as first made. Verdict:
no blocker; three should-fix. The reader's numbers were measured on its own copy; I have not re-measured them.

| # | Level | Finding | Decision |
|---|---|---|---|
| S1 | SHOULD | LED current through long 0.4 mm tracks on In2: +BATT Q1 to Q2 83 mm (225 milliohm), VLED feed 36 mm (112 milliohm), no parallel path; about 42 C rise at 0.7 A by the IPC formula (from memory). The widening step had widened almost nothing: it gave up on a whole track if any point was tight | Partly fixed: `--fatten` now cuts tracks into 2 mm pieces first. Supply tracks on In2 are now 107 mm at 0.8 mm, 17 mm at 0.6 mm, 144 mm at 0.4 mm (+BATT: 39 mm at 0.8, 48 at 0.4; VLED: 19 at 0.8, 24 at 0.4). Not re-measured as resistance. Still open for the owner: 1 oz inner copper; keep the firmware cap of 0.3 A |
| S1b | SHOULD | The LED rail is fed through C11's pad and a 0.25 mm neck 2.9 mm long (5.8 milliohm, about 6 C at 0.7 A); the rail's own head end is a 7.5 mm dead spur | Left: thermally fine by the reader's figures. Untidy; to tidy if the head end is routed again |
| S1c | SHOULD | All battery return current through one ground via at SJ2.1 | Fixed: two more ground vias at SJ2.1 |
| S2 | SHOULD | U9's placement coordinate 0.16 mm off: `jlc_cpl.py` paired JLCPCB's centre pad with pad 2. Rotation 0 is right (JLCPCB pads 1 to 4 land on SDA, SCL, +3V3, GND) | Fixed in `tools/make_upload.sh`: U9 is placed at its footprint origin, (19.000, -35.600) |
| S3 | SHOULD | Signal nets beside touch lines outside the lanes: BUZZ 0.23 mm from the snout line for 7 mm on In2; TOUCH_IRQ, CHG_STAT_5V, SPINE_DATA and several vias at 0.2 to 0.4 mm. The front-flipper line ran 0.75 mm outside the battery area for 18 mm, then 0.75 mm inside it for 2.2 mm | Fixed: `patch_route.py` now keeps 0.5 mm between a touch line and any track or via of a signal net (ground and supplies exempt; pads keep 0.15 mm), and keeps touch lines 0.6 mm outside the battery area. `tools/clear_touch_neighbours.py` took out 53 offending pieces, which were laid again; it now finds none. To make room at the compass, the tail line's run to its pad starts at its lane's end instead of a stub below the band |
| N1 | NOTE | Under U11: the 3.3 V link pad 1 to pad 6 is 0.227 mm from pads 2 and 7, no current, not a bridging risk. From the reader's memory, Bosch and ST advise against copper under LGA sensors because of stress offsets | Left: the pressure reading may carry a small fixed offset. A toy |
| N5 | NOTE | Copper behind touch pads with no plane between: the two buttons' pads behind the snout pad; R18.2 (SCL) overlaps the rear-flipper pad by 0.36 mm2; 17 mm of the snout line on In2 lies in the pour-free moat and senses like the pad | Left; known weakness (see Placement). The routes near the snout changed again after the re-read |
| N6 | NOTE | Pieces of ground fill on one via each (three on In2, several on the parts side); none with no via | Left |
| N7 | NOTE | One ground via inside module pad U4.61 at (176.46, 56.78); 64 vias 0.10 to 0.15 mm from their own pad, mask web 0.1 mm | Left. Ask JLCPCB's DFM if it objects |
| N8 | NOTE | R10's pad is 0.55 mm from the outline at (89.1, 65.3) | Left; keep panel tabs away from there |
| N9 | NOTE | Two BOM lines share C318884 (RESET, BOOT). Inner layers are named .g1 and .g2: check in JLCPCB's viewer that In1, the plane, is layer 2 | For the owner at upload |
| N10 | NOTE | The cached JLCPCB / EasyEDA footprint files (`draft/.jlc_cache`) carry a licence notice addressed to AI tools, asking that outputs citing the library credit "JLCEDA/EasyEDA Official Library" and link lceda.cn and easyeda.com | Not acted on; put to the owner |

Found right by the reader: finding 1 of the first review (no via in or against a J1 slot; smallest hole-to-hole
0.39 mm); all eleven touch lines in their lanes; the eye LED footprint against its datasheet, and its nets;
the compass's pins and surroundings; J3's pin order (1 GND, 2 3V3, 3 SDA, 4 SCL) and direction, with 5.6 mm
clear in front; the tail's ground (In1 solid through the stem); In1 cover 94 to 99 % under the module,
regulator, charger and battery; the Gerbers (each copper layer compared with the board, inner layers present
and not swapped; drill counts agree); the BOM (every fitted part once, every part number as in the table);
and every rotation in the placement file, by laying JLCPCB's own footprint at the file's position and
rotation and comparing pad numbers and pin names with the board's nets. What that does not prove: that
JLCPCB's reels are oriented as its library draws them, and its rotation sign (from the reader's memory).
The placement preview remains the last check, especially the side LEDs, D21, U9 and J2.

The fixes above changed the routing round the head, the tail stem and the battery corner after the re-read.
Those changes have been rule-checked and audited, not independently read.

### Release review, 2026-11-24: `fab/v0.1` and everything changed since the re-read (fresh independent reader)

Read the upload set as first packaged (zip md5 da43ef1e...) and the board changes since commit e8cc24e.
Verdict: no blocker.

| # | Level | Finding | Decision |
|---|---|---|---|
| S1 | SHOULD | ACC_INT1 (motion interrupt 1, 0.15 mm, parts side) was re-laid by the touch-spacing fix as a 21 mm loop: 13.4 mm of it lies behind the rear-flipper electrode E11 with no plane between, it passes E11's anchor pad at 0.22 mm, and the old route was left as a 4.6 mm dead stub with a via and a show-face piece 0.5 mm from the rear-flipper touch line | Stub removed (13 track pieces and the via at board (92.38, 70.10); pours refilled; rule check and audit otherwise unchanged). The loop is left: the direct way from U5 pin 4 is closed by the rear-flipper line's own via at (89.0, 69.76), 0.3 mm below the chip's pad row, and moving a touch via now is the greater risk. My estimate of the coupling: 0.1 to 0.2 pF. Firmware keeps INT1 still while touch is in use (see For firmware) |
| S2 | SHOULD | Parts-side silkscreen unfinished: the text still says DRAFT; no + / - at J2 and no instruction at SJ1 / SJ2, which "Check before ordering" relies on; no labels on the test points | + and - added inside the battery rectangle at the connector's mouth, in line with its two pins (pad 1 is +), and four lines of instruction in the rectangle (`tools/silkscreen.py`, FRONT). The DRAFT text stays: the owner, 2026-11-24, "definitely leave the info on the parts side". Test points are not labelled on the board: TP1 to TP17 are, in order, the nets in `TESTPOINTS` in `tools/design_spec.py` |
| N1 | NOTE | Supply paths by the reader's own network solve: battery connector to Q1 45 milliohm; Q1 to the regulator 16; Q1 to the LED switch 179 (was 225), of which 112 is 45 mm of 0.4 mm track on In2; LED switch to the far LED 206; regulator to the module 232 (the notes' 243 confirmed); the 0.25 mm neck on VLED is still there | Known. Firmware LED limit; 1 oz inner copper is the owner's choice on the order form |
| N2 | NOTE | XC6220B331 checked against its datasheet pin by pin: pins, enable levels in all three states (switch on, USB only, off), input range, capacitor table, start-up. All correct. Not settled by the datasheet: stability with about 40 uF spread along a 0.23 ohm feed (its charts stop at 22 uF). After USB is unplugged with the switch off, the enable pin drifts through its undefined band for up to a second, so the rail may chatter on the way down | Accepted. Try both on the first board |
| N3 | NOTE | JLCPCB's pads for C86534 lie wholly inside the board's; rotation 0 puts its pins 1 to 5 on pads 1 to 5 | None needed |
| N4 | NOTE | Back silkscreen Gerber, rasterised: ink 84 % of the board, 0.48 mm bare rim, no ink on any opening (nearest 0.27 mm), no ink under 0.15 mm, six slivers of 0.15 to 0.20 mm, no bare line under 0.20 mm; seven isolated dots of about 0.4 x 0.3 mm at the slider teeth's tips may print or drop out; 401 tented via holes under ink | Accepted: cosmetic |
| N5 | NOTE | Parts-side silkscreen: nothing prints on pads; only 25 references show; BZ1 and U11 are 0.8 mm tall with 0.12 mm strokes, under JLCPCB's limits; 317 footprint lines are 0.10 to 0.12 mm (library defaults) | Left: the parts side is inside the case |
| N6 | NOTE | Copper behind touch pads with no plane between: snout +3V3 17 mm, BOOT, EN, SCL, BUZ_P and the buttons' pads; rear flipper ACC_INT1 13.4 mm (S1), SCL 1 mm; spine 8 SCL 1.2 mm | Known |
| N7 | NOTE | The rear-flipper touch line runs 8.9 mm on the show face (was 2.5 mm): a finger there reads as rear flipper | Accepted: it is beside that flipper |
| N8 | NOTE | Order form: vias are tented both sides in the Gerbers; J1's two short shell slots are 1.2 mm long with a 0.6 mm tool (exactly 2:1) and may draw a query | See "Check before ordering" |

Checked and found fine by the reader: every file in the zip against a fresh export; layer names and order
(In1 one solid region, In2 tracks); a closed outline of 225.59 x 72.60 mm; drill counts; paste only on fitted
SMD pads; mask openings; the jumpers' default bridges in copper; BOM against the schematic and JLCPCB's part
titles; all 122 placement rows by laying JLCPCB's own footprint at the file's position and rotation (pad
numbers and pin names agree for every polarised or keyed part; side LEDs face off the edge); the rule check
reproduced; schematic against board, zero differences; no signal within 0.5 mm of a touch line except at the
touch chip; nothing within 2 mm of the compass but its own nets. Not checked: stock on the day, how JLCPCB's
reels are oriented, its rotation sign (assumed, as `jlc_cpl.py` does), how the white flood prints, panel
rails and tabs, the regulator on the real board, anything measured.

## Placement (2026-11-23), no mechanical sign-off yet

Where things are, seen from the parts side (head on the right):

| Area | What is there |
|---|---|
| Spine edge | D1 to D18, firing off the edge, D1 at the head; each LED's 100 nF 3.7 mm inboard. The run stops 15 mm short of the tail base |
| Below the LEDs | The LED supply rail, then the eleven touch lines in lanes and a grounded guard track |
| Nose | Light sensor U10 and its capacitor |
| Head | Eye LED D21 (top-emitting, no hole in the board); RESET and BOOT buttons; buzzer BZ1 and its drive in the jaw; touch controller U7 and the 12 series resistors between the buttons and the module |
| Neck | Module U4, antenna end at the throat edge |
| Between module and battery | LED rail switch (Q2, Q3), supervisor, EN parts, sense dividers, eight test points |
| Mid body | Battery area 36 x 26 mm, kept free of parts |
| Belly edge | USB-C J1 and slide switch SW1, with the USB protection beside them |
| Tail side of the battery | Battery connector J2 (opening towards the battery), polarity jumpers, fuse, charger, regulator |
| Rear flipper root | Motion sensor U5, pressure sensor U11, I2C pull-ups |
| Tail stem | Compass U8, then Qwiic J3 opening towards the body; just past the end of the LED run, the rail's end capacitor C9 and test point TP11 |
| Tail (outside the case) | Temperature sensor U9 at the tip of the upper lobe; the tail touch pad on the lower lobe |

Checks, 2026-11-23:

- DRC with schematic parity: no missing or extra footprints, no net conflicts (160 field-difference
  warnings, which are noise); no courtyard overlaps.
- `tools/check_leds.py` (run on the placement of 2026-11-22, which the LED row has not changed since):
  spine LEDs all facing their edge, chains in order, faces 0.10 mm inside the edge. NOT re-run for 18 LEDs.
- `jlc_cpl.py` has NOT been re-run since the sensors were added: it runs when the upload set is made.
- USB-C: board edge 2.66 mm in front of the footprint origin, from the maker's drawing. The connector
  overhangs the edge by about 1 mm. Slide switch: wholly on the board; its knob overhangs by about 0.85 mm.

Known weaknesses:

- The spine electrodes (show face, 5.5 to 11.5 mm from the edge) sit behind the LED supply rail and the
  touch lanes on the parts side. Each adds stray capacitance to that channel. Not measured.
- The regulator is about 100 mm from the module; the 3.3 V feed between them measured 204 milliohm through
  12 vias on the first four-layer route (layout review) and computes to 243 milliohm on the present one
  (network solve over the track pieces, 0.5 oz inner copper; 77 mm of it is on In2, so 1 oz inner copper
  would take roughly 50 to 70 milliohm off). Not a plane: In2 carries signals and ground fill.
- Both mounting holes are placeholders until the case exists.
- The temperature sensor is on the part of the tail that sticks out of the case: a bare 1.5 x 1.5 mm part
  and its capacitor on the back of the tail tip, within reach of fingers. By the owner's choice.
- Antenna: the module footprint's keep-out is honoured on all four layers, the throat edge is in front
  of it and the case is plastic. Expect room-range Wi-Fi and Bluetooth; not measured.
- No room has been reserved for JLCPCB's tabs. A rectangular frame would not make the board eligible for
  Economic assembly (the service is decided by the parts), but a frame with our own tabs is still worth
  drawing so they land where we choose and not on the LED edge or the USB socket.

## Routing (2026-11-23)

Made by `tools/route_all.sh`, start to finish, in this order (about an hour; the Mac must stay awake):

1. `tools/build_board.py`: 4-layer board, placement, nets, electrodes.
2. `tools/route_board.py strip`: everything drawn by rule, and fixed from then on. The LED strip (supply
   rail on the parts side 5.6 mm in, a ground via at each LED and each capacitor into a ground strip on
   the show face between the edge and the slider, data LED to LED); the touch controller's fan-out; the
   eleven touch lines in lanes; the tail line from its lane to its pad; the guard track; the motion
   sensor's ground links; the pressure sensor's supply and ground links; the snout link.
3. `tools/route_board.py dsn`, `tools/freerouting_capped.sh 80`, `tools/route_board.py ses`: Freerouting
   2.1.0 for 80 passes on the parts side and In2 only, with ground left out. Signals 0.15 mm, supplies
   0.4 mm, clearance 0.15 mm, vias 0.5 / 0.3 mm. It left 72 connections open on the last run.
4. `tools/patch_route.py`: closes what the autorouter left open and removes what breaks a rule, checking
   against KiCad's DRC each round; then `--tidy`; then `--ground`, every ground pad joined by track;
   then `--plane-vias 1.5`, a ground via beside every surface ground pad; then `--fatten`, supply tracks
   on In2 widened to 0.8 or 0.6 mm where DRC allows.
5. `tools/trim_dangling.py`, then `tools/route_board.py pour`: In1 ground plane, ground fill on the other
   three layers, pour-free areas (touch copper, antenna, mounting holes, round the compass and the
   temperature sensor), stitching vias on a 4 mm grid where all four layers have ground.

How the board in the repository was made (2026-11-23, third four-layer route): `route_all.sh` start to
finish on the present placement, which left one connection open at the pressure sensor U11 (SDA and 3.3 V
taking turns under its body). Then by hand-run commands: U11's local links added to the board and to
`build/pcb/strip.kicad_pcb` (they are in `route_board.py strip` for next time, so a fresh run would differ
here); the ground tracks round U11 cleared and re-laid after SDA; the LED supply feed, which had come out
0.25 mm wide for 27 mm on In2, taken out and re-routed at 0.4 mm; `--fatten`, `trim_dangling.py`, `pour`.
`patch_route.py` was changed along the way (supplies keep full width before a narrower track is tried;
the fatten step never leaves a track wider than DRC accepts). `route_all.sh` has NOT been run start to
finish with those last changes.

The board as it stands:

- 155 footprints. Tracks: 3689 mm on the parts side, 1050 mm on In2, 236 mm on the show face (170 mm of
  that is the scripted ground chain under the LEDs; 66 mm is signal). 444 vias, 252 of them ground,
  95 of those stitching.
- Supply tracks on In2 (half-ounce copper): 107 mm at 0.8 mm, 17 mm at 0.6 mm, 144 mm at 0.4 mm, and one
  2.9 mm piece of VBUS at 0.25 mm. +BATT 88 mm (39 at 0.8), +3V3 81 mm (37 at 0.8), VBUS 51 mm, VLED 47 mm
  (19 at 0.8). See the re-read, S1: 1 oz inner copper on the order form would halve their heating.
- DRC with schematic parity: 0 unconnected, no shorts, no clearance errors. Violations left, all looked at:
  1 starved thermal (U5.6 reaches the parts-side pour by one spoke; it is also tied by track);
  10 dangling track ends: three are the open ends of the guard track (by design); two are unused ends of
  the touch controller's scripted pick-up stubs (SCL 0.8 mm, TOUCH_IRQ 1.1 mm); one is a 7.5 mm spur of
  VLED left on the parts side at board (186.8, 44.9) when the feed was re-routed (harmless, untidy);
  four are fragments under 0.1 mm;
  20 silkscreen items (the silkscreen is not done);
  2 "does not match library" (a pad angle stored as 360 instead of 0: layout review, finding 16).
- `board_audit.py --hole-radius 2.6` (output in `build/pcb/audit.txt`): holes 0; floating 0.
  Joints: 14 track ends that meet their copper 0.03 to 0.25 mm off its centre line (KiCad counts all as
  joined; the copper overlaps), the dangling ends above, the snout link (ends inside the snout pad's
  copper), 6 duplicated scripted segments.
  Ground: every surface ground pad has a ground via within 2.1 mm, most within 1.5 mm; SW3.2 is 5.7 mm
  from one (tied by track). Four pieces of parts-side pour have no via of their own (at C34.2, U5.1-3,
  C8.2, D21.4), where the audit cannot see that the pads are also joined by track.
  Decoupling: U4.14 is VBAT_SENSE, not a supply; U1.5 is the USB protection array's VBUS pin (a clamp).
  Supplies on the parts side: 3.3 V is 0.13 mm for 3 mm in all (pad escapes at the fine-pitch sensors);
  the others never under 0.2 mm.
- The guard track is joined to ground only where the parts-side pour meets it: it carries no current.
- Seen on the show face: two small bare squares in the ground pour, one over the compass (tail stem) and
  one at the temperature sensor (tail tip), where pour is kept away from them.
- Independent reading: the first layout review read the first four-layer route; the re-read (see Reviews)
  read the third. The board in the repository is the third route with the re-read's fixes applied by
  hand-run commands (`clear_touch_neighbours.py`, `patch_route.py` rounds, ground, plane vias, two vias at
  SJ2.1, `--fatten`, pour): rule-checked and audited, not independently read since.

## Outline

- `outline/make_outline.py` writes `mosasaurus_outline.svg` (outline only, mm) and
  `mosasaurus_concept.svg/png` (outline with LEDs, touch zones and the big parts sketched in).
- Current draft: 225.6 x 72.6 mm. Closed mouth (jaw line and teeth are to be artwork or part of the
  printed case, not outline), tail 14 mm longer than the first draft, and a 26 mm flat on the belly for
  the USB socket and slide switch, which the case will hide. LED and slider run 137.2 mm, 18 LEDs at
  7.72 mm pitch, ending two LED places (15 mm) short of the tail base.
- An open-mouthed outline traced from a reference illustration (214.6 x 107 mm, tall upswept tail) was
  tried on 2026-11-22; the owner preferred this one. It is in the git history of `make_outline.py`.
- The owner's guidance, 2026-11-22: the PCB only has to carry the shape, since detail can go in the 3D
  print; one flipper front and one rear is enough.

## For the case

- Parts, battery and connectors on the back, under a printed cover; the front stays bare.
- Translucent ridge along the spine as the light guide. The side LEDs stand 2.0 mm off the board.
- Eye: D21 is on the parts side at board (202, 51), 3.7 x 3.5 mm and 1.1 mm tall, lens facing away from the
  board, 120 degree beam. The printed cover needs a hole or a thin window over it; there is no hole in the
  board and nothing shows on the bare face. The snout touch pad keeps 4.6 mm clear of it.
- `output/dinolight.step` is the board for the case design (most small parts have no 3D model in it).
- Battery space sketched as 36 x 28 mm (a 500 to 600 mAh cell). Keep that area of the board free of
  parts: a pouch cell must not rest on solder joints.
- USB-C and the slide switch must be reachable; BOOT and RESET by a pin hole at least.
- Openings in the cover, all on the parts side: a window over the light sensor U10 at the nose; a vent
  near the barometer U11 (rear flipper root); a sound hole over the buzzer BZ1 in the jaw. The tip of the
  upper tail lobe, with the temperature and humidity sensor U9, should stand clear of the case altogether.
- The tail sticks out of the case (the owner, 2026-11-23): the case ends about board x = 42 to 55, just past the
  last LED D18 at board (57.9, 43.6). Outside it, on the parts side: temperature
  sensor U9 and C41 (tip of the upper lobe), and possibly C9 and TP11 at board x 51 to 53. The compass U8 is
  inside, at board (61.5, 57.5). Keep magnets (a magnetic catch, a speaker)
  away from the tail.
- Qwiic socket J3 at board (69.2, 57.6) opens towards the head: leave room in the case for its plug and cable
  over board x 72 to 78 (5.6 mm clear of parts in front of it), and somewhere for an add-on board to sit.
- Battery: a pocket in the case holds the cell over the area marked on the board (no ties, no slots).
- Fixing the board to the case is undecided (the owner, 2026-11-22: press fit has no loose small parts, but
  what goes in can be pulled out). The board has two 2.7 mm (M2.5) holes, H1 in the snout and H2 behind the
  battery connector, at placeholder positions. My
  recommendation: keep holes and use screws, because the thing to keep a child out of is the LiPo.
  Alternative with no holes: back shell plus a front rim screwed together from behind.

## For firmware

Pin map (as in the schematic):

| GPIO | Use |
|---|---|
| 0 | BOOT button |
| 1 | TOUCH_IRQ from the MPR121: low when a touch or release is waiting; can wake the module |
| 2, 5 to 9, 12 to 14, 47 | Spare, not brought out |
| 4 | BUZZ: buzzer, high = on; drive with a 4 kHz square wave, leave low otherwise |
| 3 | Not used (strapping pin); test point |
| 10 | VBAT_SENSE: battery / 2 (ADC1) |
| 15, 16 | Motion sensor INT1 (wake), INT2: push-pull, active high |
| 17 | CHG_STAT: high = charge complete; low = charging, or no USB |
| 18 | VBUS_DET: high = USB present |
| 19, 20 | USB D-, D+ |
| 21 | LED_EN: high = LED rail on; pulled down |
| 11 | Spine LED data, 18 LEDs, first LED at the head |
| 41, 42 | I2C SDA, SCL: see the address table below |
| 48 | Eye LED data, 1 LED |
| 43, 44 | UART0 TX, RX on test points |

I2C addresses (one bus, 2.2k pull-ups, use 100 kHz unless measured):

| Address | Part | Library (from memory, unverified) |
|---|---|---|
| 0x29 | U10 LTR-303ALS light, at the nose | adafruit_ltr329_ltr303 |
| 0x2C | U8 QMC5883P compass, in the tail stem | adafruit_qmc5883p, or a few register writes |
| 0x44 | U9 SHT40 temperature and humidity, tail tip | adafruit_sht4x |
| 0x46 | U11 BMP580 pressure | adafruit_bmp5xx |
| 0x5C | U7 MPR121 touch | adafruit_mpr121 (pass the address) |
| 0x6A | U5 LSM6DS3TR-C accelerometer and gyroscope | adafruit_lsm6ds (LSM6DS3TRC) |

- The firmware is in `software/` (2026-11-26). Read from the libraries' and CircuitPython's source on that
  day, not tried on hardware: build to try first `generic_esp32s3_supermini` (status LED on GPIO48 = the
  eye, no LED power pin; the Adafruit Feather ESP32-S3 4 MB / 2 MB build would drive GPIO21, the LED
  rail switch, as its LED power pin); `adafruit_qmc5883p`'s `magnetic` is in gauss although its
  docstring says microtesla; `adafruit_ltr329_ltr303` gives raw counts, not lux; `adafruit_bmp5xx` is
  opened with `BMP5XX.over_i2c(i2c, address=0x46)`; `adafruit_lsm6ds` does not expose the chip's tap or
  free-fall detectors or its interrupt routing (raw register writes needed); deep-sleep pin alarms on
  this chip are level only.
- Claim every pin at start-up. CircuitPython pulls unclaimed pins up through about 45k: the gate pull-downs
  hold against that, but the motion sensor's interrupt pins (driven low) waste 73 uA each until claimed
  as inputs with no pull.
- At start-up clock SCL nine times, then soft-reset every sensor: after a brown-out the module resets but
  the sensors keep their state.
- Buzzer: PWM at 4 kHz, 50 %. Never leave GPIO4 high: 53 mA flows through R35 and R37 for as long as it is.
- Compass: read it with the LEDs dark or dim (LED current makes its own field); it needs a
  figure-of-eight calibration; keep steel away (see "For the case"). Put it in suspend before sleep; it
  still draws 22 uA.
- Motion sensor: for wake-on-movement leave the accelerometer in 12.5 Hz low-power mode (9 uA) with the
  gyroscope off; otherwise power it down (3 uA). Axes with the board lying parts side up: see the ground truth.
- BMP580: never enable its interrupt (the pin is grounded) and never address 0x7E on the bus. For deep
  standby it needs an output rate under 5 Hz, FIFO off and both filters bypassed.
- SHT40: do not use its heater. Wait 10 ms after asking for a reading.
- LTR-303: wait 100 ms after power-up. It will also see the board's own LEDs.
- A Qwiic add-on with its own pull-ups lowers the bus pull-up: cut the add-on's pull-up jumpers if more
  than one is fitted.
- Sleep current with everything in its lowest state: about 75 to 80 uA (reviewer's sum).
- Turn the LED rail off before sleeping. Drive both LED data pins low (or release them) before taking
  LED_EN low: a high data pin back-feeds the dead rail through the LED's input, about 8 mA per line.
- Cap total LED current at about 0.3 A: the maker allows 70 % with all colours lit, 19 LEDs at full
  white would be about 0.7 A, and the fuse holds 1.1 A.
- After LED_EN goes high the rail takes about 2 ms to rise; wait 5 ms before sending data. Blank the
  LEDs before taking LED_EN low: the rail takes about 60 ms to fall.
- At start-up read VBAT_SENSE before lighting anything, and go back to sleep below about 3.5 V: the
  supervisor resets the module if the 3.3 V rail dips under 2.93 V, and a load that is re-applied on
  every boot becomes a reboot loop.
- After releasing RESET the module starts about 0.2 s later (U6's delay).
- CHG_STAT reads "charging" with no cell fitted, and VBUS_DET stays high for 1 to 2 s after unplugging.
- Keep the motion sensor's INT1 (GPIO15) still while touch is in use: its track runs 13 mm behind the
  rear-flipper pad (release review, S1). Use it only as the deep-sleep wake line and send live events
  (tap, tilt, free-fall) to INT2 on GPIO16. Leave the MPR121's debounce at 2 samples or more.
- Deep-sleep wake: use the motion sensor's INT1 on GPIO15 (wake on high). Touch wake is limited (reviewer, from memory:
  one pad).
- CircuitPython's status LED is IO48, the eye; it stays dark unless the build names GPIO21 as its
  power pin (from memory, unverified).
- Touch: MPR121 at I2C 0x5C (not the library default of 0x5A: pass the address). ELE0 to ELE7 are spine 1 to 8 (head to tail), ELE8 snout, ELE9 tail,
  ELE10 rear flipper, ELE11 front flipper (changed 2026-11-22; it was 9 front flipper, 11 tail). Adafruit's CircuitPython MPR121 library should drive it
  (from memory, unverified). For the slider, take each spine electrode's baseline minus its filtered
  reading and compute the weighted centre.
- LED data and supply tracks run behind the spine electrodes: expect to tune thresholds with the LEDs
  running. Use 10 or more first-filter samples and some debounce.
- MPR121: send the soft reset (0x80) at start-up. Read the touch status before sleeping, or IRQ stays
  low. For touch-to-wake leave it running at a 32 to 64 ms sample interval (11 to 17 uA) and wake on
  GPIO1 low; otherwise stop it (3 uA).
- Ignore touch when the battery is low: readings shift when the 3.3 V rail drops out of regulation.
- Sleep at about 3.5 V so the cell's own protection never has to act.
- With USB plugged in and the charge finished, the charger never sees its termination current while the
  board is awake (the board's own draw exceeds it), so it holds the cell at 4.2 V. Sleep when CHG_STAT
  goes high or after a time limit.

## When the boards arrive

In this order, on one board first. Each item is something no review could check.

1. Before any cell or USB: look at the side LEDs (windows facing off the edge), the eye LED, the temperature
   sensor on the tail tip, the regulator U3 and the battery connector against the placement file.
2. The cell's polarity with a meter against the + and - marks at J2 (+ is pad 1, the pin nearer the
   belly edge), before it is plugged in and before USB. If it is the other way round: cut SJ1 and SJ2 and
   solder the other side of each.
3. USB only, no cell: 3.3 V on TP2, the module appears as a USB device.
4. Cell only, switch on, then off: the 3.3 V rail comes up cleanly and goes down (the XC6220 with this
   board's capacitance and long feed is not covered by its datasheet). Then USB unplugged with the switch
   off: the rail may chatter for up to a second on the way down.
5. A Wi-Fi burst with the cell near 3.5 V: no reset (U6 trips at 2.93 V).
6. I2C scan: 0x29, 0x2C, 0x44, 0x46, 0x5C, 0x6A.
7. Every touch pad, and the slider end to end, with USB plugged and unplugged; the rear-flipper pad while
   the motion sensor's INT1 is toggled on purpose (release review, S1).
8. Spine LEDs 1 to 18 in order against the numbers on the show face; the eye; the LED current limit.
9. The buzzer's loudness at 4 kHz (0.63 V at DC through 50 ohms: an estimate).
10. Wake from deep sleep on motion; sleep current against the 80 to 86 uA expected.

## Not fitted by the assembler

- LiPo cell (bought separately).
- Nothing else: SJ1, SJ2, test points, touch electrodes and holes are board features.

## Files

| File | What it is |
|---|---|
| `NOTES.md` | this |
| `tools/design_spec.py` | the parts and nets, declared once: the source of truth |
| `tools/schematic.py` | draws the schematic from the spec (overwrites the `.kicad_sch` files) |
| `dinolight.kicad_sch`, `mcu.kicad_sch`, `leds.kicad_sch` | the schematic: power; module, touch, accelerometer; LEDs |
| `output/schematic.pdf`, `output/schematic_p1..3.png` | the schematic to read |
| `tools/flat_netlist.py`, `build/sch/netlist_flat.txt` | flattened netlist for review |
| `tools/build_board.py` | builds `dinolight.kicad_pcb` from the netlist: outline, placement, nets. Overwrites the board |
| `dinolight.kicad_pcb`, `dinolight.kicad_pro` | the board: draft placement, fully routed |
| `output/board_parts_side.png`, `board_show_face.png`, `board_1to1_parts_side.pdf`, `dinolight.step` | renders, a 1:1 print and a STEP of the board |
| `tools/make_bom.py` | JLCPCB-format BOM from the netlist |
| `tools/route_all.sh` | the whole routing run in one command, about 45 minutes; `finish` re-does everything after the autorouter |
| `tools/route_board.py` | routing stages: LED strip, touch block and touch lanes by rule; autorouter in and out; ground pours and stitching vias |
| `tools/touch_block.py` | where the touch controller's parts sit and how its lines leave it (shared by placement and routing) |
| `tools/patch_route.py` | closes what the autorouter leaves open: a grid search that keeps scripted tracks and pads fixed and may push autorouted tracks aside; also ties in every ground pad |
| `tools/trim_dangling.py` | takes out dead-end tracks for as long as nothing comes unconnected |
| `tools/drc_summary.py`, `tools/view_region.py` | a short reading of a KiCad DRC report; a picture of part of the board for looking at routing |
| `routing/route_signals.ses` | the autorouter's result that the current board was made from (it is not repeatable run to run) |
| `tools/silkscreen.py` | draws the show face's silkscreen onto the board (reversed, or `lines`); `lines look` only makes a picture |
| `tools/title_outline.py`, `art/lettering.json` | the name and the LED numbers as plain outlines from a font file (needs matplotlib; run only to change the words or the font) |
| `software/` | the firmware and its documents, started 2026-11-26: see `software/README.md`. The `dino` library, host program and eight behaviours pass 45 desktop tests on a pretend board. `software/board/dino/hw_board.py`, `code.py` and `boot.py` have never run: every bench question in them is marked CHECK |
| `web/`, `tools/sim_shape.py` | the website (landing page, simulator, write-with-an-AI page) and the board shape the simulator draws. Published 2026-11-26 at https://mo-seph.github.io/dino-board/ by GitHub Pages from the top folder of `main` (the owner turned it on); the simulator was seen working there the same day |
| `output/show_face_art.png`, `output/show_face_art_lines.png` | the show face as drawn: the reversed version on the board, and the white-on-green alternative |
| `tools/make_upload.sh` | exports Gerbers, BOM and placement file into `fab/<name>/` |
| `fab/draft2/` | upload set from the first routing pass, for a quote only (superseded) |
| `lib/DinoLight.kicad_sym`, `lib/DinoLight.pretty/` | own symbols (side LED, slide switch, VLED rail) and footprints (side LED, touch anchor) |
| `datasheets/` | maker datasheets, named by C-number, plus Espressif's English module datasheet |
| `outline/` | outline generator and its SVG / PNG output |
| `tools/build_draft.py`, `draft/` | the quote-only draft board, its renders and upload set (`draft/jlc/`) |
| `tools/check_leds.py` | checks spine LED direction, edge distance and chain order on any board |
| `tools/fpinfo.py` | prints pad and courtyard extents of library footprints |
| `kicad-user/` | KiCad's documents folder for this project (set `KICAD_DOCUMENTS_HOME` to it) |
