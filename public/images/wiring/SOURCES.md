# Wiring illustration references

Original supplier assets, displayed with SVG crops and wiring overlays in the guide. Copyright remains with the respective makers. These are reference images of individual components, not photographs of a tested assembled keyboard.

| Local file | Original asset | Product / reference |
| --- | --- | --- |
| kb2040.jpg | https://cdn-shop.adafruit.com/970x728/5302-18.jpg | https://learn.adafruit.com/adafruit-kb2040/pinouts |
| pixels.jpg | https://cdn-shop.adafruit.com/970x728/4776-01.jpg | https://www.adafruit.com/product/4776 |
| encoder.jpg | https://cdn-shop.adafruit.com/970x728/377-03.jpg | https://www.adafruit.com/product/377 |
| joystick-bottom.jpg | https://www.sparkfun.com/media/catalog/product/0/9/09426-03.jpg | https://www.sparkfun.com/thumb-slide-joystick.html |
| switch.webp | https://ueeshop.ly200-cdn.com/u_file/UPAW/UPAW819/2408/07/photo/Gateron-NewNorthPole20-Yellow-Switch-5pin-SMD9.webp | https://www.gateron.com/products/gateron-new-north-pole-yellow-20-switch-set |

The switch image is the manufacturer's component render. The controller, pixel, encoder and joystick images are product photos. DIP chip, passive components, white LEDs and encoder underside are explanatory vector drawings. Reference pinouts:

- TI SN74AHCT125N DIP-14 top view: https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf (pages 3–4).
- PEC11 series terminal arrangement: https://cdn-shop.adafruit.com/datasheets/pec11.pdf (page 2).
- SparkFun joystick: underside contacts X / VCC / Y / GND, with GND nearest the pair of mounting tabs. The KB2040 build powers this passive joystick at **3.3V**, not the 5V in SparkFun's Arduino example.

The application uses the checked-in CircuitPython firmware's assignments. `scripts/check-wiring.mjs` checks the instructional map against that firmware. Hardware operation, physical fit, signal integrity and soldered connections require bench testing.
