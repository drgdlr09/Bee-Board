# Bee Board - A Brief Overview
For Half Life week 3, I designed Bee Board, a MIDI controller with 7 hexagon-shaped capacitive touch keys, two sliders, two switches, and two RGB LEDs. I wanted to make a MIDI keyboard that had some sort of theme, and after brainstorming, I decided to lay out my touch buttons like a honeycomb with C in the middle, and G, E, A, F, D, and B around it. Another cool thing about the Bee Board is that you can play chords by placing your finger at the intersection of touch buttons. Since it's a honeycomb, I made a simple bee image and put it on the board as well.

# How It Works
Bee Board has an esp32-s3-zero microcontroller, 7 capacitive touchpads, two slides, two Kailh Choc switches, and two SK6812MINI-E RGB LEDs under the switches. The MIDI is build around the ESP32-S3-Zero. I wanted to add a good amount of features, so this was the right pick for this project. 
The touch pads are hexagons about 24mm across, with 1.2mm gaps between them so touching one pad doesn’t trigger the one next to it. They’re covered by solder mask, so the note letters are printed right on top of them. Touch pad 1 (C) is on GP1, and pads 2 through 7 (G, E, A, F, D, B) are on GP2 through GP7. When a pad is touched, the firmware sends a MIDI Note On message, and when it’s released, it sends Note Off. 
The sliders control how the notes sound. Slider 1 is on GP10 and sets the velocity, which is how loud each note plays. Touch pads can’t tell how hard you press them, so this was the easiest way to change the volume. Slider 2 is on GP11 and sends MIDI CC 1, the modulation wheel, which adds vibrato in most synths.
The switches change the octave. Switch 1 is on RX and moves down an octave, and switch 2 is on TX and moves up an octave. Pressing both resets it to the middle octave. Each switch has an SK6812MINI-E LED mounted under it on the back of the board, shining up through a cutout. The LED data line is on GP12. The first LED changes color to show the octave, and the second lights up blue for a single note and gold for a chord.

## Bill of Materials

| Part | Qty | Unit Price | Total | Vendor |
|------|-----|-----------|-------|--------|
| Waveshare ESP32-S3-Zero | 1 | $5.69 | $5.69 | AliExpress |
| Kailh Choc V2 Low Profile Switches | 5 | $0.63 | $3.15 | AliExpress |
| Bourns PTA1543 Slide Potentiometers (10k) | 2 | $1.58 | $3.16 | DigiKey |

Tax & shipping: $7.29
**Total**: **$19.29**
