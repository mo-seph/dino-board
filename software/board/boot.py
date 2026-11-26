"""Runs once at power-on, before USB starts. Decides who may write to the board's files: a computer
(the drive shows up on USB, and the board cannot save anything) or the board itself (no drive; scores
are saved and behaviours can arrive over Wi-Fi).

The drive is shown if any of these is true:
  - a file called KEEP_USB_DRIVE is on the board (it is, until the board has been proved on the bench)
  - the snout is being touched as the board is switched on or plugged in
  - anything at all goes wrong in here: never lock the owner out

NOT YET RUN ON HARDWARE."""
import os

show_drive = True
try:
    if "KEEP_USB_DRIVE" not in os.listdir("/"):
        import time
        import busio
        import microcontroller
        import adafruit_mpr121
        i2c = busio.I2C(microcontroller.pin.GPIO42, microcontroller.pin.GPIO41, frequency=100000)
        touch = adafruit_mpr121.MPR121(i2c, address=0x5C)
        time.sleep(0.3)                         # let its baselines settle
        show_drive = bool(touch.touched() & (1 << 8))     # electrode 8 is the snout
        i2c.deinit()
except Exception as e:
    print("boot.py:", e)
    show_drive = True

if not show_drive:
    import storage
    storage.disable_usb_drive()
    storage.remount("/", readonly=False)
