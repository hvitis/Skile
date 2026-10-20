"""Dish-type themes for render_recipe.py: line icons, accent palettes, and ornaments.

Icons are original 24x24 stroke drawings (currentColor), so they inherit the
colour of whatever element holds them.
"""

import math
from urllib.parse import quote

# name -> SVG inner markup on a 24x24 grid
ICONS = {
    "cookie": (
        '<path d="M21 12a9 9 0 1 1-9-9c0 1.7 1.3 3 3 3 0 1.7 1.3 3 3 3 0 1.7 1.3 3 3 3z"/>'
        '<g fill="currentColor" stroke="none"><circle cx="8.5" cy="9" r="1.2"/>'
        '<circle cx="12.5" cy="12.5" r="1.1"/><circle cx="8" cy="15" r="1.1"/>'
        '<circle cx="15.5" cy="16" r="1.2"/><circle cx="12" cy="7" r=".9"/></g>'
    ),
    "cake": (
        '<rect x="4" y="12" width="16" height="8" rx="1.5"/>'
        '<path d="M4 15c1.3 1.2 2.7 1.2 4 0s2.7-1.2 4 0 2.7 1.2 4 0 2.7-1.2 4 0"/>'
        '<path d="M2.5 20.5h19M12 12V8.5"/>'
        '<path d="M12 4.5c1 1 1 2.2 0 3-1-.8-1-2 0-3z" fill="currentColor"/>'
    ),
    "bread": (
        '<path d="M3 17.5c0-6 4-10.5 9-10.5s9 4.5 9 10.5v.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>'
        '<path d="M8 11l1.6 2.6M11.4 10l1.6 2.6M14.8 11l1.6 2.6"/>'
    ),
    "pie": (
        '<path d="M3 13.5h18l-1.8 5.2a1 1 0 0 1-.9.8H5.7a1 1 0 0 1-.9-.8z"/>'
        '<path d="M4.2 13.5C5.4 10.3 8.5 8 12 8s6.6 2.3 7.8 5.5"/>'
        '<path d="M9 10.6l.9 2.4M12 9.6v3.3M15 10.6l-.9 2.4"/>'
    ),
    "soup": (
        '<path d="M3 12h18c0 4.4-4 8-9 8s-9-3.6-9-8z"/><path d="M9 20.5h6"/>'
        '<path d="M8.5 9c-.9-1 .9-1.8 0-3s.9-2 0-3M12 9c-.9-1 .9-1.8 0-3s.9-2 0-3'
        'M15.5 9c-.9-1 .9-1.8 0-3s.9-2 0-3"/>'
    ),
    "stew": (
        '<path d="M4.5 11h15v6a3 3 0 0 1-3 3h-9a3 3 0 0 1-3-3z"/>'
        '<path d="M4.5 13.5h-2M19.5 13.5h2"/>'
        '<path d="M3.5 11c1-2.6 4.4-4 8.5-4s7.5 1.4 8.5 4M12 7V5.2M10.6 5.2h2.8"/>'
    ),
    "pasta": (
        '<path d="M3 13h18c0 3.9-4 7-9 7s-9-3.1-9-7z"/>'
        '<path d="M6 13c.6-2.4 2.6-2.6 2-5.2M9.5 13c.6-2.4 2.6-2.6 2-5.2"/>'
        '<path d="M14.5 3v3M16 3v3M17.5 3v3M14.5 6a1.5 1.5 0 0 0 3 0M16 7.5V13"/>'
    ),
    "salad": (
        '<path d="M3 12h18c0 4.4-4 8-9 8s-9-3.6-9-8z"/>'
        '<path d="M6.5 12c-.8-3.2 1.2-5.8 4.4-6.2.4 3.1-1.3 5.7-4.4 6.2z"/>'
        '<path d="M12.5 12c0-3 2.5-5.2 5.7-4.8-.3 2.9-2.7 4.9-5.7 4.8z"/>'
        '<circle cx="12" cy="9.6" r="1.4"/>'
    ),
    "meat": (
        '<path d="M10.3 13.7a6 6 0 1 1 3.9 1.7c-1 0-1.9-.3-2.7-.8z"/>'
        '<path d="M10.8 14.2l-3.4 3.4M7.4 17.6a1.6 1.6 0 1 0-2 2 1.6 1.6 0 1 0 2-2z"/>'
        '<path d="M13.5 6.5a3.5 3.5 0 0 1 3.5 2.6"/>'
    ),
    "fish": (
        '<path d="M7 12c2.5-4 5.5-6 9-6 3 0 5 2.5 6 6-1 3.5-3 6-6 6-3.5 0-6.5-2-9-6z"/>'
        '<path d="M7 12 2.5 8.5v7z"/><path d="M13.5 9.2c.9 1.8.9 3.8 0 5.6"/>'
        '<circle cx="18" cy="10.8" r=".9" fill="currentColor" stroke="none"/>'
    ),
    "egg": (
        '<path d="M12 3.5c2.8 0 4.2 1.8 6 3s3.6 3 3 6-2.8 3.6-3.8 5.4-2.8 3.6-5.6 2.6'
        '-4.6-1.8-6.4-3.2S2.4 13 3.4 10 7 5.2 9 4.2s2-.7 3-.7z"/>'
        '<circle cx="11.5" cy="12" r="3.3"/><path d="M10.2 10.9a1.6 1.6 0 0 1 1.3-.9"/>'
    ),
    "pizza": (
        '<path d="M12 21 4 6.5C6.4 4.9 9.1 4 12 4s5.6.9 8 2.5z"/>'
        '<path d="M5.4 9c2-1.2 4.2-1.9 6.6-1.9s4.6.7 6.6 1.9"/>'
        '<circle cx="10" cy="11.4" r="1.2"/><circle cx="14.2" cy="12.4" r="1.2"/>'
        '<circle cx="12" cy="16" r="1"/>'
    ),
    "drink": (
        '<path d="M5.5 7h13l-1.6 12.9a1.2 1.2 0 0 1-1.2 1.1H8.3a1.2 1.2 0 0 1-1.2-1.1z"/>'
        '<path d="M6.1 11.5h11.8M13 7l2.4-4.5h2.6"/><rect x="9" y="14" width="2.6" height="2.6" rx=".5"/>'
    ),
    "dessert": (
        '<path d="M7 10.5a5 5 0 0 1 10 0"/><path d="M6 10.5h12"/>'
        '<path d="M7 10.5l5 11 5-11"/><path d="M9.2 13.5l3.8 3.4M14.8 13.5 11 16.9"/>'
    ),
    "sauce": (
        '<path d="M6 9.5h12V19a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z"/>'
        '<rect x="6.8" y="5.5" width="10.4" height="4" rx="1"/>'
        '<rect x="9" y="13" width="6" height="4.5" rx=".8"/>'
    ),
    "vegetable": (
        '<path d="M13.6 8c1.7-.4 3.2 1.1 2.8 2.8-.3 1.5-1.8 2.4-3.1 3.2L4.5 19.5l5.2-8.6'
        'c.8-1.4 2.2-2.6 3.9-2.9z"/>'
        '<path d="M15.6 8.4C16.4 5.8 18.3 4.2 21 4.3c0 2.7-1.9 4.6-4.6 4.9'
        'M15.6 8.4c-.4-2.2.2-4.3 1.8-5.9"/><path d="M9.3 13l1.4 1.4M11.4 10.5l1.2 1.2"/>'
    ),
    "other": (
        '<path d="M6.5 16.5v4h11v-4"/>'
        '<path d="M6.5 16.5C4 16 2.5 14.2 2.5 12a4 4 0 0 1 5-3.9A4.6 4.6 0 0 1 12 4.5'
        'a4.6 4.6 0 0 1 4.5 3.6 4 4 0 0 1 5 3.9c0 2.2-1.5 4-4 4.5z"/>'
        '<path d="M10 16.5V13M14 16.5V13"/>'
    ),
    # utility icons for the header pills
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "yield": (
        '<path d="M7 3v7M5 3v4a2 2 0 0 0 4 0V3M7 10v11"/>'
        '<path d="M17 21V3c-2 0-3.5 2.5-3.5 6.5V13H17"/>'
    ),
}

DISH_TYPES = [name for name in ICONS if name not in ("clock", "yield")]

# name -> (accent, soft tint, ink). Ink carries text; accent carries decoration.
PALETTES = {
    "cookie":    ("#E07A1F", "#FFF1E2", "#7E3F0E"),
    "cake":      ("#E2557F", "#FFEAF1", "#862244"),
    "bread":     ("#C98A2E", "#FBF1DE", "#6E4812"),
    "pie":       ("#C4622D", "#FCEBDF", "#713318"),
    "soup":      ("#E2533B", "#FFEAE5", "#86281A"),
    "stew":      ("#B5562C", "#F9E9DF", "#682D15"),
    "pasta":     ("#E5A11B", "#FFF5DC", "#7A5407"),
    "salad":     ("#4E9F3D", "#EAF6E5", "#285A1E"),
    "meat":      ("#C2412F", "#FBE6E2", "#712118"),
    "fish":      ("#1E8E9E", "#E1F4F6", "#0E515B"),
    "egg":       ("#E9AE10", "#FFF7DA", "#735504"),
    "pizza":     ("#D9531E", "#FFEDE3", "#7E2C0D"),
    "drink":     ("#7C55C4", "#F0EAFB", "#45277A"),
    "dessert":   ("#D9468F", "#FCE8F2", "#801E4B"),
    "sauce":     ("#B0384A", "#F8E5E8", "#661D28"),
    "vegetable": ("#3F9160", "#E6F4EB", "#1F5034"),
    "other":     ("#E07A1F", "#FFF1E2", "#7E3F0E"),
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS[name]}</svg>')


def mix(hex_a, hex_b, t):
    """Blend two #RRGGBB colours: t=0 gives a, t=1 gives b."""
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def data_uri(svg):
    return "data:image/svg+xml;charset=utf-8," + quote(svg, safe=" =:/;,'")


def background_tile(dish, accent):
    """A wallpaper tile: two tilted dish icons and a scatter of dots."""
    glyph = ICONS[dish]
    stroke = (f'fill="none" stroke="{accent}" stroke-width="1.4" '
              f'stroke-linecap="round" stroke-linejoin="round"')
    return data_uri(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">'
        f'<g opacity="0.10" color="{accent}">'
        f'<g transform="translate(10 12) rotate(-12 18 18) scale(1.5)" {stroke}>{glyph}</g>'
        f'<g transform="translate(68 70) rotate(14 18 18) scale(1.5)" {stroke}>{glyph}</g>'
        f'<g fill="{accent}"><circle cx="86" cy="22" r="2.2"/><circle cx="24" cy="88" r="2.2"/>'
        f'<circle cx="104" cy="50" r="1.4"/><circle cx="52" cy="104" r="1.4"/>'
        f'<circle cx="58" cy="44" r="1.2"/></g></g></svg>'
    )


def corner_ornament(accent, ink):
    """A leafy garland hugging the top-left corner; CSS flips it for the others."""
    p0, p1, p2, p3 = (14, 94), (14, 44), (44, 14), (94, 14)

    def point(t):
        u = 1 - t
        return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                     for a, b, c, d in zip(p0, p1, p2, p3))

    def tangent(t):
        u = 1 - t
        dx, dy = (3 * u * u * (b - a) + 6 * u * t * (c - b) + 3 * t * t * (d - c)
                  for a, b, c, d in zip(p0, p1, p2, p3))
        length = math.hypot(dx, dy)
        return dx / length, dy / length

    leaf = "M0 0C3.5-4.5 9.5-5.5 13.5-3 9.5 1.2 3.5 1.6 0 0z"
    parts = [
        f'<path d="M{p0[0]} {p0[1]}C{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}" '
        f'stroke="{accent}" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
        f'<path d="M25 84C26 54 54 26 84 25" stroke="{accent}" stroke-width="1.8" fill="none" '
        f'stroke-linecap="round" stroke-dasharray="0.1 6"/>',
    ]
    for t in (0.16, 0.34, 0.66, 0.84):
        x, y = point(t)
        dx, dy = tangent(t)
        heading = math.degrees(math.atan2(dy, dx))
        for turn, opacity in ((-42, 1), (42, 0.75)):
            parts.append(f'<path d="{leaf}" fill="{accent}" opacity="{opacity}" '
                         f'transform="translate({x:.1f} {y:.1f}) rotate({heading + turn:.1f})"/>')
    x, y = point(0.5)
    dx, dy = tangent(0.5)
    nx, ny = -dy, dx  # inner normal, towards the page centre
    for offset, along, r in ((6, 0, 3.2), (11, -4, 2.2), (11, 4, 2.2)):
        parts.append(f'<circle cx="{x + nx * offset + dx * along:.1f}" '
                     f'cy="{y + ny * offset + dy * along:.1f}" r="{r}" fill="{ink}"/>')
    for end in (p0, p3):
        parts.append(f'<circle cx="{end[0]}" cy="{end[1]}" r="2.8" fill="{ink}"/>')
    return f'<svg viewBox="0 0 100 100" aria-hidden="true">{"".join(parts)}</svg>'
