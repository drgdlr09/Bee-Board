import time
import microcontroller
import touchio
import analogio
import digitalio
import usb_midi
import neopixel_write

DEBUG = False
MIDI_CHANNEL = 1
BASE_NOTE = 60
TOUCH_SENSITIVITY = 0.04
RELEASE_RATIO = 0.6
LED_BRIGHTNESS = 0.25

PADS = [
    (microcontroller.pin.GPIO1, "C", 0),
    (microcontroller.pin.GPIO2, "G", 7),
    (microcontroller.pin.GPIO3, "E", 4),
    (microcontroller.pin.GPIO4, "A", 9),
    (microcontroller.pin.GPIO5, "F", 5),
    (microcontroller.pin.GPIO6, "D", 2),
    (microcontroller.pin.GPIO7, "B", 11),
]

midi_out = usb_midi.ports[1]

touch = [touchio.TouchIn(pin) for pin, _, _ in PADS]

vel_slider = analogio.AnalogIn(microcontroller.pin.GPIO10)
mod_slider = analogio.AnalogIn(microcontroller.pin.GPIO11)

def button(pin):
    b = digitalio.DigitalInOut(pin)
    b.switch_to_input(pull=digitalio.Pull.UP)
    return b

btn_down = button(microcontroller.pin.GPIO44)
btn_up = button(microcontroller.pin.GPIO43)

led_pin = digitalio.DigitalInOut(microcontroller.pin.GPIO12)
led_pin.direction = digitalio.Direction.OUTPUT

def send(*data):
    midi_out.write(bytes(data))

def note_on(note, velocity):
    send(0x90 | (MIDI_CHANNEL - 1), note, velocity)

def note_off(note):
    send(0x80 | (MIDI_CHANNEL - 1), note, 0)

def control_change(cc, value):
    send(0xB0 | (MIDI_CHANNEL - 1), cc, value)

def to_midi(raw):
    return min(127, raw * 128 // 65536)

def set_leds(c1, c2):
    buf = bytearray()
    for r, g, b in (c1, c2):
        buf += bytes((int(g * LED_BRIGHTNESS), int(r * LED_BRIGHTNESS), int(b * LED_BRIGHTNESS)))
    neopixel_write.neopixel_write(led_pin, buf)

OCTAVE_COLOURS = {-3: (128, 0, 255), -2: (0, 0, 255), -1: (0, 160, 255), 0: (0, 255, 0),
                  1: (255, 200, 0), 2: (255, 80, 0), 3: (255, 0, 0)}

print("Calibrating touch pads - don't touch them...")
set_leds((40, 40, 40), (40, 40, 40))
baseline = [0.0] * len(touch)
SAMPLES = 40
for _ in range(SAMPLES):
    for i, t in enumerate(touch):
        baseline[i] += t.raw_value / SAMPLES
    time.sleep(0.02)
print("Baselines:", [int(b) for b in baseline])

octave = 0
velocity = 100
mod_value = -1
vel_smooth = float(vel_slider.value)
mod_smooth = float(mod_slider.value)
held = [False] * len(touch)
sounding = {}
last_buttons = (True, True)
last_button_change = 0.0
last_leds = None
last_debug = 0.0

def all_notes_off():
    for note in sounding.values():
        note_off(note)
    sounding.clear()
    for i in range(len(held)):
        held[i] = False

print("Ready! Honeycomb MIDI is running.")

while True:
    now = time.monotonic()

    for i, t in enumerate(touch):
        raw = t.raw_value
        jump = baseline[i] * TOUCH_SENSITIVITY
        if not held[i] and raw > baseline[i] + jump:
            held[i] = True
            note = BASE_NOTE + 12 * octave + PADS[i][2]
            if 0 <= note <= 127:
                note_on(note, velocity)
                sounding[i] = note
        elif held[i] and raw < baseline[i] + jump * RELEASE_RATIO:
            held[i] = False
            if i in sounding:
                note_off(sounding.pop(i))
        elif not held[i]:
            baseline[i] += (raw - baseline[i]) * 0.001

    vel_smooth += (vel_slider.value - vel_smooth) * 0.2
    mod_smooth += (mod_slider.value - mod_smooth) * 0.2
    velocity = max(1, to_midi(int(vel_smooth)))
    new_mod = to_midi(int(mod_smooth))
    if abs(new_mod - mod_value) >= 2 or (new_mod in (0, 127) and new_mod != mod_value):
        mod_value = new_mod
        control_change(1, mod_value)

    buttons = (btn_down.value, btn_up.value)
    if buttons != last_buttons and now - last_button_change > 0.03:
        last_button_change = now
        down_pressed, up_pressed = (not buttons[0]), (not buttons[1])
        if down_pressed and up_pressed:
            new_octave = 0
        elif down_pressed and last_buttons[0]:
            new_octave = max(-3, octave - 1)
        elif up_pressed and last_buttons[1]:
            new_octave = min(3, octave + 1)
        else:
            new_octave = octave
        if new_octave != octave:
            all_notes_off()
            octave = new_octave
            print("Octave:", octave)
        last_buttons = buttons

    playing = len(sounding)
    d2 = (0, 0, 0) if playing == 0 else ((0, 80, 255) if playing == 1 else (255, 170, 0))
    leds = (OCTAVE_COLOURS[octave], d2)
    if leds != last_leds:
        set_leds(*leds)
        last_leds = leds

    if DEBUG and now - last_debug > 0.25:
        last_debug = now
        print(" ".join("%s:%+5.1f%%" % (PADS[i][1], (t.raw_value - baseline[i]) / baseline[i] * 100)
                       for i, t in enumerate(touch)), "| vel", velocity, "mod", mod_value)
