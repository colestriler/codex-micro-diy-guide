"""Copy with code.py onto CIRCUITPY; unplug/replug after adding boot.py."""
import usb_cdc
usb_cdc.enable(console=True, data=True)
