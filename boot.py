import digitalio
import board
import storage
import usb_cdc
import usb_hid

keypress_pins = [board.GP28, board.GP27, board.GP22]
key_pin_array = []
for pin in keypress_pins:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.switch_to_input(digitalio.Pull.DOWN)
    key_pin_array.append(key_pin)

if (not key_pin_array[0].value) and (not key_pin_array[1].value) and (not key_pin_array[2].value):
    print(f"boot: expected button key sequence was not pressed, disabling usb drive")
    storage.remount("/", False)
    storage.disable_usb_drive()
    # usb_hid.enable(devices=(usb_hid.Device.MOUSE,))
    # usb_cdc.disable()

usb_cdc.enable(console=True, data=True)