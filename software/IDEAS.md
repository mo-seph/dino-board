# What can the Mosasauraboard do?

The Mosasauraboard is a circuit board in the shape of a mosasaurus, about 23 cm long, with lights,
touch pads and a handful of sensors. It runs small programs called **behaviours**. There is room for 18
of them, one for each light along its back, and any of them can be swapped for a new one. You pick one
by holding its snout and sliding a finger along its back.

This page is for thinking up new behaviours. You don't need to be able to program: a good idea, written
down clearly, is enough for someone (or an AI model) to turn into code.

## What it can notice

- **Touch**, in five places: snout, tail, front flipper, rear flipper, and a strip along its back that
  knows where your finger is and how fast it is moving.
- **Movement:** which way up it is, tilting, shaking, tapping, spinning, and being in free fall.
- **Compass direction**, and magnets nearby.
- **Temperature and humidity**, at the tip of its tail.
- **Air pressure**, finely enough to tell when it has been lifted from the floor to a table.
- **Light**, at its nose: bright, dim, a shadow passing.
- **Time:** it can count seconds, minutes and hours while it is on.

## What it can do

- **18 lights along its back**, any colour each. They sit above the touch strip, so a light can follow
  your finger.
- **An eye**, any colour.
- **Beep.** Short beeps and simple tones; not tunes you would want to listen to.
- **Remember** a few numbers when switched off: a best score, a setting.

Later it should also be able to show readings on a phone, and send small messages to other
Mosasauraboards in other places ("someone stroked the one in the other house").

## What it can't do

It has no screen, no microphone, no camera and no proper speaker. It doesn't know the time of day or
where it is. It runs on a small battery, so anything that keeps all the lights bright for hours will
need it plugged in.

## How a behaviour works

A behaviour looks at what the board notices, and decides what the lights, eye and buzzer should do,
about 30 times a second. The best ones do one thing and are obvious within a few seconds of picking the
board up.

## Some to start from

Science and games:

| Behaviour | What you do | What it does | What it's about |
|---|---|---|---|
| Marble | Tip it one way and the other | A marble of light rolls along its back, picks up speed, bounces off the ends | Gravity, speed, friction |
| Reaction timer | Wait for the eye to turn green, then touch the snout | The lights show how long you took; it remembers your best | How fast nerves are |
| Jump height | Hold it and jump | It times how long you were in the air and shows the height | Free fall: height from time |
| Stair climber | Touch the snout at the bottom, carry it up | One more light for every 25 cm you climb | Air pressure falls as you go up |
| Magnet hunt | Someone hides a magnet; sweep the board about | The lights grow and turn red as you get close | Magnetic fields, and how fast they fade with distance |
| Colour mixer | Hold the flippers and tail, in any combination | Each adds red, green or blue; the back shows the mix | How screens make every colour from three |

Useful things:

| Behaviour | What you do | What it does |
|---|---|---|
| Timer | Slide to choose 1 to 18 minutes, touch the snout | The lights count down, then it flashes and beeps |
| Weather tail | Glance at it | The back shows the temperature as a bar from blue to red; touch a flipper for humidity; the eye shows whether the pressure is rising (fine weather) or falling |

## Sending in an idea

Three sentences are enough:

1. **What you do to it:** touch, tilt, shake, carry it somewhere, shine a torch at it.
2. **What it does back:** which lights, what colours, any beeps.
3. **What it's for:** a game, an experiment, something useful.

For example: *"When I shake it, the lights fill up from the head like a battery charging, and slowly
drain when I stop. If I fill it right up, the eye flashes and it beeps. It's a game: how fast can you
fill it?"*

The full list of what a behaviour can read and control is in [API.md](API.md). To have an AI model
write the code, give it [PROMPT.md](PROMPT.md) with your idea added at the end.
