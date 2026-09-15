"""Maintain the short, staged bench lessons. Run to regenerate data/wiring-lessons.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def step(id, title, how, why, check, *, trace=None, links=None):
    return dict(id=id, title=title, how=how, why=why, check=check, trace=trace, links=links or [])
def link(label, file):
    return dict(label=label, url='/downloads/wiring-guide/'+file)
def group(title, steps): return dict(title=title, steps=steps)
def phase(id, title, intro, need, groups): return dict(id=id, title=title, intro=intro, need=need, groups=groups)
def jumper(id, title, a, b, bridge_a, bridge_b, why, check, length='1 inch', trace=None):
    return step(id,title,[f'Unplug USB. Cut a {length} insulated wire and strip about 4 mm from each end.', f'From the TOP of the perfboard, put its ends through {a} and {b}.', f'Underneath, bend the bare ends to touch {bridge_a} and {bridge_b}, respectively. Solder each end to its own pad and the connection it touches.'],why,check,trace=trace)

phases=[
phase('wiring-start','Get the KB2040 ready','Start with the controller alone. No switches or LEDs need to be connected yet.',
      'KB2040, a USB data cable, your computer.',[group('Make the board appear in Finder',[
 step('install-python','Install CircuitPython',[
  'If CIRCUITPY already appears when you plug in, skip this step. Back up an existing code.py before replacing it.',
  'Download the CircuitPython UF2 specifically for Adafruit KB2040. With USB unplugged, hold BOOT, plug USB in, then release BOOT when RPI-RP2 appears.',
  'Copy the UF2 onto RPI-RP2. It disappears and comes back as CIRCUITPY. Quit macOS Keyboard Setup Assistant if it opens; our small keypad cannot complete the normal full-keyboard identification steps.'
 ],'CircuitPython is the software that runs our small Python programs on the board.','CIRCUITPY is visible. RPI-RP2 is the installer drive; CIRCUITPY is where code.py goes.',links=[dict(label='KB2040 CircuitPython download',url='https://circuitpython.org/board/adafruit_kb2040/')]),
 step('install-libraries','Add the keyboard library',[
  'Open CIRCUITPY/boot_out.txt to check the CircuitPython major version. Download the matching Adafruit CircuitPython library bundle.',
  'Create a lib folder on CIRCUITPY if it does not exist. Copy the entire adafruit_hid folder from the bundle into CIRCUITPY/lib.',
  'Each test below is a replacement code.py, not an extra program to run alongside the old one. Keep a backup on your computer. Install only the stage you are testing.'
 ],'The HID library lets the KB2040 send normal keyboard presses to your computer.','You have CIRCUITPY/lib/adafruit_hid. Do not put code.py in lib.',links=[dict(label='Adafruit library bundles',url='https://circuitpython.org/libraries')]),
 ])]),
phase('wiring-knob-button','Make the knob click','The knob is two controls in one: a pushbutton and a rotation sensor. Test the button first.',
 'Encoder, two insulated wires, soldering iron, solder, wire stripper, a holder or heat-resistant tape.',[group('Two wires, one keypress',[
 step('identify-encoder','Find the two button terminals',[
  'Unplug USB. Look at the underside of the Adafruit 377 encoder: one side has TWO electrical terminals, and the other has THREE.',
  'The two-terminal side is the pushbutton. The three-terminal side measures rotation. Large metal mounting tabs are not signal terminals.',
  'Cut two wires roughly 4 inches (10 cm) long, or longer if your case layout needs it. Strip about 3 mm at each end. Leave enough slack to lift the plate.'
 ],'Pressing the knob joins the two button terminals, like closing a tiny door.','You are using the two-terminal side. This step does not require a key switch or a diode.'),
 step('button-controller','Solder the button wires to the KB2040',[
  'With USB unplugged, put one wire through the KB2040 pad marked G and the other through A2.',
  'Route the insulated wires from the component side and solder the pad and wire together on the underside. Either entry direction works electrically, but check clearance before mounting.',
  'A small joint should join the wire and the metal ring without touching the next ring. Trim excess wire, leaving the joint intact.'
 ],'A2 listens for the button; G provides ground.','Trace each wire back to the printed label. A2 is not the perfboard hole A2.'),
 step('button-encoder','Attach those wires to the encoder',[
  'Lightly tin the two button terminals and wire ends. Secure the encoder so you do not have to hold it near the iron.',
  'Solder the G wire to one of the TWO button terminals and the A2 wire to the other. Either terminal order works.',
  'The bare wire rests against the outside of the terminal; there is no slot to thread it through. Keep the two joints separate and insulate exposed joins before final assembly.'
 ],'A button press connects A2 to ground. The program detects that change.','No bare strands touch the other terminal or the encoder metal shell.'),
 step('test-button','Test: pressing the knob types “a”',[
  'Set the board on a dry nonmetal surface, inspect the joints, and plug USB in.',
  'Download button-test.py below. Back up the existing code.py, then copy the test to the root of CIRCUITPY and name it exactly code.py.',
  'Open a blank text document and click inside it. Press and release the knob once. You should see one a.'
 ],'This checks the controller, USB, program and your first two soldered wires together.','One press produces one a. If not, confirm the file name, HID library, focused text field and the G/A2 wires before adding more parts.',links=[link('Download button-test.py','firmware/button-test.py')]),
 ])]),
phase('wiring-knob-turn','Make the knob turn','Keep the working button connected. Add three wires for rotation.',
 'The same encoder, three more insulated wires, your working button test.',[group('Read left and right',[
 step('encoder-common','Connect the middle rotation terminal to ground',[
  'Unplug USB. Cut three wires about 4 inches long. Strip about 3 mm at the ends.',
  'Use the middle terminal on the THREE-terminal side of the encoder. Connect it to a KB2040 pad labeled GND.',
  'G and GND are the same electrical ground. If your board has two holes under the GND label, either is ground. Use a free one; do not force multiple wires into an occupied hole.'
 ],'The center terminal is the common connection shared by both rotation signals.','Ground goes to the middle of the three rotation terminals, not the middle of the encoder body.'),
 step('encoder-signals','Connect the two outer rotation terminals',[
  'Connect one outer terminal to KB2040 TX and the other to RX. Solder one connection at a time.',
  'Either outer-terminal order can be used; it changes which direction counts as clockwise in software.',
  'Keep these wires clear of the two button terminals. Leave the existing A2 button connection in place.'
 ],'The two signals change in a different order depending on which way you turn the knob.','Three rotation wires: outer to TX, middle to GND, other outer to RX.'),
 step('test-rotation','Test: turning prints “r” and “l”',[
  'Inspect the joints, then plug USB in. Replace code.py with knob-test.py, renamed code.py.',
  'In a blank text document, turn one click right, then one click left. The test should type r and l. Pressing still types a.',
  'If right prints l, change REVERSE_ROTATION from True to False, or the reverse, in code.py and save. You do not need to resolder the outer wires.'
 ],'This proves the rotation circuit works before assigning app shortcuts.','The knob responds in both directions. Remember your REVERSE_ROTATION setting for the next program.',links=[link('Download knob-test.py','firmware/knob-test.py')]),
 step('reasoning-shortcuts','Optional: make the knob send app shortcuts',[
  'Once rotation works, reasoning-knob.py sends Control+Option+Command+Up or Down. Keep your calibrated REVERSE_ROTATION value.',
  'An app or an OS shortcut tool must actually bind those chords to increase/decrease reasoning. Availability depends on the app and its current controls.',
  'This firmware sends keystrokes only. It does not read the app’s reasoning level, and it does not create a missing app command.'
 ],'The physical knob can be reused for different actions by changing software.','Verify the shortcut with your ordinary keyboard first, then try the knob with that app focused.',links=[link('Download reasoning-knob.py','firmware/reasoning-knob.py')]),
 ])]),
phase('wiring-perfboard','Build the LED perfboard','This is the same hole-by-hole layout from our bench walkthrough. Work with USB unplugged until the power-on checkpoint.',
 '4 × 6 cm isolated-pad perfboard (A–T / 01–14), SN74AHCT125N DIP-14, one RGBW NeoPixel, 330 Ω resistor, 104 / 100 nF capacitor, insulated wire.',[
group('A. Prepare the LED and place the chip',[
 step('prepare-led','Solder three wires to the LED’s input side',[
  'Look at the back of the Adafruit 4776 RGBW mini LED. Find + / 5V, GND / −, and DIN. DIN is on the side where the arrows start; do not use DOUT.',
  'With the arrows pointing right and 5V at the top, the input-side pads are top: 5V, middle: DIN, bottom: GND. If your board markings differ, follow its labels rather than this orientation.',
  'Cut three wires long enough to reach beneath the key, roughly 4 inches for our test. Strip about 2 mm at the LED ends. Tape the LED edges to a heat-resistant surface, tin the pads and ends, then briefly reheat each pair together.',
  'Label the far ends 5V, DIN and GND. Keep them disconnected for now.'
 ],'The switch itself is not a lamp. This separate LED shines up through the clear switch and keycap.','Three separate input-side joints. No solder bridges between pads. The other three pads are for the next LED.'),
 step('place-chip','Place the level shifter in D and G',[
  'Orient the perfboard with A–T across the top and row 01 at the bottom. The diagrams show the used area A–K, rows 03–12.',
  'Place the chip writing-side up, with its semicircular notch pointing toward the column letters.',
  'Left legs: D10, D09, D08, D07, D06, D05, D04. Right legs: G10, G09, G08, G07, G06, G05, G04. Columns E and F sit underneath the body. Do not force the legs.'
 ],'The notch identifies the numbering: pin 1 is D10, pin 7 is D4, and pin 14 is G10.','This coordinate plan requires separate metal pads, not a breadboard or stripboard with connected rows.'),
 step('solder-chip','Solder the chip in place',[
  'Secure the body with tape, flip the board, and solder opposite corner legs D10 and G04 first. Remember the layout is mirrored underneath.',
  'Check that the chip is seated and oriented correctly, then solder the other 12 legs.',
  'Touch the iron to both the leg and its pad, feed in a little solder, remove the solder, then the iron. Keep each ring separate from neighboring rings.'
 ],'These joints hold the chip to individual pads. The next wires will connect selected pads together.','All 14 legs have their own joints. No unintended bridges. Read coordinates from the top, not by counting left-to-right on the underside.'),
]),
group('B. Ground, power and the small capacitor',[
 jumper('g-loop','Enable the channel we will use','C10','C4','D10','D4','Grounding enable pin 1 switches this channel on. Pin 7 is the chip ground.','Only C10-D10 and C4-D4 are joined; the insulated wire connects the two ends.',trace='g-loop'),
 step('ground-lead','Add the loose ground lead at B4',[
  'Cut a 4-inch wire. Strip about 4 mm at one end and insert it through B4 from the top.',
  'Underneath, bend that bare end to touch the existing C4 connection. Solder B4 and the join to C4.',
  'Label the free end GND. Leave it disconnected.'
 ],'This lead will connect the whole ground network to the KB2040.','The ground path is B4-C4-D4, with the C4-C10 jumper reaching D10.',trace='kb-ground'),
 step('power-lead','Add the loose power lead at H10',[
  'Cut a 4-inch wire. Strip about 4 mm at one end and insert it through H10.',
  'Underneath, join it to the neighboring chip leg at G10. Label its loose end 5V and leave that end disconnected.'
 ],'G10 is chip pin 14, its power supply.','H10-G10 is separate from G9 and H9.',trace='kb-power'),
 step('capacitor','Add the 104 capacitor',[
  'Find the small ceramic capacitor marked 104, 100 nF or 0.1 µF. These mean the same value. It has no positive or negative leg.',
  'Put its legs through D11 and G11. The holes are 7.6 mm apart. Support each leg near the body and gently bend farther down; do not pull against the yellow body. It may sit slightly raised.',
  'Underneath, join D11 to D10 and G11 to G10. Solder each leg to its own pad and neighboring chip leg. Trim excess tails after soldering.'
 ],'It is a tiny energy cushion across power and ground, smoothing brief disturbances.','Do not connect its two legs with bare wire. The capacitor itself is the component between the two networks.'),
]),
group('C. Give the LED its data, ground and power',[
 step('data-lead','Add the loose DATA IN lead at C9',[
  'Cut a 4-inch wire. Strip about 4 mm at one end, insert it through C9 and join it to D9 underneath.',
  'Label the free end DATA IN and leave it disconnected. Keep D9 separate from grounded D10.'
 ],'D9 is input pin 2. It will receive the KB2040’s color instructions.','C9-D9 is its own signal connection.',trace='kb-data'),
 step('resistor','Fit and solder the 330 Ω resistor',[
  'Bend the resistor legs gently and insert them through B8 and B12 from the top. Either direction is correct. Leave the body slightly raised.',
  'Underneath, bend the B8 leg across C8 until it touches D8. Solder to B8 and the chip leg D8. Contact with C8 on that same row is okay.',
  'Solder the other leg to B12 only. Keep row 8 clear of rows 7 and 9. Trim tails beyond the finished joints.'
 ],'The resistor sits in the data path and helps protect the LED’s input.','B8 connects to D8; the resistor body connects B8 to B12. Do not bypass the resistor with a wire.'),
 step('led-data','Attach the LED’s DIN wire at A12',[
  'Trace the wire back to the LED’s DIN pad. Strip about 4 mm from its loose end.',
  'Insert it through A12, bend it toward the resistor leg at B12 underneath, and solder A12 and the B12 join.',
  'Trim only excess metal beyond the joined section. Leave enough insulated wire to reach the key position.'
 ],'The route is chip output D8 → resistor → A12 → LED DIN. This connection can stay in the final build.','DIN is not DOUT, 5V or ground.',trace='led-data'),
 step('led-ground','Attach the LED’s GND wire at A4',[
  'Trace the LED’s GND / − wire. Strip about 4 mm from the loose end and insert it through A4.',
  'Underneath, join A4 to the existing ground connection at B4. Solder both.'
 ],'The LED and chip need the same ground reference.','A4-B4-C4-D4 is connected; unrelated adjacent rows remain separate.',trace='led-ground'),
 step('led-power','Attach the LED’s 5V wire at I10',[
  'Trace the LED’s 5V / + wire. Strip about 4 mm and insert it through I10 (letter I).',
  'Underneath, join I10 to H10 and solder. Keep USB unplugged.'
 ],'The LED gets its power directly from the power network, not through the data resistor.','I10-H10-G10 is one power network. We still need to finish the unused chip inputs.',trace='led-power'),
]),
group('D. Keep the three spare channels quiet',[
 jumper('unused-1','Ground the first unused input','C6','B5','D6','B4','The chip has four channels. Ground holds an unused input steady instead of letting it pick up noise.','C6-D6 joins B5-B4 through the insulated wire.',trace='unused-1'),
 jumper('unused-pair','Join the other two unused inputs','H5','H8','G5','G8','This joins unused input pins 9 and 12.','This pair is not grounded until the next step.',trace='unused-pair'),
 jumper('unused-ground','Connect that pair to ground','I5','A5','H5','A4','This gives both inputs a path to the shared ground.','All three unused inputs, pins 5, 9 and 12, now reach ground.',length='1½-inch',trace='unused-ground'),
 jumper('enable-pair','Join two unused enable pins','H6','H9','G6','G9','These control whether the spare channels are on. They will go to 5V to switch them OFF.','Keep these joints separate from the ground connections at H5 and H8.',trace='enable-pair'),
 jumper('enable-power','Connect those enable pins to 5V','I9','J10','H9','I10','A high voltage on these enable pins switches the two spare channels off.','I9-H9 and J10-I10 are power connections, not ground.',trace='enable-power'),
 jumper('enable-last','Switch off the last unused channel','C7','K10','D7','J10','This puts enable pin 4 at 5V, switching the last spare channel off.','D7 must stay separate from grounded D6. Leave output pins 6 (D5), 8 (G4), and 11 (G7) unconnected.',length='1½-inch',trace='enable-last'),
]),
group('E. Connect the completed circuit to the KB2040',[
 step('connect-data','Connect DATA IN to KB2040 MO',[
  'With USB unplugged, trace the loose DATA IN wire from C9-D9. Strip about 3 mm from its free end.',
  'Solder it to KB2040 MO (letter O), not MI. On the row that reads 10, MO, MI, CLK, A0, it is between 10 and MI.'
 ],'MO is the pin named board.MOSI in the test program.','This is the loose controller lead, not the wire already going to LED DIN.',trace='kb-data'),
 step('connect-power','Connect the 5V lead to RAW',[
  'Trace the loose 5V wire from H10-G10. Strip about 3 mm and solder it to KB2040 RAW, near USB and beside G.',
  'Use RAW, not 3V. Leave the board’s USB power-protection jumper unchanged.'
 ],'RAW supplies the LED and level shifter from USB power.','Do not plug in yet; the common ground must also be connected.',trace='kb-power'),
 step('connect-ground','Connect the ground lead; share a junction if needed',[
  'Trace the loose GND wire from B4. If a KB2040 G/GND hole is free, you can solder it there and leave the knob’s ground wire in place. The ground pads are electrically shared.',
  'Our PDF shows this alternative: unplug USB, check the existing knob wire on G reaches perfboard A3 comfortably, then desolder that wire from G. Do not pull until its solder has melted.',
  'Insert the moved knob wire through A3 and join A3 to A4 underneath. Solder it. Put the loose B4 ground lead into the now-empty KB2040 G hole and solder.',
  'If that wire will not reach, use a longer insulated wire. Do not stretch a soldered connection. The other encoder ground on GND stays connected.'
 ],'The perfboard becomes a shared junction: knob → A3-A4 → B4 → KB2040 G. The LED shares it too.','For the PDF layout, confirm BOTH the A3-A4 joint and B4-to-KB-G lead are complete. With a free GND pad, the A3 reroute is unnecessary.',trace='knob-ground'),
 step('inspect-circuit','Check before applying power',[
  'With USB unplugged, inspect both sides under good light. No stray strand or unintended solder bridge should join power and ground or neighboring chip legs.',
  'If you have a multimeter, check continuity of the intended paths and for a persistent near-zero resistance between power and ground. A capacitor can cause a brief changing reading; do not power a circuit with a sustained short.',
  'Without a meter, a visual inspection is only a basic check, not electrical verification. Keep the boards on a dry nonmetal surface and all loose metal clear. Stop and correct any uncertain joint.'
 ],'A successful code upload cannot tell us whether every solder joint is right.','The map and PDF describe intended connections. They do not verify your soldered board.'),
]),
]),
phase('wiring-led-test','Light one key','Use one LED first. This is the point where we check the light, before committing to the baffle tray.',
 'Completed perfboard, one RGBW LED, clear switch and keycap for the optical check.',[group('Power on, then send a color',[
 step('power-on','Do a basic power-on check',[
  'Place the inspected circuit on a dry nonmetal surface and plug the KB2040 into USB. Do not hold exposed joints against metal.',
  'Confirm CIRCUITPY appears. The external LED may remain dark until its program sends a color.',
  'Unplug immediately for a burning smell, smoke or a USB power warning. Do not keep retrying a suspected short.'
 ],'Power alone does not tell an addressable LED which color to display.','CIRCUITPY appears. This is a controller check, not yet a successful LED test.'),
 step('load-led-test','Install the one-LED test',[
  'The download bundle contains three staged tests, the HID folder and NeoPixel libraries. Copy its lib contents into CIRCUITPY/lib. Do not remove other libraries you already use.',
  'Back up code.py, then copy led-test.py to CIRCUITPY and rename it code.py. Keep your calibrated REVERSE_ROTATION setting.',
  'This program drives ONE RGBW LED on MO at 8% brightness. It keeps the knob’s r/l test and button a test. The external LED should glow dim pink.'
 ],'A single low-brightness pixel is enough to test the driver circuit and light leakage.','Physically confirm the external LED lights. A log saying “color sent” only proves the program ran.',links=[link('Download starter bundle','wiring-starter.zip'),link('Download led-test.py','firmware/led-test.py')]),
 step('dark-led','If the LED stays dark',[
  'Read the CircuitPython serial console for an exception. Missing neopixel or adafruit_pixelbuf means the libraries are not installed. Confirm the file is code.py, not code.py.txt.',
  'Unplug before checking wiring. Trace MO → C9-D9; D8 → B8 → resistor → B12-A12 → DIN. Confirm the LED input side, RAW supply and shared ground.',
  'Recheck chip notch orientation and the 104 capacitor joints. A photo cannot rule out a bad joint or hidden short; a multimeter is the next useful diagnostic tool if the cause is unclear.'
 ],'Troubleshoot one path at a time instead of changing many wires at once.','Do not infer that the light is working merely because Finder shows CIRCUITPY.'),
 step('baffle-test','Compare the light with and without a baffle',[
  'Unplug USB before positioning the LED below one clear switch and cap. Keep its metal pads isolated from the switch pins. Add two neighboring caps for comparison.',
  'Power it again without touching the wiring. Compare the lit key and its neighbors in normal room light, then dimmer light.',
  'Unplug, add one existing opaque baffle, then repeat. If it makes a useful difference, continue the tray fit test. If not, you can defer the extra baffle print.'
 ],'This small test answers whether light-blocking parts improve your actual printed keys.','This is an optical test, not proof of the full tray fit. Do not move a powered LED against exposed switch pins.'),
])]),
]
(ROOT/'data/wiring-lessons.json').write_text(json.dumps(phases,ensure_ascii=False,indent=2)+'\n')
print(f'Wrote {len(phases)} phases, {sum(len(g["steps"]) for p in phases for g in p["groups"])} steps')
