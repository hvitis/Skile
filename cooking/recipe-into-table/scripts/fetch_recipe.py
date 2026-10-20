#!/usr/bin/env python3
"""Extract recipe text from a URL, a video, or a local file, for building a recipe tree.

Usage:
    fetch_recipe.py SOURCE [-o OUT.md] [--full-text] [--max-chars N]

SOURCE is one of:
  - a recipe web page URL: schema.org Recipe data (JSON-LD) when the page has it,
    otherwise the page's readable text (--full-text appends it either way)
  - a video URL (YouTube, Vimeo, TikTok, Instagram, Facebook, Dailymotion):
    title, description, chapters and captions, via yt-dlp
  - a local file: .pdf (pdftotext), .docx, .html/.htm, .txt/.md, or anything
    pandoc can read (.odt, .rtf, .epub, ...)

Images are not handled here: view them directly to read the recipe.

Stdlib only; yt-dlp, pdftotext and pandoc are used when installed. Output is
Markdown on stdout (or -o). Exit codes: 0 ok, 1 nothing extracted (the message
says what to try next).
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com", "tiktok.com", "instagram.com",
               "facebook.com", "fb.watch", "dailymotion.com")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".bmp", ".tif", ".tiff"}
DEFAULT_MAX_CHARS = 60000


class FetchError(RuntimeError):
    pass


# --- helpers ----------------------------------------------------------------

def http_get(url):
    """Return (bytes, content_type, charset)."""
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return (response.read(), response.headers.get_content_type(),
                    response.headers.get_content_charset())
    except urllib.error.HTTPError as exc:
        raise FetchError(
            f"HTTP {exc.code} from {url}. The site may block scripts: fetch the page with "
            "your host's web/browser tool, or ask the user to paste the recipe."
        ) from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"could not reach {url}: {exc.reason}") from exc


def iso_duration(value):
    """'PT1H20M' -> '1 h 20 min'; anything unparseable is returned unchanged."""
    if not isinstance(value, str):
        return value
    match = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?",
                         value.strip())
    if not match or not any(match.groups()):
        return value
    days, hours, minutes, seconds = match.groups()
    hours = int(hours or 0) + 24 * int(days or 0)
    parts = []
    if hours:
        parts.append(f"{hours} h")
    if minutes and int(minutes):
        parts.append(f"{int(minutes)} min")
    if seconds and float(seconds) and not parts:
        parts.append(f"{float(seconds):g} s")
    return " ".join(parts) or None


def clean_inline(text):
    """Strip HTML tags and entities from a JSON-LD string."""
    text = re.sub(r"<br\s*/?>", "\n", str(text), flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[ \t]+", " ", html.unescape(text)).strip()


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def stamp(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def truncate(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[... truncated at {max_chars} characters; rerun with --max-chars]"


# --- HTML: schema.org Recipe ------------------------------------------------

def find_recipes(data):
    if isinstance(data, list):
        for item in data:
            yield from find_recipes(item)
    elif isinstance(data, dict):
        types = as_list(data.get("@type"))
        if any(str(t).split("/")[-1] == "Recipe" for t in types):
            yield data
            return
        for value in data.values():
            if isinstance(value, (dict, list)):
                yield from find_recipes(value)


def json_ld_recipes(page):
    recipes = []
    for block in re.findall(
            r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", page, flags=re.S | re.I):
        try:
            recipes.extend(find_recipes(json.loads(block.strip())))
        except json.JSONDecodeError:
            continue
    return recipes


def format_instructions(items, lines, depth=0):
    """Flatten strings, HowToStep, HowToSection and ItemList into numbered lines."""
    number = 0
    for item in as_list(items):
        if isinstance(item, str):
            for part in filter(None, (p.strip() for p in clean_inline(item).split("\n"))):
                number += 1
                lines.append(f"{'   ' * depth}{number}. {part}")
        elif isinstance(item, dict):
            children = item.get("itemListElement")
            if children:
                if item.get("name"):
                    lines.append(f"{'   ' * depth}**{clean_inline(item['name'])}**")
                format_instructions(children, lines, depth)
            else:
                text = item.get("text") or item.get("name")
                if text:
                    number += 1
                    lines.append(f"{'   ' * depth}{number}. {clean_inline(text)}")


def format_recipe(recipe):
    lines = [f"## Recipe (schema.org data): {clean_inline(recipe.get('name', 'Untitled'))}", ""]
    authors = [a.get("name") if isinstance(a, dict) else a for a in as_list(recipe.get("author"))]
    yields = []
    for y in as_list(recipe.get("recipeYield")):
        if str(y) not in yields:
            yields.append(str(y))
    fields = [
        ("Author", ", ".join(clean_inline(a) for a in authors if a)),
        ("Yield", " / ".join(yields)),
        ("Prep time", iso_duration(recipe.get("prepTime"))),
        ("Cook time", iso_duration(recipe.get("cookTime"))),
        ("Total time", iso_duration(recipe.get("totalTime"))),
    ]
    lines += [f"- {label}: {value}" for label, value in fields if value]
    if recipe.get("description"):
        lines += ["", clean_inline(recipe["description"])]
    lines += ["", "### Ingredients", ""]
    lines += [f"- {clean_inline(i)}" for i in as_list(recipe.get("recipeIngredient"))]
    lines += ["", "### Instructions", ""]
    format_instructions(recipe.get("recipeInstructions"), lines)
    return "\n".join(lines)


# --- HTML: readable text fallback -------------------------------------------

class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "form", "iframe", "template"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
             "section", "article", "header", "ul", "ol", "table", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skipping += 1
        elif tag in self.BLOCK:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skipping:
            self.skipping -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.split("\n")]
        out = []
        for line in lines:
            if line in ("", "-"):
                if out and out[-1] != "":
                    out.append("")
            else:
                out.append(line)
        return "\n".join(out).strip()


def page_text(page):
    extractor = TextExtractor()
    extractor.feed(page)
    return extractor.text()


def page_title(page):
    match = re.search(r"<title[^>]*>(.*?)</title>", page, flags=re.S | re.I)
    return clean_inline(match.group(1)) if match else None


def extract_html(page, origin, full_text, max_chars):
    title = page_title(page) or origin
    recipes = json_ld_recipes(page)
    out = [f"# SOURCE: {title}", f"- origin: {origin}"]
    if recipes:
        out.append(f"- kind: web page with {len(recipes)} schema.org Recipe object(s)")
        out += ["", *("\n\n".join(format_recipe(r) for r in recipes).split("\n"))]
        if full_text:
            out += ["", "## Page text", "", truncate(page_text(page), max_chars)]
    else:
        out += ["- kind: web page (no schema.org Recipe data; readable text below)", "",
                "## Page text", "", truncate(page_text(page), max_chars)]
    return "\n".join(out)


# --- video ------------------------------------------------------------------

def is_video_url(url):
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in VIDEO_HOSTS)


def pick_caption_track(info):
    """Return (lang, is_auto) for the best caption track, or (None, None)."""
    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat"}
    auto = info.get("automatic_captions") or {}
    original = (info.get("language") or "").split("-")[0]
    preferred = [original, "en"] if original else ["en"]
    for lang in preferred:
        for key in manual:
            if key == lang or key.startswith(lang + "-"):
                return key, False
    if manual:
        return next(iter(manual)), False
    for lang in preferred:
        for key in (f"{lang}-orig", lang):
            if key in auto:
                return key, True
    return None, None


def vtt_to_text(vtt):
    """Collapse WebVTT (incl. YouTube rolling auto-captions) into timestamped paragraphs."""
    out, recent, last_mark = [], [], -60.0
    start = 0.0
    for line in vtt.splitlines():
        timing = re.match(r"(\d+):(\d\d):(\d\d)\.\d+\s+-->|(\d\d):(\d\d)\.\d+\s+-->", line)
        if timing:
            g = timing.groups()
            start = (int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2])) if g[0] else int(g[3]) * 60 + int(g[4])
            continue
        if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in line:
            continue
        if line.strip().isdigit():
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
        if not text or text in recent:
            continue
        recent = (recent + [text])[-3:]
        if start - last_mark >= 30:
            out.append(f"\n[{stamp(start)}] ")
            last_mark = start
        out.append(text + " ")
    return "".join(out).strip()


def extract_video(url, max_chars):
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        raise FetchError(
            "yt-dlp is not installed (pip install yt-dlp, or brew install yt-dlp). "
            "Without it, ask the user for the video's description or transcript."
        )
    try:
        result = subprocess.run([ytdlp, "--dump-single-json", "--skip-download", "--no-playlist", url],
                                capture_output=True, text=True, timeout=120, check=True)
    except subprocess.CalledProcessError as exc:
        raise FetchError(f"yt-dlp could not read the video: {exc.stderr.strip()[-400:]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise FetchError("yt-dlp timed out reading the video") from exc
    info = json.loads(result.stdout)

    out = [f"# SOURCE: {info.get('title', url)}", f"- origin: {info.get('webpage_url', url)}",
           f"- kind: video ({info.get('extractor_key', 'unknown')})"]
    if info.get("uploader") or info.get("channel"):
        out.append(f"- channel: {info.get('channel') or info.get('uploader')}")
    if info.get("duration"):
        out.append(f"- duration: {stamp(info['duration'])}")
    out += ["", "## Description", "", (info.get("description") or "(empty)").strip()]
    if info.get("chapters"):
        out += ["", "## Chapters", ""]
        out += [f"- [{stamp(c.get('start_time', 0))}] {c.get('title', '')}" for c in info["chapters"]]

    lang, is_auto = pick_caption_track(info)
    if not lang:
        out += ["", "## Transcript", "", "(no captions available)"]
        return "\n".join(out)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [ytdlp, "--skip-download", "--no-playlist", "--sub-format", "vtt", "--sub-langs", lang,
               "--write-auto-subs" if is_auto else "--write-subs",
               "-o", str(Path(tmp) / "captions.%(ext)s"), url]
        subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        files = sorted(Path(tmp).glob("*.vtt"))
        transcript = vtt_to_text(files[0].read_text(encoding="utf-8", errors="replace")) if files else ""
    label = "auto-generated captions" if is_auto else "captions"
    out += ["", f"## Transcript ({label}, {lang})", "", truncate(transcript or "(captions empty)", max_chars)]
    return "\n".join(out)


# --- local files ------------------------------------------------------------

def extract_pdf(path, max_chars):
    tool = shutil.which("pdftotext")
    if not tool:
        raise FetchError("pdftotext is not installed (poppler). Open the PDF with your file "
                         "reader instead; it can read PDFs directly.")
    result = subprocess.run([tool, "-layout", str(path), "-"], capture_output=True,
                            text=True, timeout=120)
    text = result.stdout.strip()
    if len(text) < 40:
        raise FetchError("the PDF has no text layer (likely a scan or photo). View its pages as "
                         "images to read the recipe.")
    return f"# SOURCE: {path.name}\n- kind: pdf\n\n{truncate(text, max_chars)}"


def extract_docx(path, max_chars):
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
    paragraphs = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", para, flags=re.S))
        paragraphs.append(html.unescape(text))
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(paragraphs)).strip()
    return f"# SOURCE: {path.name}\n- kind: docx\n\n{truncate(text, max_chars)}"


def extract_with_pandoc(path, max_chars):
    tool = shutil.which("pandoc")
    if not tool:
        raise FetchError(f"no extractor for '{path.suffix}' files and pandoc is not installed. "
                         "Ask the user for a PDF, DOCX or plain-text copy.")
    result = subprocess.run([tool, str(path), "-t", "plain", "--wrap=none"],
                            capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise FetchError(f"pandoc could not read {path.name}: {result.stderr.strip()[-300:]}")
    return f"# SOURCE: {path.name}\n- kind: {path.suffix.lstrip('.')} (via pandoc)\n\n" \
           f"{truncate(result.stdout.strip(), max_chars)}"


def extract_file(path, full_text, max_chars):
    if not path.exists():
        raise FetchError(f"file not found: {path}")
    suffix = path.suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        raise FetchError(f"{path.name} is an image: view it directly to read the recipe.")
    if suffix == ".pdf":
        return extract_pdf(path, max_chars)
    if suffix == ".docx":
        return extract_docx(path, max_chars)
    if suffix in (".html", ".htm"):
        return extract_html(path.read_text(encoding="utf-8", errors="replace"), str(path),
                            full_text, max_chars)
    if suffix in (".txt", ".md", ".markdown", ".text", ""):
        return f"# SOURCE: {path.name}\n- kind: text\n\n" \
               f"{truncate(path.read_text(encoding='utf-8', errors='replace'), max_chars)}"
    return extract_with_pandoc(path, max_chars)


def extract_url(url, full_text, max_chars):
    if is_video_url(url):
        return extract_video(url, max_chars)
    body, content_type, charset = http_get(url)
    if content_type == "application/pdf" or url.lower().endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "download.pdf"
            pdf.write_bytes(body)
            return extract_pdf(pdf, max_chars).replace("# SOURCE: download.pdf", f"# SOURCE: {url}", 1)
    if content_type.startswith("image/"):
        raise FetchError(f"{url} is an image: download it and view it directly.")
    page = body.decode(charset or "utf-8", errors="replace")
    return extract_html(page, url, full_text, max_chars)


# --- CLI --------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", help="URL or local file path")
    parser.add_argument("-o", "--out", type=Path, help="write Markdown here instead of stdout")
    parser.add_argument("--full-text", action="store_true",
                        help="append the page text even when schema.org data was found")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                        help=f"truncate long text sections (default {DEFAULT_MAX_CHARS})")
    args = parser.parse_args(argv)

    try:
        if re.match(r"https?://", args.source, flags=re.I):
            document = extract_url(args.source, args.full_text, args.max_chars)
        else:
            document = extract_file(Path(args.source).expanduser(), args.full_text, args.max_chars)
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(document + "\n", encoding="utf-8")
        print(f"wrote {args.out} ({len(document)} chars)")
    else:
        print(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
