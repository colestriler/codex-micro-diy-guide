"""Generate the Codex Micro LED driver PCB and JLCPCB assembly package.

Run this with KiCad's bundled Python (pcbnew module available), then use
build.sh to run DRC and export the manufacturing files.
"""
from pathlib import Path
import csv
import json
import pcbnew

ROOT = Path(__file__).resolve().parent
KICAD = Path("/Volumes/KiCad/KiCad/KiCad.app/Contents/SharedSupport")
FP = KICAD / "footprints"
BOARD_PATH = ROOT / "codex-micro-led-driver.kicad_pcb"

mm = pcbnew.FromMM
pt = pcbnew.VECTOR2I_MM
board = pcbnew.BOARD()
board.GetDesignSettings().SetCopperLayerCount(2)

nets = {}
for code, name in enumerate(("+5V", "GND", "DATA_IN", "DATA_BUFFERED", "DATA_OUT"), 1):
    net = pcbnew.NETINFO_ITEM(board, name, code)
    board.Add(net)
    nets[name] = net

def footprint(library, name, ref, value, x, y, rotation, pin_nets):
    fp = pcbnew.FootprintLoad(str(FP / f"{library}.pretty"), name)
    if fp is None:
        raise RuntimeError(f"Could not load {library}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(rotation)
    fp.Reference().SetVisible(False)
    for number, net_name in pin_nets.items():
        pad = fp.FindPadByNumber(str(number))
        if pad is None:
            raise RuntimeError(f"{ref} has no pad {number}")
        pad.SetNet(nets[net_name])
    board.Add(fp)
    return fp

# Both connectors use the same safe order: +5V, DATA, GND. Their openings
# point toward the top edge. The extra solder pads are a service fallback.
j1 = footprint("Connector_JST", "JST_XH_S3B-XH-A-1_1x03_P2.50mm_Horizontal",
               "J1", "KB2040: 5V DATA GND", 9, 8, 180,
               {1: "+5V", 2: "DATA_IN", 3: "GND"})
j2 = footprint("Connector_JST", "JST_XH_S3B-XH-A-1_1x03_P2.50mm_Horizontal",
               "J2", "LED: 5V DATA GND", 27, 8, 180,
               {1: "+5V", 2: "DATA_OUT", 3: "GND"})
u1 = footprint("Package_TO_SOT_SMD", "SOT-23-5", "U1", "SN74AHCT1G125DBVR",
               18, 17, 0,
               {1: "GND", 2: "DATA_IN", 3: "GND", 4: "DATA_BUFFERED", 5: "+5V"})
r1 = footprint("Resistor_SMD", "R_0603_1608Metric", "R1", "330R",
               22, 17.95, 0, {1: "DATA_BUFFERED", 2: "DATA_OUT"})
c1 = footprint("Capacitor_SMD", "C_0603_1608Metric", "C1", "100nF",
               18, 13.5, 90, {1: "+5V", 2: "GND"})
c2 = footprint("Capacitor_SMD", "CP_Elec_6.3x5.4", "C2", "100uF 16V",
               9, 24, 0, {1: "+5V", 2: "GND"})

def add_text(text, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(pt(x, y))
    item.SetLayer(layer)
    item.SetTextSize(pt(size, size))
    item.SetTextThickness(mm(0.15))
    item.SetTextAngleDegrees(angle)
    board.Add(item)

add_text("CODEX MICRO LED DRIVER REV A", 18, 28.8, 0.8)
add_text("KB2040", 6.5, 13.1, 0.8)
add_text("LED CHAIN", 24.5, 13.1, 0.8)
add_text("G   D   5V", 6.5, 14.3, 0.8)
add_text("G   D   5V", 24.5, 14.3, 0.8)
add_text("U1", 18, 19.5, 0.8)
add_text("R1", 22, 19.5, 0.8)
add_text("C1", 20, 13.5, 0.8)
add_text("C2 +", 9, 20, 0.8)

def track(net_name, points, width):
    for start, end in zip(points, points[1:]):
        item = pcbnew.PCB_TRACK(board)
        item.SetNet(nets[net_name])
        item.SetLayer(pcbnew.F_Cu)
        item.SetWidth(mm(width))
        item.SetStart(pt(*start))
        item.SetEnd(pt(*end))
        board.Add(item)

# Signal routes.
track("DATA_IN", [(6.5, 8), (6.5, 17), (16.8625, 17)], 0.35)
track("DATA_BUFFERED", [(19.1375, 17.95), (21.175, 17.95)], 0.35)
track("DATA_OUT", [(22.825, 17.95), (24.5, 17.95), (24.5, 8)], 0.35)

# 5 V trunk and short branches, sized for the dim 14-pixel prototype.
def via(net_name, x, y):
    item = pcbnew.PCB_VIA(board)
    item.SetNet(nets[net_name])
    item.SetPosition(pt(x, y))
    item.SetWidth(mm(0.8))
    item.SetDrill(mm(0.4))
    board.Add(item)

def bottom_track(net_name, points, width):
    for start, end in zip(points, points[1:]):
        item = pcbnew.PCB_TRACK(board)
        item.SetNet(nets[net_name])
        item.SetLayer(pcbnew.B_Cu)
        item.SetWidth(mm(width))
        item.SetStart(pt(*start))
        item.SetEnd(pt(*end))
        board.Add(item)

bottom_track("+5V", [(9, 8), (9, 12.7), (27, 12.7), (27, 8)], 1.0)
bottom_track("+5V", [(9, 12.7), (4.2, 12.7), (4.2, 24)], 1.0)
bottom_track("+5V", [(20.5, 12.7), (20.5, 15.55)], 0.6)
via("+5V", 4.2, 24)
track("+5V", [(4.2, 24), (6.2, 24)], 0.8)
via("+5V", 20.5, 15.55)
track("+5V", [(20.5, 15.55), (19.1375, 16.05)], 0.6)
track("+5V", [(20.5, 15.55), (20.5, 14.275), (18, 14.275)], 0.6)

# Ground trunk and branches.
bottom_track("GND", [(4, 8), (2, 8), (2, 28), (34, 28), (34, 18), (32, 18)], 1.0)
bottom_track("GND", [(22, 8), (22, 5), (32, 5), (32, 18)], 1.0)
for x, y in ((13.8, 24), (15.5, 16.05), (15.5, 17.95), (19.3, 11)):
    via("GND", x, y)
bottom_track("GND", [(13.8, 24), (13.8, 28)], 0.8)
bottom_track("GND", [(15.5, 16.05), (15.5, 28)], 0.6)
bottom_track("GND", [(15.5, 17.95), (15.5, 28)], 0.6)
bottom_track("GND", [(19.3, 11), (19.3, 3), (32, 3), (32, 18)], 0.6)
track("GND", [(11.8, 24), (13.8, 24)], 0.8)
track("GND", [(16.8625, 16.05), (15.5, 16.05)], 0.6)
track("GND", [(16.8625, 17.95), (15.5, 17.95)], 0.6)
track("GND", [(18, 12.725), (19.3, 12.725), (19.3, 11)], 0.6)

# Rectangular 36 x 30 mm outline.
for start, end in (((0, 0), (36, 0)), ((36, 0), (36, 30)),
                   ((36, 30), (0, 30)), ((0, 30), (0, 0))):
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(pt(*start))
    edge.SetEnd(pt(*end))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(mm(0.05))
    board.Add(edge)

pcbnew.SaveBoard(str(BOARD_PATH), board)

parts = [
    {"Designator": "U1", "Comment": "SN74AHCT1G125DBVR", "Footprint": "SOT-23-5", "JLCPCB Part #": "C7484", "MPN": "SN74AHCT1G125DBVR", "Assembly": "SMT"},
    {"Designator": "R1", "Comment": "330R 1%", "Footprint": "0603", "JLCPCB Part #": "C23138", "MPN": "0603WAF3300T5E", "Assembly": "SMT"},
    {"Designator": "C1", "Comment": "100nF 50V X7R", "Footprint": "0603", "JLCPCB Part #": "C14663", "MPN": "CC0603KRX7R9BB104", "Assembly": "SMT"},
    {"Designator": "C2", "Comment": "100uF 16V", "Footprint": "SMD,D6.3xL5.4mm", "JLCPCB Part #": "C2887276", "MPN": "RVT100UF16V67RV0016", "Assembly": "SMT"},
    {"Designator": "J1,J2", "Comment": "JST XH 3-pin right-angle", "Footprint": "Through Hole,Right Angle,P=2.5mm", "JLCPCB Part #": "C157928", "MPN": "S3B-XH-A(LF)(SN)", "Assembly": "THT"},
]
with (ROOT / "bom-jlcpcb.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=parts[0].keys())
    writer.writeheader()
    writer.writerows(parts)

placements = [
    ("J1", 9, 8, 180, "Top"), ("J2", 27, 8, 180, "Top"),
    ("U1", 18, 17, 0, "Top"), ("R1", 22, 17.95, 0, "Top"),
    ("C1", 18, 13.5, 90, "Top"), ("C2", 9, 24, 0, "Top"),
]
with (ROOT / "cpl-jlcpcb.csv").open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(("Designator", "Mid X", "Mid Y", "Rotation", "Layer"))
    for ref, x, y, rotation, side in placements:
        # KiCad's board Y axis points down in this generated file. JLCPCB's CPL
        # importer plots positive Y upward from the Gerber origin, so top-side
        # placement Y values must be inverted to land on the pads.
        writer.writerow((ref, f"{x:.3f}mm", f"{-y:.3f}mm", rotation, side))

(ROOT / "design-summary.json").write_text(json.dumps({
    "revision": "A-prototype",
    "board_mm": [36, 30, 1.6],
    "purpose": "Fully assembled replacement for the tested perfboard LED level-shifter circuit",
    "input_connector": ["+5V from KB2040 RAW", "data from KB2040 MO/MOSI", "GND"],
    "output_connector": ["+5V", "buffered data through 330 ohm", "GND"],
    "limits": [
        "This is an unbuilt prototype; fabrication files do not prove physical or electrical operation.",
        "It replaces only the LED-driver perfboard, not the key matrix, knob, joystick, touch sensor or KB2040.",
        "The input and output connectors need matching JST XH 3-pin cable assemblies.",
        "Confirm the existing single-LED perfboard circuit works before paying for assembly.",
        "The 100uF capacitor supports the low-brightness prototype; current and USB power must be checked on the completed 14-pixel chain.",
    ],
}, indent=2) + "\n")
print(BOARD_PATH)
