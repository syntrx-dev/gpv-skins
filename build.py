"""Builds blue-flame.css: a GPV DS4 classic-skin override with recolored SVG parts embedded as data URIs."""
import base64, random, re, pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "ps4-assets"

# Palette (from the owner's controller photo)
BLUE = "#1e8fe6"        # solid center section
BLUE_DEEP = "#0b5fc0"
BLUE_LIGHT = "#5fc3ff"
SPECK = "#2d8cff"
PRESS = "#6fd6ff"       # pressed-state fill (bright ice blue)
PRESS_RING = "#d8f4ff"
BTN = "#101216"         # glossy black buttons
BTN_RING = "#2a2f38"


def read(name):
    return (SRC / f"{name}.svg").read_text(encoding="utf-8")


def recolor(svg, mapping):
    """mapping: {'.cls-N': 'css body'} replaces the whole rule body for that selector."""
    for sel, body in mapping.items():
        svg, n = re.subn(r"(\s%s\s*\{)[^}]*(\})" % re.escape(sel), r"\g<1> %s \g<2>" % body, svg)
        assert n, f"selector {sel} not found"
    return svg


def uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


# ---------- base (body) ----------
def flames(rng, side):
    """Smoky blue flame wisps rising from the bottom of one grip. Left-grip coordinates; right is mirrored."""
    out = []
    # broad glow at the bottom of the grip
    out.append('<ellipse cx="95" cy="560" rx="150" ry="150" fill="url(#flameGlow)"/>')
    for i in range(14):
        x0 = rng.uniform(5, 200)
        y0 = rng.uniform(520, 610)
        h = rng.uniform(140, 300)
        w = rng.uniform(18, 55)
        lean = rng.uniform(-60, 60)
        curl = rng.uniform(-40, 40)
        tipx, tipy = x0 + lean, y0 - h
        d = (f"M{x0 - w:.1f},{y0:.1f} "
             f"C{x0 - w + curl:.1f},{y0 - h * .45:.1f} {tipx - w * .6:.1f},{tipy + h * .35:.1f} {tipx:.1f},{tipy:.1f} "
             f"C{tipx + w * .3 + curl:.1f},{tipy + h * .4:.1f} {x0 + w + curl:.1f},{y0 - h * .4:.1f} {x0 + w:.1f},{y0:.1f} Z")
        op = rng.uniform(.35, .75)
        out.append(f'<path d="{d}" fill="url(#flameGrad)" opacity="{op:.2f}" filter="url(#soft)"/>')
    # thin bright smoke lines
    for i in range(10):
        x0 = rng.uniform(10, 200)
        y0 = rng.uniform(500, 600)
        h = rng.uniform(100, 230)
        c1 = rng.uniform(-50, 50)
        c2 = rng.uniform(-50, 50)
        d = (f"M{x0:.1f},{y0:.1f} C{x0 + c1:.1f},{y0 - h * .35:.1f} {x0 - c2:.1f},{y0 - h * .7:.1f} "
             f"{x0 + c1 * .5:.1f},{y0 - h:.1f}")
        out.append(f'<path d="{d}" fill="none" stroke="{BLUE_LIGHT}" stroke-width="{rng.uniform(1, 2.6):.1f}" '
                   f'stroke-linecap="round" opacity="{rng.uniform(.35, .7):.2f}" filter="url(#softer)"/>')
    g = "".join(out)
    if side == "right":
        return f'<g transform="translate(806.1 0) scale(-1 1)">{g}</g>'
    return f"<g>{g}</g>"


def speckles(rng, n, box):
    x0, y0, x1, y1 = box
    dots = []
    for _ in range(n):
        r = rng.choice([.7, .8, 1, 1, 1.2, 1.5, 1.8])
        dots.append(f'<circle cx="{rng.uniform(x0, x1):.1f}" cy="{rng.uniform(y0, y1):.1f}" r="{r}" '
                    f'fill="{SPECK}" opacity="{rng.uniform(.55, 1):.2f}"/>')
    return "".join(dots)


def build_base():
    svg = read("base")
    rng = random.Random(51)
    lines = svg.split("\n")
    body_line = next(i for i, l in enumerate(lines) if 'class="cls-3" d="M801.3,418.6' in l)
    body_d = re.search(r'd="([^"]+)"', lines[body_line]).group(1)
    pad_line = next(i for i, l in enumerate(lines) if 'class="cls-8" d="M534.8,128' in l)
    pad_d = re.search(r'd="([^"]+)"', lines[pad_line]).group(1)

    defs = f"""
    <clipPath id="bodyClip"><path d="{body_d}"/></clipPath>
    <clipPath id="padClip"><path d="{pad_d}"/></clipPath>
    <linearGradient id="flameGrad" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="{BLUE_DEEP}"/>
      <stop offset=".45" stop-color="{BLUE}"/>
      <stop offset=".8" stop-color="{BLUE_LIGHT}" stop-opacity=".6"/>
      <stop offset="1" stop-color="{BLUE_LIGHT}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="flameGlow" cx=".5" cy=".7" r=".6">
      <stop offset="0" stop-color="{BLUE}" stop-opacity=".95"/>
      <stop offset=".6" stop-color="{BLUE_DEEP}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{BLUE_DEEP}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="centerGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a9cf0"/>
      <stop offset="1" stop-color="{BLUE_DEEP}"/>
    </linearGradient>
    <linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".10"/>
      <stop offset=".35" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
    <filter id="softer" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.1"/></filter>
  </defs>"""
    # Paint layer that sits on the black shell, under the wells/buttons/touchpad.
    # Center section: the DualSense-style blue lower-middle piece around the sticks.
    center = ('<path d="M196,282 C240,268 300,276 403,276 C506,276 566,268 610,282 '
              'L640,470 C600,440 560,430 520,428 L286,428 C246,430 206,440 166,470 Z" fill="url(#centerGrad)"/>')
    paint = (f'<g clip-path="url(#bodyClip)">'
             f'{speckles(rng, 520, (0, 90, 806, 470))}'
             f'{flames(rng, "left")}{flames(rng, "right")}'
             f'{center}'
             f'<path d="{body_d}" fill="url(#gloss)"/>'
             f'</g>')
    # insert after the body path and its 6% highlight group (3 lines: <g class="cls-4">, path, </g>)
    insert_at = body_line + 4
    assert lines[body_line + 3].strip() == "</g>", lines[body_line + 3]
    lines.insert(insert_at, paint)
    svg = "\n".join(lines)
    svg = svg.replace("</defs>", defs, 1)

    # touchpad speckles on top of the black pad
    svg = svg.replace("</svg>", f'<g clip-path="url(#padClip)">{speckles(rng, 110, (270, 120, 536, 275))}</g></svg>')

    svg = recolor(svg, {
        ".cls-6": f"fill: {BLUE_DEEP};",          # stick well outer rim
        ".cls-7": f"fill: {BLUE};",               # stick well face
        ".cls-22": f"fill: {BTN_RING};", ".cls-23": f"fill: {BTN_RING};",
        ".cls-24": f"fill: {BTN_RING};", ".cls-25": f"fill: {BTN_RING};",
    })
    return svg


# ---------- parts ----------
def build_face():
    g = '<radialGradient id="bg" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#3a3f48"/><stop offset=".45" stop-color="#15171c"/><stop offset="1" stop-color="#07080a"/></radialGradient>'
    svg = read("face").replace("<defs>", "<defs>" + g, 1)
    return recolor(svg, {
        # pressed row
        ".cls-1": f"fill: {PRESS};", ".cls-2": f"fill: {PRESS_RING};",
        ".cls-3": "fill: #ffffff;", ".cls-4": "fill: #ffffff;", ".cls-5": "fill: #ffffff;", ".cls-6": "fill: #ffffff;",
        # resting row: glossy black, faint symbols
        ".cls-7": "fill: url(#bg);", ".cls-8": f"fill: {BTN_RING};",
        ".cls-9": "fill: #4a505c;", ".cls-10": "fill: #4a505c;", ".cls-11": "fill: #4a505c;", ".cls-12": "fill: #4a505c;",
    })


def build_dpad():
    return recolor(read("dpad"), {
        ".cls-1": "fill: #1c1f26;",
        ".cls-3": f"fill: {PRESS};",
    })


def build_sticks():
    return recolor(read("sticks"), {
        ".cls-1": "fill: #17191d;", ".cls-2": "fill: #2c3038;", ".cls-3": "fill: #0d0e11;",
        ".cls-4": f"fill: {PRESS};", ".cls-5": f"fill: {PRESS_RING};", ".cls-6": "fill: #3fb8f5;",
    })


def build_triggers():
    return recolor(read("triggers"), {".cls-1": f"fill: {PRESS};", ".cls-2": f"fill: {PRESS_RING};"})


def build_bumper():
    return recolor(read("bumper"), {".cls-1": f"fill: {PRESS_RING};", ".cls-2": f"fill: {PRESS};"})


def build_touchpad():
    return recolor(read("touchpad"), {".cls-3": f"fill: {PRESS}; opacity: .55;", ".cls-4": f"fill: {PRESS}; opacity: .35;"})


def build_meta():
    return recolor(read("meta"), {".cls-1": f"fill: {PRESS};", ".cls-2": f"fill: {PRESS_RING};", ".cls-3": "fill: #06223a;"})


def build_start():
    return recolor(read("start"), {".cls-1": f"fill: {PRESS_RING};", ".cls-2": f"fill: {PRESS};"})


def main():
    parts = {
        "base": build_base(), "face": build_face(), "dpad": build_dpad(), "sticks": build_sticks(),
        "triggers": build_triggers(), "bumper": build_bumper(), "touchpad": build_touchpad(),
        "meta": build_meta(), "start": build_start(),
    }
    out = HERE / "parts"
    out.mkdir(exist_ok=True)
    for k, v in parts.items():
        (out / f"{k}.svg").write_text(v, encoding="utf-8")
    u = {k: uri(v) for k, v in parts.items()}

    # Selectors use .controller.ds4 so they beat both the black (.ds4) and white (.ds4.white) variants.
    css = f"""/* GPV DS4 classic skin - Blue Flame (black speckle shell, blue flames, blue center)
   Works with both "DS4" and "DS4 White" skins. Paste this file's URL into Edit CSS URL. */

.controller.ds4:not(.disconnected) {{ background-image: url("{u['base']}") !important; }}

.controller.ds4 .trigger {{ background-image: url("{u['triggers']}") !important; }}
.controller.ds4 .bumper {{ background-image: url("{u['bumper']}") !important; }}
.controller.ds4 .touchpad.pressed {{ background-image: url("{u['touchpad']}") !important; }}
.controller.ds4 .meta.pressed {{ background-image: url("{u['meta']}") !important; }}
.controller.ds4 .back, .controller.ds4 .start {{ background-image: url("{u['start']}") !important; }}
.controller.ds4 .button {{ background-image: url("{u['face']}") !important; }}
.controller.ds4 .stick {{ background-image: url("{u['sticks']}") !important; }}
.controller.ds4 .face {{ background-image: url("{u['dpad']}") !important; }}

/* glow on press */
.controller.ds4 .button.pressed,
.controller.ds4 .face.pressed,
.controller.ds4 .stick.pressed,
.controller.ds4 .meta.pressed {{ filter: drop-shadow(0 0 8px rgba(95, 200, 255, .9)); }}
.controller.ds4 .trigger,
.controller.ds4 .bumper.pressed {{ filter: drop-shadow(0 0 10px rgba(95, 200, 255, .8)); }}
"""
    (HERE / "blue-flame.css").write_text(css, encoding="utf-8")
    print("css bytes", len(css))


main()

