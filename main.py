from apps.base_app import AppsBuilder
import adafruit_ssd1306
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import usb_hid
import busio
import board
import digitalio
import time
import apps.shared.icons as icons
import easycrypt

import usb_cdc

font5x8 = "/apps/shared/font5x8.bin"

def ButtonsInit():
    buttons = []
    for pin in [board.GP28, board.GP27, board.GP22]:
        btn = digitalio.DigitalInOut(pin)
        btn.switch_to_input(digitalio.Pull.DOWN)
        buttons.append(btn)
    return buttons
def ReadInput() -> int:
    input = 0
    index = 0
    for b in buttons:
        input |= 1 << index if b.value else 0
        index += 1
    return input
def UsbKeyboardInit():
    time.sleep(1)
    try:
        keyboard = Keyboard(usb_hid.devices)
        return KeyboardLayoutUS(keyboard)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
def OledInit():
    i2c = busio.I2C(board.GP13, board.GP12, frequency = 800000)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    oled.rotate(False)
    oled.fill(0)
    oled.show()
    return oled
def DrawIcon(oled, x,y, scale, iconIndex):
    icon = icons.Icons8x8[iconIndex]
    for xx in range(len(icon)):
        for yy in range(8):
            for z in range(scale*scale):
                oled.pixel(xx*scale + z%scale,yy*scale + z//scale, icon[xx] & (1<<yy))

def EncryptSecret(secret, key, iv):
    return easycrypt.encrypt_string(key, secret, iv)

def DecryptSecret(secret, key, iv):
    return easycrypt.decrypt_string(key, secret, iv)

def ReadSecrets():
    secrets = []
    # 1st is secret as ecrypted hex string
    # 2nd is key 16byte key hex string
    # 3rd is init vector hex string
    # 4th is pin code 
    with open("secrets.txt", "rt") as fb:
        secrets+= fb.read().splitlines()
        fb.close()
    return secrets

def SaveSecrets(secrets):
    with open("secrets.txt", "wt") as fb:
        for s in secrets:
            fb.write(f"{s}\n")
        fb.close()

def MainAppFlow():
    apps = AppsBuilder.load()
    secrets = ReadSecrets()

    serial = usb_cdc.data
    serial_data = bytearray()
    input_buffer = bytearray()
    serial.write(bytes([27,91,50,74,27,91,72]))

    lastInput = -1
    menuIndex = 0
    selectedMenuIndex = None
    maxMenuItems = len(apps)
    while True:
        input = ReadInput()
        if (input != lastInput):
            pressed = input > 0
            if (input & 2) == 2:
                selectedMenuIndex = menuIndex
            if (input & 1) == 1 and (input & 4) == 4:
                selectedMenuIndex = None
            elif (input & 1) == 1:
                menuIndex = menuIndex - 1
            elif (input & 4) == 4:
                menuIndex = menuIndex + 1
            if (menuIndex >= maxMenuItems): menuIndex = 0
            if (menuIndex < 0): menuIndex = maxMenuItems - 1
            
            oled.fill(0)
            if (selectedMenuIndex == None):
                app = apps[menuIndex]
                oled.text(f"{app.name()}", 48,0, 1, size=1, font_name=font5x8)
                DrawIcon(oled, 0,0, 4, app.icon())
            elif (selectedMenuIndex == 0) and (pressed):
                if (input & 1) == 1:
                    keyboard.write(DecryptSecret(secrets[0],secrets[1],secrets[2]))
                else:
                    oled.text("Waiting for secret input...", 0,0, 1, size=1, font_name=font5x8)
                    serial.write(bytes([27,91,50,74,27,91,72]))
                    serial.write("> ".encode())
                    input_buffer = bytearray()

            oled.show()

            lastInput = input

        if (selectedMenuIndex == 0):
            app = apps[selectedMenuIndex]
            if serial.in_waiting > 0:
                byte = serial.read(1)
                if byte == b'\r':
                    input_buffer = serial_data
                    serial_data = bytearray()
                    serial.write("\n\r> ".encode())
                else:
                    serial_data += byte
                    serial.write(byte)
            
            inlen = len(input_buffer)
            if (inlen >= 6):
                data = input_buffer.decode("utf-8")
                pssw = data[:len(data)-3:]
                pin = data[len(data)-3::]
                key = secrets[1]
                iv = secrets[2]
                secrets[0] = EncryptSecret(pssw, key, iv)
                secrets[3] = EncryptSecret(pin, key, iv)
                # xdata = DecryptSecret(encpssw, key, iv)
                # print(f"{data} => {encpssw} => {xdata}")
                SaveSecrets(secrets)
                input_buffer = bytearray()
                oled.fill(0)
                oled.text(f"Pssw:{pssw} Pin:{pin}", 0,0, 1, size=1, font_name=font5x8)
                oled.show()
            elif (inlen > 0):
                oled.fill(0)
                oled.text("Incorrect password+pin length", 0,0, 1, size=1, font_name=font5x8)
                oled.show()


def GetPinValue(val):
    return val if val >= 0 else ('_')

def PinCodeFlow():
    secrets = ReadSecrets()
    pin = DecryptSecret(secrets[3],secrets[1],secrets[2])

    oled.fill(0)
    oled.text(f"*", 5,0, 1, size=4, font_name=font5x8)
    oled.show()
    time.sleep(0.2)
    oled.fill(0)
    oled.text(f"_ *", 5,0, 1, size=4, font_name=font5x8)
    oled.show()
    time.sleep(0.2)
    oled.fill(0)
    oled.text(f"_ _ *", 5,0, 1, size=4, font_name=font5x8)
    oled.show()
    time.sleep(0.2)
    oled.fill(0)
    oled.text(f"_ _ _", 5,0, 1, size=4, font_name=font5x8)
    oled.show()

    lastInput = ReadInput()
    lastInputTime = -1
    pinValues = [-1,-1,-1]
    while True:
        input = ReadInput()
        if (input != lastInput):
            if (input & 1) == 1:
                pinValues[0] = (pinValues[0] + 1) % 10
            if (input & 2) == 2:
                pinValues[1] = (pinValues[1] + 1) % 10
            if (input & 4) == 4:
                pinValues[2] = (pinValues[2] + 1) % 10
            oled.fill(0)
            oled.text(f"{GetPinValue(pinValues[0])} {GetPinValue(pinValues[1])} {GetPinValue(pinValues[2])}", 5,0, 1, size=4, font_name=font5x8)
            oled.show()
            lastInputTime = time.time()
            lastInput = input
            
        if (lastInputTime > 0 and (time.time()-lastInputTime) > 3):
            if (pin == f"{pinValues[0]}{pinValues[1]}{pinValues[2]}"):
                break
            else:
                oled.fill(0)
                oled.text(f"Invalid PIN", 0,0, 1, size=1, font_name=font5x8)
                oled.show()
                time.sleep(1)
                oled.fill(0)
                oled.text(f"_ _ _", 5,0, 1, size=4, font_name=font5x8)
                oled.show()
                pinValues = [-1,-1,-1]
                lastInputTime = -1
      
buttons = ButtonsInit()
keyboard = UsbKeyboardInit()
oled = OledInit()

PinCodeFlow()
MainAppFlow()
