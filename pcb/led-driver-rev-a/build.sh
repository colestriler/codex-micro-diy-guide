#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
KICAD_APP=/Volumes/KiCad/KiCad/KiCad.app/Contents
PYTHONPATH="$KICAD_APP/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages"
export PYTHONPATH
"$KICAD_APP/Frameworks/Python.framework/Versions/3.9/bin/python3.9" "$HERE/generate.py"
CLI="$KICAD_APP/MacOS/kicad-cli"
BOARD="$HERE/codex-micro-led-driver.kicad_pcb"
"$CLI" pcb drc --severity-all --exit-code-violations --output "$HERE/drc-report.txt" "$BOARD"
mkdir -p "$HERE/manufacturing/gerbers"
"$CLI" pcb export gerbers --output "$HERE/manufacturing/gerbers/" --layers F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts "$BOARD"
"$CLI" pcb export drill --output "$HERE/manufacturing/gerbers/" --format excellon --excellon-units mm "$BOARD"
"$CLI" pcb render --output "$HERE/board-top.png" --width 1600 --height 1100 --side top --background opaque --quality high --floor --perspective --rotate 0,0,0 "$BOARD"
cp "$HERE/bom-jlcpcb.csv" "$HERE/manufacturing/bom-jlcpcb.csv"
cp "$HERE/cpl-jlcpcb.csv" "$HERE/manufacturing/cpl-jlcpcb.csv"
(cd "$HERE/manufacturing/gerbers" && zip -q -FS ../gerbers-jlcpcb.zip ./*)
(cd "$HERE/manufacturing" && zip -q -FS ../Codex-Micro-LED-Driver-Rev-A-JLCPCB.zip gerbers-jlcpcb.zip bom-jlcpcb.csv cpl-jlcpcb.csv)
printf 'Manufacturing package: %s\n' "$HERE/Codex-Micro-LED-Driver-Rev-A-JLCPCB.zip"
