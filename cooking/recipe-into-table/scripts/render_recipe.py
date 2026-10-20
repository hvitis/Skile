#!/usr/bin/env python3
"""Render recipe trees (JSON) as Cooking for Engineers tables: HTML, optionally PDF.

Usage:
    render_recipe.py RECIPE.json [MORE.json ...] [-o OUT.html] [--pdf]
                     [--portrait] [--font-pt N] [--no-webfonts]

Layout: every ingredient is one row in the leftmost column. Each action sits in
the column equal to its height in the tree (1 + tallest input), spans the rows
of all ingredients beneath it, and stretches right (colspan) to meet its parent.
The root action is therefore always the single rightmost cell.

Each recipe gets one A4 page, themed by its dish_type (icon, palette, wallpaper,
corner garlands); several recipes render into one document, one page each.
Page labels default to Polish (lang "pl").

Fitting: each page is landscape in the type size its grid suggests. A table that
does not fit gets smaller type, in half points down to MIN_FONT_PT; only one that
fits no landscape size turns portrait (down to LAST_FONT_PT). Chrome fits the pages
with a script in the HTML (so does any browser printing it); WeasyPrint with
fit_weasyprint. --portrait and --font-pt pin the page instead.

Stdlib only. PDF engines tried in order: Chrome/Chromium/Edge (headless),
WeasyPrint (module or CLI). Exit codes: 0 ok, 1 PDF failed (HTML written),
2 invalid recipe JSON.
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep installed skill folders free of __pycache__
from recipe_theme import (DISH_TYPES, PALETTES, background_tile, corner_ornament,
                          icon, mix)

MAX_ROWS_ONE_PAGE = 30
MAX_COLS_ONE_PAGE = 9
MIN_FONT_PT = 7.0  # landscape goes down to this
LAST_FONT_PT = 6.0  # portrait, for a table no landscape size holds
PAD_FROM_PT = 8.5  # the smallest automatic size; below it the cells' padding shrinks with the type
LABELS = {
    "en": {"before": "Before you start", "finish": "To finish", "tips": "Tips",
           "prep": "Prep", "cook": "Cook", "total": "Total", "source": "Source"},
    "pl": {"before": "Zanim zaczniesz", "finish": "Na koniec", "tips": "Wskazówki",
           "prep": "Przygotowanie", "cook": "Gotowanie", "total": "Razem", "source": "Źródło"},
    "de": {"before": "Bevor es losgeht", "finish": "Zum Schluss", "tips": "Tipps",
           "prep": "Vorbereitung", "cook": "Garzeit", "total": "Gesamt", "source": "Quelle"},
    "es": {"before": "Antes de empezar", "finish": "Para terminar", "tips": "Consejos",
           "prep": "Preparación", "cook": "Cocción", "total": "Total", "source": "Fuente"},
    "fr": {"before": "Avant de commencer", "finish": "Pour finir", "tips": "Astuces",
           "prep": "Préparation", "cook": "Cuisson", "total": "Total", "source": "Source"},
    "it": {"before": "Prima di iniziare", "finish": "Per finire", "tips": "Consigli",
           "prep": "Preparazione", "cook": "Cottura", "total": "Totale", "source": "Fonte"},
}
# Fraunces with its softest serifs (SOFT 100) and no wonky letters (WONK 0); both fonts carry
# every Polish letter.
WEBFONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,500..600,100,0"
            "&family=Nunito:wght@400;600;800&display=block")


class RecipeError(ValueError):
    pass


# --- validation -------------------------------------------------------------

def validate_node(node, path):
    if not isinstance(node, dict):
        raise RecipeError(f"{path}: expected an object, got {type(node).__name__}")
    is_leaf = "ingredient" in node
    is_action = "action" in node
    if is_leaf == is_action:
        raise RecipeError(f"{path}: needs exactly one of 'ingredient' or 'action'")
    if is_leaf:
        if "inputs" in node:
            raise RecipeError(f"{path}: an ingredient cannot have 'inputs'")
        return
    inputs = node.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise RecipeError(f"{path} ('{node['action']}'): 'inputs' must be a non-empty list")
    for i, child in enumerate(inputs):
        validate_node(child, f"{path}.inputs[{i}]")


def validate(recipe):
    if not isinstance(recipe, dict):
        raise RecipeError("top level must be an object")
    if not recipe.get("title"):
        raise RecipeError("missing 'title'")
    dish = recipe.get("dish_type", "other")
    if dish not in DISH_TYPES:
        raise RecipeError(f"unknown dish_type '{dish}'; use one of: {', '.join(DISH_TYPES)}")
    steps = recipe.get("steps")
    if not isinstance(steps, dict) or "action" not in steps:
        raise RecipeError("'steps' must be a single action node (the final step)")
    validate_node(steps, "steps")
    labels = recipe.get("labels", {})
    if not isinstance(labels, dict) or set(labels) - set(LABELS["en"]):
        raise RecipeError(f"'labels' may only override: {', '.join(LABELS['en'])}")
    for key in ("setup", "finish", "notes"):
        value = recipe.get(key, [])
        if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
            raise RecipeError(f"'{key}' must be a list of strings")


# --- layout -----------------------------------------------------------------

def height(node):
    if "ingredient" in node:
        return 0
    return 1 + max(height(child) for child in node["inputs"])


def layout(root):
    """Return rows: a list of rows, each a list of cell dicts in column order."""
    rows = []

    def place(node, parent_height):
        h = height(node)
        cell = {"node": node, "colspan": parent_height - h}
        if "ingredient" in node:
            cell["rowspan"] = 1
            rows.append([cell])
            return
        first_row = len(rows)
        for child in node["inputs"]:
            place(child, h)
        cell["rowspan"] = len(rows) - first_row
        # Post-order append keeps each row's cells in ascending column order.
        rows[first_row].append(cell)

    place(root, height(root) + 1)
    return rows


def leaves(node):
    if "ingredient" in node:
        yield node
    else:
        for child in node["inputs"]:
            yield from leaves(child)


def lint(recipe, rows, total_cols):
    warnings = []
    seen = {}
    for leaf in leaves(recipe["steps"]):
        key = leaf["ingredient"].strip().lower()
        seen[key] = seen.get(key, 0) + 1
    for name, count in seen.items():
        if count > 1:
            warnings.append(
                f"'{name}' appears {count} times; if it is divided, make each portion "
                "distinguishable (e.g. 'sugar (for topping)')"
            )
    if len(rows) > MAX_ROWS_ONE_PAGE:
        warnings.append(f"{len(rows)} ingredient rows; the page will need small type, "
                        "portrait (consider one page per component)")
    if total_cols > MAX_COLS_ONE_PAGE:
        warnings.append(f"{total_cols} columns; likely too wide for one page")
    return warnings


# --- HTML -------------------------------------------------------------------

CSS = """
@page { size: A4 landscape; margin: 0; }
@page portrait { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #FFFCF5; }
body {
  font-family: "Nunito", "Avenir Next", "Segoe UI", "Helvetica Neue", Arial, system-ui, sans-serif;
  color: #2B2420; -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
.display, h1, .verb, .tag, .pill {
  font-family: "Fraunces", "Iowan Old Style", Georgia, serif;
  font-variation-settings: "SOFT" 100, "WONK" 0;
}
.page {
  position: relative; width: 297mm; min-height: 209.5mm;
  padding: 13mm 22mm 12mm; line-height: 1.25; overflow: hidden;
  background-color: #FFFCF5; background-size: 34mm 34mm;
}
.page.portrait { page: portrait; width: 210mm; min-height: 296.5mm; }
.page + .page { break-before: page; page-break-before: always; }
.corner { position: absolute; width: 27mm; height: 27mm; }
.corner svg { display: block; width: 100%; height: 100%; }
.corner.tl { top: 3mm; left: 3mm; }
.corner.tr { top: 3mm; right: 3mm; transform: scaleX(-1); }
.corner.bl { bottom: 3mm; left: 3mm; transform: scaleY(-1); }
.corner.br { bottom: 3mm; right: 3mm; transform: scale(-1, -1); }
.content { position: relative; }
header { display: flex; align-items: center; gap: 4.5mm; margin-bottom: 5mm; }
.badge {
  flex: none; width: 17mm; height: 17mm; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--soft); border: 2px solid var(--accent); color: var(--ink);
  box-shadow: 0 0 0 1.2mm #FFFCF5, 0 0 0 1.6mm var(--rule);
}
.badge svg { width: 10.5mm; height: 10.5mm; }
h1 { font-weight: 600; font-size: 2.15em; line-height: 1.05; color: var(--ink); margin: 0 0 1.8mm; }
.meta { display: flex; flex-wrap: wrap; gap: 2mm; }
.pill {
  display: inline-flex; align-items: center; gap: 1.2mm; padding: 0.5mm 2.8mm;
  border-radius: 99px; background: #fff; border: 1.3px solid var(--rule);
  color: var(--ink); font-size: 0.86em; font-weight: 500;
}
.pill svg { width: 1.15em; height: 1.15em; color: var(--accent); }
.sheet {
  background: #fff; border: 2px solid var(--accent); border-radius: 4mm; overflow: hidden;
  box-shadow: 0 1.4mm 0 var(--shadow);
}
table.recipe { border-collapse: collapse; border-style: hidden; width: 100%; }
table.recipe td {
  border: 1.3px solid var(--rule); vertical-align: middle;
  padding: calc(1.6mm * var(--pad, 1)) calc(2.8mm * var(--pad, 1));
}
td.ing { text-align: left; background: #fff; }
td.ing .amt { font-weight: 800; color: var(--ink); white-space: nowrap; margin-right: 0.35em; }
td.act { text-align: center; background: var(--soft); }
td.act .verb { font-weight: 600; font-size: 1.05em; color: var(--ink); white-space: nowrap; }
td.act .detail { display: block; font-size: 0.84em; color: #5E544C; margin-top: 0.4mm; }
td.final { background: var(--ink); }
td.final .verb, td.final .detail { color: #fff; }
td.final svg { display: block; width: 2.4em; height: 2.4em; margin: 0 auto 1.2mm; color: #fff; }
td.band { background: var(--band); text-align: left; }
.tag {
  display: inline-block; margin-right: 2mm; padding: 0.2mm 2.4mm; border-radius: 99px;
  background: var(--ink); color: #fff; font-weight: 500; font-size: 0.82em; letter-spacing: 0.02em;
}
.notes {
  margin-top: 4.5mm; padding: 2.4mm 4mm; border-radius: 3mm;
  background: rgba(255, 255, 255, 0.88); border: 1.3px dashed var(--accent);
}
.notes ul { margin: 1.6mm 0 0; padding-left: 5mm; }
.notes li { margin-bottom: 0.8mm; }
.source { margin-top: 3mm; color: #6B6058; font-size: 0.84em; }
@media screen {
  html, body { background: #E8E2D6; }
  body { padding: 8mm 0; }
  .page { margin: 0 auto 8mm; box-shadow: 0 2px 14px rgba(0, 0, 0, 0.15); }
}
"""


def esc(text):
    return html.escape(str(text), quote=True)


def cell_html(cell, is_root, dish):
    node = cell["node"]
    attrs = []
    if cell["rowspan"] > 1:
        attrs.append(f'rowspan="{cell["rowspan"]}"')
    if cell["colspan"] > 1:
        attrs.append(f'colspan="{cell["colspan"]}"')
    if "ingredient" in node:
        cls = "ing"
        amount = node.get("amount")
        body = (f'<span class="amt">{esc(amount)}</span>' if amount else "") + esc(node["ingredient"])
    else:
        cls = "act final" if is_root else "act"
        body = icon(dish) if is_root else ""
        body += f'<span class="verb">{esc(node["action"])}</span>'
        if node.get("detail"):
            body += f'<span class="detail">{esc(node["detail"])}</span>'
    attrs.insert(0, f'class="{cls}"')
    return f"<td {' '.join(attrs)}>{body}</td>"


def auto_font_pt(n_rows, n_cols):
    if n_rows > 26 or n_cols > 8:
        return 8.5
    if n_rows > 18 or n_cols > 7:
        return 9.5
    if n_rows > 12:
        return 11
    return 12.5


def build_page(recipe, font_pt=None, portrait=False, fit=False):
    """Return (section_html, rows, total_cols) for one recipe. fit: the page fits itself in a
    browser, starting from font_pt."""
    root = recipe["steps"]
    dish = recipe.get("dish_type", "other")
    accent, soft, ink = PALETTES[dish]
    rows = layout(root)
    total_cols = height(root) + 1
    font_pt = font_pt or auto_font_pt(len(rows), total_cols)
    text = {**LABELS.get(recipe.get("lang", "pl"), LABELS["pl"]), **recipe.get("labels", {})}

    style = (
        f"--accent:{accent};--soft:{soft};--ink:{ink};--rule:{mix(accent, '#FFFFFF', 0.45)};"
        f"--band:{mix(accent, '#FFFFFF', 0.84)};--shadow:{mix(accent, '#FFFFFF', 0.62)};"
        f"font-size:{font_pt}pt;--pad:{round(min(1, font_pt / PAD_FROM_PT), 3)};"
        f"background-image:url(&quot;{background_tile(dish, accent)}&quot;)"
    )
    corner = corner_ornament(accent, ink)
    pills = []
    if recipe.get("yield"):
        pills.append(f'<span class="pill">{icon("yield")}{esc(recipe["yield"])}</span>')
    for key, label in (("prep_time", "prep"), ("cook_time", "cook"), ("total_time", "total")):
        if recipe.get(key):
            pills.append(f'<span class="pill">{icon("clock")}{esc(text[label])} {esc(recipe[key])}</span>')

    classes = f"page dish-{dish}" + (" portrait" if portrait else "")
    fitting = f' data-fit-pt="{font_pt}"' if fit else ""
    out = [f'<section class="{classes}"{fitting} style="{style}">']
    out += [f'<div class="corner {pos}">{corner}</div>' for pos in ("tl", "tr", "bl", "br")]
    out.append('<div class="content"><header>')
    out.append(f'<div class="badge">{icon(dish)}</div>')
    out.append(f'<div><h1>{esc(recipe["title"])}</h1>')
    if pills:
        out.append(f'<div class="meta">{"".join(pills)}</div>')
    out.append("</div></header>")

    out.append('<div class="sheet"><table class="recipe"><tbody>')
    for line in recipe.get("setup", []):
        out.append(f'<tr><td class="band" colspan="{total_cols}">'
                   f'<span class="tag">{esc(text["before"])}</span>{esc(line)}</td></tr>')
    for row in rows:
        out.append("<tr>" + "".join(cell_html(c, c["node"] is root, dish) for c in row) + "</tr>")
    for line in recipe.get("finish", []):
        out.append(f'<tr><td class="band" colspan="{total_cols}">'
                   f'<span class="tag">{esc(text["finish"])}</span>{esc(line)}</td></tr>')
    out.append("</tbody></table></div>")

    if recipe.get("notes"):
        items = "".join(f"<li>{esc(n)}</li>" for n in recipe["notes"])
        out.append(f'<div class="notes"><span class="tag">{esc(text["tips"])}</span><ul>{items}</ul></div>')
    if recipe.get("source"):
        out.append(f'<div class="source">{esc(text["source"])}: {esc(recipe["source"])}</div>')
    out.append("</div></section>")
    return "\n".join(out), rows, total_cols


def build_html(recipes, portrait=False, font_pt=None, webfonts=True, layouts=None, fit=False):
    """Return (document_html, [(rows, total_cols), ...]). Every page is portrait or not, in
    font_pt (None: its grid's size), unless layouts gives (portrait, font_pt) per recipe.
    fit: the pages fit themselves in a browser (FIT_JS)."""
    layouts = layouts or [(portrait, font_pt)] * len(recipes)
    pages, grids = [], []
    for recipe, (page_portrait, page_pt) in zip(recipes, layouts):
        section, rows, total_cols = build_page(recipe, page_pt, page_portrait, fit)
        pages.append(section)
        grids.append((rows, total_cols))

    title = recipes[0]["title"] if len(recipes) == 1 else f"{len(recipes)} recipes"
    lang = recipes[0].get("lang", "pl")
    head = [
        "<!doctype html>",
        f'<html lang="{esc(lang)}"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)}</title>",
    ]
    if webfonts:
        head.append(f'<link rel="stylesheet" href="{esc(WEBFONTS)}">')
    head.append(f"<style>{CSS}</style></head><body>")
    script = [f"<script>{FIT_JS}</script>"] if fit else []
    return "\n".join(head + pages + script + ["</body></html>"]) + "\n", grids


# The same fitting as fit_weasyprint, measured live in a browser: headless Chrome runs it before
# printing, and so does any browser printing the HTML.
FIT_JS = """
(() => {
  const MIN = %(min)s, LAST = %(last)s, PAD_FROM = %(pad)s;
  const spills = (page) => {
    const sheet = page.querySelector(".sheet");
    const table = page.querySelector("table.recipe");
    const tall = page.getBoundingClientRect().height > parseFloat(getComputedStyle(page).minHeight) + 1;
    return tall || table.getBoundingClientRect().width > sheet.clientWidth + 1;
  };
  const fit = (page) => {
    const start = parseFloat(page.dataset.fitPt);
    for (const [portrait, smallest] of [[false, MIN], [true, LAST]]) {
      page.classList.toggle("portrait", portrait);
      for (let pt = start; pt >= smallest; pt -= 0.5) {
        page.style.fontSize = pt + "pt";
        page.style.setProperty("--pad", Math.min(1, pt / PAD_FROM));
        if (!spills(page)) return;
      }
    }
  };
  const run = () => document.querySelectorAll(".page[data-fit-pt]").forEach(fit);
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(run);
})();
""" % {"min": MIN_FONT_PT, "last": LAST_FONT_PT, "pad": PAD_FROM_PT}


# --- fitting (WeasyPrint) -----------------------------------------------------

def font_sizes(largest, smallest):
    """Half-point steps from largest down to smallest."""
    return [largest - 0.5 * step for step in range(int((largest - smallest) / 0.5) + 1)]


def _boxes(box):
    yield box
    for child in getattr(box, "children", None) or ():
        yield from _boxes(child)


def fits(document):
    """Whether every page of a WeasyPrint document holds its recipe whole: the page's box no
    taller than the paper and the table no wider than its sheet. A page count alone does not
    tell: the table cannot break across pages (the final step spans every row), so the page's
    hidden overflow clips it. WeasyPrint keeps the layout on the private Page._page_box."""
    from weasyprint.formatting_structure.boxes import TableBox  # noqa: PLC0415

    for page in document.pages:
        sheet = None
        for box in _boxes(page._page_box):
            element = getattr(box, "element", None)
            classes = (element.get("class") or "").split() if element is not None else []
            if "page" in classes and box.margin_height() > page.height + 0.5:
                return False
            if "sheet" in classes:
                sheet = box
            elif (isinstance(box, TableBox) and sheet is not None
                  and box.margin_width() > sheet.width + 0.5):
                return False
    return True


def _largest_fit(render, portrait, sizes):
    """((portrait, size), document) for the largest of sizes (largest first) whose one page
    holds the recipe, by bisection (smaller type never fits worse); None when none does."""
    low, high, best = 0, len(sizes) - 1, None
    while low <= high:
        middle = (low + high) // 2
        document = render(portrait, sizes[middle])
        if len(document.pages) == 1 and fits(document):
            best, high = ((portrait, sizes[middle]), document), middle - 1
        else:
            low = middle + 1
    return best


def fit_weasyprint(recipes, webfonts=True, stylesheets=(), font_config=None):
    """Return (WeasyPrint document, [(portrait, font_pt), ...]): each recipe on one page,
    landscape in its grid's size or the largest smaller one that fits (down to MIN_FONT_PT),
    else portrait (down to LAST_FONT_PT), else portrait in LAST_FONT_PT."""
    import weasyprint  # noqa: PLC0415

    def render(chosen, layouts):
        page, grids = build_html(chosen, layouts=layouts, webfonts=webfonts)
        document = weasyprint.HTML(string=page).render(
            stylesheets=list(stylesheets), font_config=font_config)
        return document, grids

    fitted = []
    for recipe in recipes:
        def render_one(portrait, font_pt, recipe=recipe):
            return render([recipe], [(portrait, font_pt)])[0]

        document, grids = render([recipe], [(False, None)])
        rows, total_cols = grids[0]
        auto = auto_font_pt(len(rows), total_cols)
        if len(document.pages) == 1 and fits(document):
            fitted.append(((False, auto), document))
            continue
        fitted.append(
            _largest_fit(render_one, False, font_sizes(auto, MIN_FONT_PT)[1:])
            or _largest_fit(render_one, True, font_sizes(auto, LAST_FONT_PT))
            or ((True, LAST_FONT_PT), render_one(True, LAST_FONT_PT))
        )
    layouts = [layout for layout, _ in fitted]
    if len(recipes) == 1:
        return fitted[0][1], layouts
    return render(recipes, layouts)[0], layouts


# --- PDF --------------------------------------------------------------------

def find_chrome():
    env = os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    mac_apps = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    for app in mac_apps:
        if Path(app).exists():
            return app
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                 "microsoft-edge", "msedge", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def pdf_with_chrome(chrome, html_path, pdf_path):
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            chrome, "--headless", "--disable-gpu", f"--user-data-dir={profile}",
            "--no-pdf-header-footer", "--print-to-pdf-no-header",
            "--virtual-time-budget=15000",  # let web fonts arrive before printing
            f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri(),
        ]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        subprocess.run(cmd, check=True, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pdf_with_weasyprint(html_path, pdf_path, recipes=None, webfonts=True):
    """recipes: fit their pages (fit_weasyprint) rather than print the HTML as it is."""
    try:
        import weasyprint  # noqa: PLC0415
    except ImportError:
        cli = shutil.which("weasyprint")
        if not cli:
            raise FileNotFoundError("weasyprint not installed")
        subprocess.run([cli, str(html_path), str(pdf_path)], check=True, timeout=120)
        return "weasyprint CLI, not fitted"
    if not recipes:
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return "weasyprint"
    document, layouts = fit_weasyprint(recipes, webfonts=webfonts)
    document.write_pdf(str(pdf_path))
    fitted = ", ".join(f"{'portrait' if portrait else 'landscape'} {font_pt} pt"
                       for portrait, font_pt in layouts)
    return f"weasyprint, fitted: {fitted}"


def render_pdf(html_path, pdf_path, recipes=None, webfonts=True):
    """Return the engine used; raise RuntimeError if every engine fails. recipes: fit them
    (Chrome runs the HTML's own FIT_JS)."""
    errors = []
    chrome = find_chrome()
    if chrome:
        try:
            pdf_with_chrome(chrome, html_path, pdf_path)
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                return f"chrome ({Path(chrome).name}){', fitted' if recipes else ''}"
            errors.append("chrome: produced no output")
        except (subprocess.SubprocessError, OSError) as exc:
            errors.append(f"chrome: {exc}")
    else:
        errors.append("chrome: not found (set CHROME_PATH to override)")
    try:
        return pdf_with_weasyprint(html_path, pdf_path, recipes, webfonts)
    except Exception as exc:  # noqa: BLE001 - report any engine failure
        errors.append(f"weasyprint: {exc}")
    raise RuntimeError("; ".join(errors))


def count_pages(pdf_path):
    data = pdf_path.read_bytes()
    count = len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))
    return count or None  # None: pages live in compressed object streams


# --- CLI --------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("recipes", type=Path, nargs="+", help="recipe tree JSON file(s)")
    parser.add_argument("-o", "--out", type=Path,
                        help="output HTML (default: alongside the JSON; required for several)")
    parser.add_argument("--pdf", action="store_true", help="also render a PDF next to the HTML")
    parser.add_argument("--portrait", action="store_true",
                        help="portrait, not fitted (default: fitted, landscape first)")
    parser.add_argument("--font-pt", type=float,
                        help="this base font size, not fitted (default: fitted)")
    parser.add_argument("--no-webfonts", action="store_true",
                        help="use system fonts only (offline rendering)")
    args = parser.parse_args(argv)

    if len(args.recipes) > 1 and not args.out:
        parser.error("several recipes need -o OUT.html")

    recipes = []
    for path in args.recipes:
        try:
            recipe = json.loads(path.read_text(encoding="utf-8"))
            validate(recipe)
        except (OSError, json.JSONDecodeError, RecipeError) as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            return 2
        recipes.append(recipe)

    fit = not args.portrait and args.font_pt is None
    document, grids = build_html(recipes, args.portrait, args.font_pt,
                                 webfonts=not args.no_webfonts, fit=fit)
    html_path = args.out or args.recipes[0].with_suffix(".html")
    html_path.write_text(document, encoding="utf-8")
    print(f"html: {html_path}")
    for recipe, (rows, total_cols) in zip(recipes, grids):
        print(f"  {recipe['title']}: {len(rows)} ingredient rows x {total_cols} columns "
              f"({recipe.get('dish_type', 'other')})")
        if recipe.get("lang", "pl") not in LABELS and not recipe.get("labels"):
            print(f"warning: {recipe['title']}: no built-in labels for lang "
                  f"'{recipe['lang']}'; add a 'labels' object", file=sys.stderr)
        for warning in lint(recipe, rows, total_cols):
            print(f"warning: {recipe['title']}: {warning}", file=sys.stderr)

    if not args.pdf:
        return 0
    pdf_path = html_path.with_suffix(".pdf")
    try:
        engine = render_pdf(html_path, pdf_path, recipes if fit else None,
                            webfonts=not args.no_webfonts)
    except RuntimeError as exc:
        print(f"pdf: failed ({exc})", file=sys.stderr)
        return 1
    pages = count_pages(pdf_path)
    print(f"pdf: {pdf_path}  (engine: {engine}, pages: {pages if pages else 'unknown'})")
    if pages and pages > len(recipes):
        print(f"warning: {pages} pages for {len(recipes)} recipe(s); a table spills past its page",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
