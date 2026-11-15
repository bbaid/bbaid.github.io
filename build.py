#!/usr/bin/env python3
"""Build the site from the markdown in content/.

    python3 build.py          write the pages for every language
    python3 build.py --pdf    also export each CV to PDF (needs Chrome or Chromium)
    python3 build.py --check  build nothing; say whether the pages are up to date

content/en.md is the master: it holds the English text and names the images,
links and categories. Every other language file (content/bg.md) only carries
text, matched to the master by {#id}; whatever it leaves out falls back to
English. The pages of the atlas book live in templates/atlas-book.html.

No third-party packages are needed.
"""
from __future__ import annotations

import copy
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
MASTER = "en"
# Languages in the order they appear in the toggle: (file stem, folder on the site).
LANGUAGES = [("en", ""), ("bg", "bg/")]

# Keys that hold data, not text. They live in the master file; a translation
# may override one (the Bulgarian CV has its own PDF), but need not repeat it.
DATA_KEYS = {
    "url", "email", "linkedin", "github", "image", "image-top", "cat", "wide",
    "more-image", "map", "source", "repo", "team", "upcoming", "pdf", "compact",
}
# Text that is usually the same in every language; left out of the progress count.
SAME_ANYWAY = {"tags", "tools", "second-name", "figure-label", "label-linkedin", "label-github", "coordinates"}

FONTS = ("https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500&family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&display=swap")
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%231c2219'/%3E"
        "%3Cpath d='M10 44c8-14 14-4 22-14s12-12 22-10' fill='none' stroke='%239fd0a8' stroke-width='4' stroke-linecap='round'/%3E"
        "%3Cpath d='M10 54c8-12 16-4 24-12s12-10 20-8' fill='none' stroke='%239fd0a8' stroke-width='4' stroke-linecap='round' opacity='.55'/%3E"
        "%3Ccircle cx='44' cy='20' r='5' fill='%23e08a63'/%3E%3C/svg%3E")


class BuildError(Exception):
    pass


# ───────────────────────── Reading the markdown ─────────────────────────

class Node:
    """One heading and what sits under it."""

    def __init__(self, ident: str, title: str, level: int):
        self.id, self.title, self.level = ident, title, level
        self.paras: list[str] = []      # body paragraphs, in order
        self.items: list[str] = []      # list entries that are not `key`: value
        self.fields: dict[str, str] = {}
        self.children: list[Node] = []

    def get(self, key: str, default: str | None = None) -> str:
        if key in self.fields:
            return self.fields[key]
        if default is None:
            raise BuildError(f"{{#{self.id}}} has no `{key}`")
        return default

    def has(self, key: str) -> bool:
        return bool(self.fields.get(key, "").strip())

    def child(self, ident: str) -> "Node":
        for c in self.children:
            if c.id == ident:
                return c
        raise BuildError(f"{{#{self.id}}} has no section {{#{ident}}}")

    def para(self, i: int) -> str:
        if i >= len(self.paras):
            raise BuildError(f"{{#{self.id}}} needs at least {i + 1} paragraph(s)")
        return self.paras[i]

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


class Doc:
    def __init__(self, path: Path):
        self.path = path
        self.meta: dict[str, str] = {}
        self.top = Node("", "", 0)
        self.nodes: dict[str, Node] = {}
        self._parse(path.read_text(encoding="utf-8"))

    def _parse(self, text: str) -> None:
        text = text.replace("\r\n", "\n")
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if front:
            for line in front.group(1).splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    self.meta[key.strip()] = value.strip()
            text = text[front.end():]
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

        stack = [self.top]
        para: list[str] = []
        item: list[str] | None = None

        def end_para():
            if para:
                stack[-1].paras.append(" ".join(para))
                para.clear()

        def end_item():
            nonlocal item
            if item is None:
                return
            entry = " ".join(item).strip()
            field = re.match(r"`([a-z0-9-]+)`:\s*(.*)\Z", entry, re.S)
            if field:
                stack[-1].fields[field.group(1)] = field.group(2).strip()
            elif entry:
                stack[-1].items.append(entry)
            item = None

        for number, line in enumerate(text.split("\n"), 1):
            heading = re.match(r"(#{1,6})\s+(.*?)\s*\Z", line)
            bullet = re.match(r"\s*(?:[-*+]|\d+[.)])\s+(.*)\Z", line)
            if heading:
                end_para(); end_item()
                with_id = re.match(r"(.*?)\s*\{#([\w-]+)\}\Z", heading.group(2))
                if not with_id:
                    raise BuildError(f"{self.path.name}: the heading “{heading.group(2)}” needs an id, like {{#name}}")
                level = len(heading.group(1))
                node = Node(with_id.group(2), with_id.group(1).strip(), level)
                if node.id in self.nodes:
                    raise BuildError(f"{self.path.name}: the id {{#{node.id}}} is used twice")
                while stack[-1].level >= level:
                    stack.pop()
                stack[-1].children.append(node)
                stack.append(node)
                self.nodes[node.id] = node
            elif bullet:
                end_para(); end_item()
                item = [bullet.group(1)]
            elif not line.strip():
                end_para(); end_item()
            elif item is not None and line.startswith((" ", "\t")):
                item.append(line.strip())
            else:
                end_item()
                para.append(line.strip())
        end_para(); end_item()


def texts_of(node: Node):
    """Every translatable string of a node, with a label for messages."""
    if node.title:
        yield "title", node.title
    for i, p in enumerate(node.paras):
        yield f"paragraph {i + 1}", p
    for i, entry in enumerate(node.items):
        yield f"list entry {i + 1}", entry
    for key, value in node.fields.items():
        if key not in DATA_KEYS and key not in SAME_ANYWAY:
            yield f"`{key}`", value


def overlay(master: Doc, translation: Doc) -> tuple[Doc, list[str], tuple[int, int]]:
    """Lay a translation over the master. Returns the merged document, any
    warnings, and (texts translated, texts in all)."""
    merged = copy.deepcopy(master)
    merged.meta = {**master.meta, **translation.meta}
    warnings = []
    for ident in translation.nodes:
        if ident not in master.nodes:
            warnings.append(f"{{#{ident}}} is not in {master.path.name}, so it is ignored")
    done = total = 0
    for node in merged.top.walk():
        other = translation.nodes.get(node.id)
        base = dict(texts_of(node))
        total += len(base)
        if other is None:
            continue
        theirs = dict(texts_of(other))
        done += sum(1 for label, text in theirs.items() if label in base and text != base[label])
        if other.paras and len(other.paras) != len(node.paras):
            warnings.append(f"{{#{node.id}}} has {len(other.paras)} paragraph(s), the master has {len(node.paras)}")
        if other.items and len(other.items) != len(node.items):
            warnings.append(f"{{#{node.id}}} has {len(other.items)} list entries, the master has {len(node.items)}")
        node.title = other.title or node.title
        node.paras = other.paras or node.paras
        node.items = other.items or node.items
        node.fields.update(other.fields)
    return merged, warnings, (done, total)


# ───────────────────────── Text to HTML ─────────────────────────

_AMP = re.compile(r"&(?!(?:[a-zA-Z]+|#\d+);)")


def esc(text: str) -> str:
    """Escape for HTML, but let entities such as &nbsp; through."""
    return _AMP.sub("&amp;", text).replace("<", "&lt;").replace(">", "&gt;")


def plain(text: str) -> str:
    """Drop the markdown marks: for attributes and titles."""
    text = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\1", text)
    return re.sub(r"`([^`]+)`", r"\1", text)


def attr(text: str) -> str:
    return esc(plain(text)).replace('"', "&quot;")


def md(text: str) -> str:
    """Inline markdown: **bold**, *italic*, `code`, [text](link)."""
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)


def lead(entry: str) -> tuple[str, str]:
    """Split “**Label** the rest” into its two parts."""
    m = re.match(r"\*\*(.+?)\*\*\s*(.*)\Z", entry, re.S)
    if not m:
        raise BuildError(f"this list entry should start with a **label**: “{entry[:60]}”")
    return m.group(1), m.group(2)


def tags(value: str) -> str:
    return "".join(f"<li>{esc(t.strip())}</li>" for t in value.split(",") if t.strip())


# ───────────────────────── Images ─────────────────────────

def image_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            b = data[21:25]
            return 1 + (b[0] | (b[1] & 0x3F) << 8), 1 + (b[1] >> 6 | b[2] << 2 | (b[3] & 0x0F) << 10)
        if kind == b"VP8X":
            return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            marker, size = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + size
    raise BuildError(f"cannot read the size of {path.relative_to(ROOT)}")


def picture(slug: str, alt: str, root: str, small: bool = True, extra: str = ' loading="lazy"') -> str:
    name = f"assets/img/{slug}{'-sm' if small else ''}.webp"
    if not (ROOT / name).exists():
        raise BuildError(f"image not found: {name}")
    w, h = image_size(ROOT / name)
    return f'<img src="{root}{name}" width="{w}" height="{h}"{extra} alt="{attr(alt)}">'


def viewer(group: str, slug: str, caption: str, root: str) -> str:
    """Attributes that open an image in the full-size viewer."""
    if not (ROOT / f"assets/img/{slug}.webp").exists():
        raise BuildError(f"image not found: assets/img/{slug}.webp")
    return f'data-lightbox data-group="{group}" data-full="{root}assets/img/{slug}.webp" data-caption="{attr(caption)}"'


# ───────────────────────── Pages and languages ─────────────────────────

class Lang:
    def __init__(self, stem: str, folder: str, doc: Doc):
        self.stem, self.folder, self.doc = stem, folder, doc
        self.code = doc.meta.get("code", stem)
        self.label = doc.meta.get("label", stem.upper())
        self.name = doc.meta.get("name", self.label)


class Page:
    """Where a page sits, so links between pages and to assets come out right."""

    def __init__(self, lang: Lang, langs: list[Lang], sub: str = ""):
        self.lang, self.langs, self.sub = lang, langs, sub
        self.path = lang.folder + sub                     # e.g. "bg/cv/"
        self.root = "../" * self.path.count("/")          # back to the site root
        self.home = (self.root + lang.folder) or "./"     # this language's front page

    def to(self, other: Lang) -> str:
        """The same page in another language."""
        return (self.root + other.folder + self.sub) or "./"

    def url(self, other: Lang | None = None) -> str:
        lang = other or self.lang
        return lang.doc.nodes["site"].get("url") + lang.folder + self.sub

    def alternates(self) -> str:
        return "\n".join(f'<link rel="alternate" hreflang="{l.code}" href="{self.url(l)}">' for l in self.langs)


# ───────────────────────── The portfolio page ─────────────────────────

CONTOURS = """  <svg class="hero-contours" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <g fill="none" stroke="currentColor" stroke-width="1">
      <path d="M-20 560C120 500 210 600 360 540S590 420 760 470s250 60 470-30"/>
      <path d="M-20 500C130 440 220 540 370 480S600 360 770 410s250 60 460-30"/>
      <path d="M-20 440C140 380 230 480 380 420S610 300 780 350s250 60 450-30"/>
      <path d="M-20 380C150 320 240 420 390 360S620 240 790 290s250 60 440-30"/>
      <path d="M-20 320C160 260 250 360 400 300S630 180 800 230s250 60 430-30"/>
      <path d="M-20 260C170 200 260 300 410 240S640 120 810 170s250 60 420-30"/>
      <path d="M-20 200C180 140 270 240 420 180S650 60 820 110s250 60 410-30"/>
      <path d="M-20 140C190 80 280 180 430 120S660 0 830 50s250 60 400-30"/>
      <path d="M-20 620C110 560 200 660 350 600S580 480 750 530s250 60 480-30"/>
    </g>
  </svg>"""

RELIEF = """  <svg class="club-relief" viewBox="0 0 760 760" aria-hidden="true">
    <defs><clipPath id="reliefClip"><circle cx="380" cy="380" r="380"/></clipPath></defs>
    <g clip-path="url(#reliefClip)" fill="none" stroke-linecap="butt">
""" + "\n".join(
    f'      <path d="M-40 {y}C120 {y - 60} 260 {y + 50} 420 {y - 10}s260-80 400-10" stroke-width="54"/>'
    for y in (120, 200, 280, 360, 440, 520, 600, 680, 40)) + """
    </g>
  </svg>"""

ARROW_PREV = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4l-8 8 8 8"/></svg>'
ARROW_NEXT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4l8 8-8 8"/></svg>'


def site_head(page: Page, d: Doc) -> str:
    site = d.nodes["site"]
    og = site.get("url") + "assets/img/og-cover.jpg"
    return f"""<!doctype html>
<html lang="{page.lang.code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by build.py from content/{page.lang.stem}.md. Edit that file, then run: python3 build.py -->
<title>{esc(plain(site.get('title')))}</title>
<meta name="description" content="{attr(site.get('description'))}">
<meta name="author" content="{attr(site.get('name'))}">
<link rel="canonical" href="{page.url()}">
{page.alternates()}
<meta property="og:type" content="website">
<meta property="og:url" content="{page.url()}">
<meta property="og:title" content="{attr(site.get('title'))}">
<meta property="og:description" content="{attr(site.get('share-description'))}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f4f2ea" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141a15" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{ICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{page.root}assets/css/style.css">
<script>
/* Apply a saved theme before first paint. */
try {{ var t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }} catch (e) {{}}
</script>
</head>"""


def language_toggle(page: Page, label: str) -> str:
    if len(page.langs) < 2:
        return ""
    links = "".join(
        f'<a href="{page.to(l)}" lang="{l.code}" hreflang="{l.code}"' + (' aria-current="true"' if l is page.lang else "") + f">{esc(l.label)}</a>"
        for l in page.langs)
    return f'\n    <div class="lang" role="group" aria-label="{attr(label)}" data-lang-toggle>{links}</div>'


def site_header(page: Page, d: Doc, sections: list[Node]) -> str:
    ui, site = d.nodes["ui"], d.nodes["site"]
    nav = "\n".join(f'      <a href="#{s.id}">{esc(s.get("nav"))}</a>' for s in sections)
    return f"""<a class="skip" href="#main">{esc(ui.get('skip'))}</a>

<header class="site-header" id="top">
  <div class="wrap header-row">
    <a class="brand" href="#top" aria-label="{attr(ui.get('home'))}">
      <svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M3 22c5-8 8-2 13-8s7-7 13-6" /><path d="M3 28c5-7 9-2 14-7s7-6 12-5" /><circle cx="23" cy="9" r="2.6" /></svg>
      <span class="brand-name">{esc(site.get('name'))}</span>
    </a>
    <nav class="nav" aria-label="{attr(ui.get('sections'))}">
{nav}
    </nav>{language_toggle(page, ui.get('language'))}
    <button class="theme-toggle" type="button" id="themeToggle" aria-label="{attr(ui.get('theme'))}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" /><path d="M12 3.5v17a8.5 8.5 0 0 0 0-17z" class="half" /></svg>
    </button>
  </div>
</header>"""


def hero(page: Page, d: Doc) -> str:
    h, r = d.nodes["hero"], page.root
    # Share a viewer group with the project card that shows the same map.
    group = next((c.id for c in d.nodes["projects"].children if c.get("image", "") == h.get("image")), "hero")
    facts = "\n".join(
        "      <div><dt>{}</dt><dd>{}</dd></div>".format(esc(n), md(t)) for n, t in map(lead, h.child("facts").items))
    return f"""<section class="hero">
{CONTOURS}
  <div class="wrap hero-grid">
    <div class="hero-text">
      <p class="eyebrow"><span class="dot"></span>{esc(h.get('eyebrow'))}</p>
      <h1>{esc(h.title)}</h1>
      <p class="hero-lead">{md(h.para(0))}</p>
      <p class="hero-sub">{md(h.para(1))}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="#work">{esc(h.get('button-work'))}</a>
        <a class="btn" href="#club">{esc(h.get('button-club'))}</a>
        <a class="btn btn-ghost" href="cv/">{esc(h.get('button-cv'))}</a>
      </div>
    </div>
    <figure class="hero-map">
      <button class="frame" type="button" {viewer(group, h.get('image'), h.get('caption'), r)}>
        {picture(h.get('image'), h.get('image-alt'), r, extra=' fetchpriority="high"')}
        <span class="tick tl"></span><span class="tick tr"></span><span class="tick bl"></span><span class="tick br"></span>
      </button>
      <figcaption><span class="mono">{esc(h.get('figure-label'))}</span> {md(h.get('figure-caption'))}</figcaption>
    </figure>
  </div>

  <div class="wrap">
    <dl class="facts">
{facts}
    </dl>
  </div>
</section>"""


def section_head(node: Node, number: int, extra: str = "") -> str:
    lead_text = f'\n      <p class="section-lead">{md(node.paras[0])}</p>' if node.paras else ""
    return f"""    <header class="section-head">
      <p class="eyebrow"><span class="mono">{number:02d}</span> {esc(node.get('eyebrow'))}</p>
      <h2>{esc(node.title)}{extra}</h2>{lead_text}
    </header>"""


def mini_facts(node: Node, indent: str) -> str:
    if not node.items:
        return ""
    rows = "\n".join(f"{indent}  <div><dt>{esc(n)}</dt><dd>{md(t)}</dd></div>" for n, t in map(lead, node.items))
    return f'{indent}<dl class="mini-facts">\n{rows}\n{indent}</dl>\n'


def atlas(page: Page, d: Doc) -> str:
    a, r = d.nodes["atlas"], page.root
    book = (ROOT / "templates/atlas-book.html").read_text(encoding="utf-8").rstrip("\n")
    book = book.replace("{{root}}", r).replace("{{label}}", attr(a.get("book-label")))
    body = "\n".join(f"          <p>{md(p)}</p>" for p in a.paras)
    return f"""    <!-- Featured: V4+2 atlas, as a book with turning pages -->
    <article class="feature reveal" id="atlas">
      <div class="feature-head">
        <div class="feature-body">
          <p class="kicker">{esc(a.get('kicker'))}</p>
          <h3>{esc(a.title)}</h3>
{body}
        </div>
        <div class="feature-aside">
{mini_facts(a, '          ')}          <p class="method">{md(a.get('method'))}</p>
          <ul class="tags">{tags(a.get('tags'))}</ul>
        </div>
      </div>

      <div class="book-wrap">
{book}

        <div class="book-bar">
          <button type="button" class="book-btn" data-book-prev aria-label="{attr(a.get('book-previous'))}" aria-controls="atlasBook">
            {ARROW_PREV}
          </button>
          <p class="book-label" data-book-label aria-live="polite">{esc(a.get('book-first'))}</p>
          <button type="button" class="book-btn" data-book-next aria-label="{attr(a.get('book-next'))}" aria-controls="atlasBook">
            {ARROW_NEXT}
          </button>
        </div>
        <p class="book-actions">
          <button type="button" class="more" data-book-zoom>{esc(a.get('book-zoom'))}</button>
          <button type="button" class="more" {viewer('v4-overview', 'v4-atlas-overview', a.get('book-overview-caption'), r)}>{esc(a.get('book-overview'))}</button>
        </p>
        <p class="book-hint">{esc(a.get('book-hint'))}</p>
      </div>
    </article>"""


def card(page: Page, c: Node, view_label: str) -> str:
    r = page.root
    classes = "card" + (" card-wide" if c.has("wide") else "") + " reveal"
    media = "card-media" + (" media-top" if c.has("image-top") else "")
    parts = [f'          <p class="kicker">{esc(c.get("kicker"))}</p>', f"          <h3>{esc(c.title)}</h3>"]
    parts += [f"          <p>{md(p)}</p>" for p in c.paras]
    extra = mini_facts(c, "          ").rstrip("\n")
    if extra:
        parts.append(extra)
    if c.has("tags"):
        parts.append(f'          <ul class="tags">{tags(c.get("tags"))}</ul>')
    if c.has("more"):
        parts.append(f'          <button class="more" type="button" {viewer(c.id, c.get("more-image"), c.get("more-caption"), r)}>{esc(c.get("more"))}</button>')
    return f"""      <article class="{classes}" data-cat="{attr(c.get('cat'))}">
        <button class="{media}" type="button" data-label="{attr(view_label)}" {viewer(c.id, c.get('image'), c.get('caption'), r)}>
          {picture(c.get('image'), c.get('image-alt'), r)}
        </button>
        <div class="card-body">
{chr(10).join(parts)}
        </div>
      </article>"""


def work(page: Page, d: Doc, number: int) -> str:
    w, ui, r = d.nodes["work"], d.nodes["ui"], page.root
    f = w.child("filters")
    chips = [("all", True)] + [(k, False) for k in ("nature", "climate", "terrain", "people")]
    filters = "\n".join(
        f'      <button type="button" class="chip{" is-active" if on else ""}" data-filter="{k}" aria-pressed="{"true" if on else "false"}">{esc(f.get(k))}</button>'
        for k, on in chips)
    cards = "\n\n".join(card(page, c, ui.get("view-map")) for c in w.child("projects").children)
    e = w.child("earlier")
    tiles = "\n".join(f"""        <button class="tile" type="button" {viewer('earlier', t.get('image'), t.get('caption'), r)}>
          {picture(t.get('image'), t.get('image-alt'), r)}
          <span><b>{esc(t.title)}</b>{esc(t.get('note'))}</span>
        </button>""" for t in e.children)
    return f"""<section class="section" id="work">
  <div class="wrap">
{section_head(w, number)}

{atlas(page, d)}

    <div class="filters" role="group" aria-label="{attr(ui.get('filter'))}">
{filters}
    </div>

    <div class="grid" id="projectGrid">

{cards}

    </div>

    <!-- Earlier work -->
    <div class="earlier reveal">
      <h3 class="sub-head">{esc(e.title)} <span class="mono">{esc(e.get('period'))}</span></h3>
      <div class="strip">
{tiles}
      </div>
    </div>
  </div>
</section>"""


def club(page: Page, d: Doc, number: int) -> str:
    c, r = d.nodes["club"], page.root
    story, goals, how, post = c.child("club-story"), c.child("club-goals"), c.child("club-how"), c.child("club-post")
    second = f' <span class="cyr">{esc(c.get("second-name"))}</span>' if c.has("second-name") and c.get("second-name") != c.title else ""
    paragraphs = "\n".join(f"        <p>{md(p)}</p>" for p in story.paras)
    goal_list = "\n".join(f"          <li>{md(g)}</li>" for g in goals.items)
    timeline = "\n".join(f"""          <li{' class="next"' if t.has('upcoming') else ''}>
            <p class="when">{esc(t.get('when'))}</p>
            <p class="what">{esc(t.title)}</p>
            <p class="where">{md(t.get('detail'))}</p>
          </li>""" for t in c.child("club-timeline").children)
    emblem = picture("club-emblem", post.get("emblem-alt"), r).replace("<img ", '<img class="emblem" ')
    return f"""<section class="club" id="club">
{RELIEF}
  <div class="wrap club-wrap">
{section_head(c, number, second)}

    <div class="club-grid">
      <div class="club-story reveal">
{paragraphs}

        <h3 class="club-sub">{esc(goals.title)}</h3>
        <ul class="club-goals">
{goal_list}
        </ul>

        <h3 class="club-sub">{esc(how.title)}</h3>
        <p class="club-how">{md(how.para(0))}</p>

        <p class="club-note">{md(story.get('note'))}</p>
      </div>

      <aside class="club-side reveal">
        <ol class="timeline">
{timeline}
        </ol>
        <figure class="club-post">
          <button class="shot" type="button" {viewer('club', post.get('image'), post.get('caption'), r)}>
            {picture(post.get('image'), post.get('image-alt'), r)}
          </button>
          <figcaption>
            {emblem}
            <span>{md(post.get('note'))}</span>
          </figcaption>
        </figure>
      </aside>
    </div>
  </div>
</section>"""


def tutoring(page: Page, d: Doc, number: int) -> str:
    t, site = d.nodes["tutoring"], d.nodes["site"]
    steps, topics = t.child("tutoring-steps"), t.child("tutoring-topics")
    step_rows = "\n".join(f"          <li><p>{md(i)}</p></li>" for i in steps.items)
    topic_rows = "\n".join(f"""        <article class="topic">
          <h4>{esc(n.title)}</h4>
          <p>{md(n.para(0))}</p>
          <p class="topic-tools mono">{esc(n.get('tools'))}</p>
        </article>""" for n in topics.children)
    mail = f"mailto:{site.get('email')}?subject={quote(plain(t.get('subject')))}"
    return f"""<section class="section tutoring" id="tutoring">
  <div class="wrap">
{section_head(t, number)}

    <div class="tutor-grid">
      <div class="reveal">
        <h3 class="sub-head">{esc(steps.title)}</h3>
        <ol class="steps">
{step_rows}
        </ol>
      </div>

      <aside class="tutor-card reveal">
        <h3 class="sub-head">{esc(t.get('note-title'))}</h3>
        <p>{md(t.get('note'))}</p>
        <a class="btn btn-primary" href="{attr(mail)}">{esc(t.get('button'))}</a>
      </aside>
    </div>

    <div class="topics-block reveal">
      <h3 class="sub-head">{esc(topics.title)}</h3>
      <div class="topics">
{topic_rows}
      </div>
    </div>
  </div>
</section>"""


def code(page: Page, d: Doc, number: int) -> str:
    c = d.nodes["code"]

    def repo(n: Node) -> str:
        badge = f' <span class="badge">{esc(c.get("label-team"))}</span>' if n.has("team") else ""
        links = (f'<a href="{attr(n.get("map"))}">{esc(c.get("label-map"))}</a>' if n.has("map") else "") + \
                f'<a href="{attr(n.get("source"))}">{esc(c.get("label-code"))}</a>'
        body = "\n".join(f"        <p>{md(p)}</p>" for p in n.paras)
        return f"""      <article class="repo reveal">
        <p class="repo-name mono">{esc(n.get('repo'))}{badge}</p>
        <h3>{esc(n.title)}</h3>
{body}
        <ul class="tags">{tags(n.get('tags'))}</ul>
        <p class="links">{links}</p>
      </article>"""

    return f"""<section class="section" id="code">
  <div class="wrap">
{section_head(c, number)}

    <div class="repos">
{(chr(10) + chr(10)).join(repo(n) for n in c.children)}
    </div>
  </div>
</section>"""


def about(page: Page, d: Doc, number: int) -> str:
    a = d.nodes["about"]
    path, box, ai = a.child("about-path"), a.child("toolbox"), a.child("ai")
    steps = "\n".join(
        f'          <li>\n            <span class="cv-when mono">{esc(when)}</span>\n            <span>{md(text)}</span>\n          </li>'
        for when, text in map(lead, path.items))
    tools = "\n".join(f"            <div><dt>{esc(k)}</dt><dd>{md(v)}</dd></div>" for k, v in map(lead, box.items))
    rules = "\n".join(f"            <li>{md(i)}</li>" for i in ai.items)
    more = "\n".join(f"        <p>{md(p)}</p>" for p in a.paras[1:])
    head = f"""    <header class="section-head">
      <p class="eyebrow"><span class="mono">{number:02d}</span> {esc(a.get('eyebrow'))}</p>
      <h2>{esc(a.title)}</h2>
    </header>"""
    return f"""<section class="section section-alt" id="about">
  <div class="wrap">
{head}

    <div class="about-grid">
      <div class="about-bio reveal">
        <p class="lead-para">{md(a.para(0))}</p>
{more}

        <h3 class="sub-head">{esc(path.title)}</h3>
        <ul class="cv">
{steps}
        </ul>
        <p class="langs">{md(a.get('languages'))}</p>
      </div>

      <div class="about-side reveal">
        <div class="toolbox">
          <h3 class="sub-head">{esc(box.title)}</h3>
          <dl>
{tools}
          </dl>
        </div>

        <div class="ai-note">
          <h3 class="sub-head">{esc(ai.title)}</h3>
          <ol>
{rules}
          </ol>
        </div>
      </div>
    </div>
  </div>
</section>"""


def contact(page: Page, d: Doc, number: int) -> str:
    c, site, cv = d.nodes["contact"], d.nodes["site"], d.nodes["cv"]
    return f"""<section class="contact" id="contact">
  <div class="wrap contact-wrap">
    <p class="eyebrow"><span class="mono">{number:02d}</span> {esc(c.get('eyebrow'))}</p>
    <h2>{esc(c.title)}</h2>
    <p class="section-lead">{md(c.para(0))}</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="mailto:{attr(site.get('email'))}">{esc(site.get('email'))}</a>
      <a class="btn" href="{attr(site.get('linkedin'))}">{esc(c.get('label-linkedin'))}</a>
      <a class="btn" href="{attr(site.get('github'))}">{esc(c.get('label-github'))}</a>
      <a class="btn btn-ghost" href="cv/">{esc(c.get('label-cv'))}</a>
      <a class="btn btn-ghost" href="{page.root}{attr(cv.get('pdf'))}">{esc(c.get('label-cv-pdf'))}</a>
    </div>
  </div>
</section>"""


def site_page(page: Page) -> str:
    d = page.lang.doc
    ui, site = d.nodes["ui"], d.nodes["site"]
    sections = [d.nodes[i] for i in ("work", "club", "tutoring", "code", "about", "contact")]
    return f"""{site_head(page, d)}
<body>
{site_header(page, d, sections)}

<main id="main">

<!-- ───────────── Hero ───────────── -->
{hero(page, d)}

<!-- ───────────── Work ───────────── -->
{work(page, d, 1)}

<!-- ───────────── GIS Club SU ───────────── -->
{club(page, d, 2)}

<!-- ───────────── Tutoring ───────────── -->
{tutoring(page, d, 3)}

<!-- ───────────── Code ───────────── -->
{code(page, d, 4)}

<!-- ───────────── About ───────────── -->
{about(page, d, 5)}

<!-- ───────────── Contact ───────────── -->
{contact(page, d, 6)}

</main>

<footer class="site-footer">
  <div class="wrap footer-row">
    <p>{md(site.get('footer'))}</p>
    <p class="mono">{esc(site.get('coordinates'))}</p>
  </div>
</footer>

<!-- Lightbox -->
<dialog class="lightbox" id="lightbox" aria-label="{attr(ui.get('viewer'))}">
  <div class="lb-bar">
    <p class="lb-count mono" id="lbCount"></p>
    <button type="button" class="lb-btn" id="lbClose" aria-label="{attr(ui.get('viewer-close'))}">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>
    </button>
  </div>
  <div class="lb-stage">
    <button type="button" class="lb-btn lb-nav" id="lbPrev" aria-label="{attr(ui.get('viewer-previous'))}">
      {ARROW_PREV}
    </button>
    <img id="lbImg" alt="">
    <button type="button" class="lb-btn lb-nav" id="lbNext" aria-label="{attr(ui.get('viewer-next'))}">
      {ARROW_NEXT}
    </button>
  </div>
  <p class="lb-caption" id="lbCaption"></p>
</dialog>

<script src="{page.root}assets/js/main.js" defer></script>
</body>
</html>
"""


# ───────────────────────── The CV page ─────────────────────────

CV_CONTOURS = """  <svg class="contours" viewBox="0 0 794 235" preserveAspectRatio="none" aria-hidden="true">
    <g fill="none" stroke="currentColor" stroke-width="0.8">
""" + "\n".join(
    f'      <path d="M-10 {y}C90 {y - 35} 150 {y + 30} 250 {y - 5}S400 {y - 70} 510 {y - 35}s170 40 300-20"/>'
    for y in (40, 78, 116, 154, 192)) + """
    </g>
  </svg>"""


def cv_page(page: Page) -> str:
    d = page.lang.doc
    cv, site, r = d.nodes["cv"], d.nodes["site"], page.root
    count = iter(range(1, 99))

    def h2(node: Node) -> str:
        return f"<h2><span>{next(count):02d}</span> {esc(node.title)}</h2>"

    def labelled(node: Node) -> str:
        return "\n".join(f"          <li><b>{esc(k)}</b> <span>{md(v)}</span></li>" for k, v in map(lead, node.items))

    def dated(node: Node, with_role: bool) -> str:
        rows = []
        for n in node.children:
            role = f' — {md(n.get("role"))}' if with_role and n.has("role") else ""
            text = "".join(f"\n              <p>{md(p)}</p>" for p in n.paras)
            rows.append(f"          <li>\n            <time>{esc(n.get('when'))}</time>\n            <div><b>{esc(n.title)}</b>{role}{text}</div>\n          </li>")
        return "\n".join(rows)

    profile, projects, experience = (cv.child(i) for i in ("cv-profile", "cv-projects", "cv-experience"))
    education, toolbox, languages, awards, interests = (
        cv.child(i) for i in ("cv-education", "cv-toolbox", "cv-languages", "cv-awards", "cv-interests"))

    project_rows = []
    for n in projects.children:
        tools = f' <span class="tools">{esc(n.get("tools"))}</span>' if n.has("tools") else ""
        project_rows.append(
            f"          <li>\n            <h3>{esc(n.title)} <small>{esc(n.get('year'))}</small></h3>\n            <p>{md(n.para(0))}{tools}</p>\n          </li>")
    main = f"""      <section>
        {h2(profile)}
        <p class="lead">{md(profile.para(0))}</p>
      </section>

      <section>
        {h2(projects)}
        <ul class="projects">
{chr(10).join(project_rows)}
        </ul>
        <p class="more">{md(projects.get('more'))}</p>
      </section>

      <section>
        {h2(experience)}
        <ul class="entries">
{dated(experience, True)}
        </ul>
      </section>"""
    tool_rows = "\n".join(f"          <div><dt>{esc(k)}</dt><dd>{md(v)}</dd></div>" for k, v in map(lead, toolbox.items))
    side = f"""      <section>
        {h2(education)}
        <ul class="entries">
{dated(education, False)}
        </ul>
      </section>

      <section>
        {h2(toolbox)}
        <dl class="toolbox">
{tool_rows}
        </dl>
      </section>

      <section>
        {h2(languages)}
        <ul class="plain">
{labelled(languages)}
        </ul>
      </section>

      <section>
        {h2(awards)}
        <ul class="plain">
{labelled(awards)}
        </ul>
      </section>

      <section>
        {h2(interests)}
        <p>{md(interests.para(0))}</p>
      </section>"""

    others = "".join(f'\n    <a href="{page.to(l)}" lang="{l.code}" hreflang="{l.code}">{esc(l.name)}</a>' for l in page.langs if l is not page.lang)
    short = lambda url: re.sub(r"^https?://(www\.)?|/$", "", url)
    w, h = image_size(ROOT / "cv/photo.jpg")
    return f"""<!doctype html>
<html lang="{page.lang.code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Generated by build.py from content/{page.lang.stem}.md. Edit that file, then run: python3 build.py -->
<title>{esc(plain(cv.get('title')))}</title>
<meta name="description" content="{attr(cv.get('description'))}">
<meta name="author" content="{attr(cv.title)}">
<link rel="canonical" href="{page.url()}">
{page.alternates()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{r}cv/cv.css">
</head>
<body>

<nav class="bar" aria-label="{attr(cv.get('options'))}">
  <a href="{page.home}">{esc(cv.get('back'))}</a>
  <div>{others}
    <a class="primary" href="{r}{attr(cv.get('pdf'))}">{esc(cv.get('download'))}</a>
  </div>
</nav>

<main class="sheet{' sheet-compact' if cv.has('compact') else ''}">
{CV_CONTOURS}

  <header class="head">
    <div>
      <p class="eyebrow">{esc(cv.get('eyebrow'))}</p>
      <h1>{esc(cv.title)}</h1>
      <p class="role">{md(cv.get('role'))}</p>
      <p class="contact">
        <a href="mailto:{attr(site.get('email'))}">{esc(site.get('email'))}</a>
        <a href="{attr(site.get('url'))}">{esc(short(site.get('url')))}</a>
        <a href="{attr(site.get('linkedin'))}">{esc(short(site.get('linkedin')))}</a>
        <a href="{attr(site.get('github'))}">{esc(short(site.get('github')))}</a>
      </p>
    </div>
    <div class="photo"><img src="{r}cv/photo.jpg" width="{w}" height="{h}" alt="{attr(cv.get('photo-alt'))}"></div>
  </header>

  <div class="cols">
    <div class="main">
{main}
    </div>

    <aside class="side">
{side}
    </aside>
  </div>

  <footer class="foot">
    <span>{md(cv.get('footer'))}</span>
    <span>{esc(short(site.get('url')))}</span>
  </footer>
</main>

</body>
</html>
"""


def redirect(target: str) -> str:
    return f"""<!doctype html>
<html lang="bg">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<title>CV</title>
</head>
<body><p><a href="{target}">{target}</a></p></body>
</html>
"""


# ───────────────────────── PDF export ─────────────────────────

def find_browser() -> str | None:
    candidates = [
        os.environ.get("CHROME", ""),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ] + [shutil.which(n) or "" for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge")]
    return next((c for c in candidates if c and Path(c).exists()), None)


def export_pdf(browser: str, html: Path, pdf: Path) -> int:
    """Print one page to PDF. Returns the number of pages in the result."""
    command = [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--hide-scrollbars",
               "--virtual-time-budget=20000", f"--print-to-pdf={pdf}", html.as_uri()]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        command.insert(1, "--no-sandbox")
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not pdf.exists():
        raise BuildError(f"the browser could not write {pdf.name}:\n{result.stderr.strip()[-600:]}")
    return len(re.findall(rb"/Type\s*/Page\b(?!s)", pdf.read_bytes()))


# ───────────────────────── Main ─────────────────────────

def main(argv: list[str]) -> int:
    check, pdf = "--check" in argv, "--pdf" in argv
    master_doc = Doc(CONTENT / f"{MASTER}.md")
    langs: list[Lang] = []
    for stem, folder in LANGUAGES:
        path = CONTENT / f"{stem}.md"
        if stem == MASTER:
            langs.append(Lang(stem, folder, master_doc))
            continue
        if not path.exists():
            continue
        merged, warnings, (done, total) = overlay(master_doc, Doc(path))
        langs.append(Lang(stem, folder, merged))
        print(f"{path.name}: {done} of {total} texts differ from English ({total - done} still to translate, or the same in both)")
        for w in warnings:
            print(f"  note: {w}")

    outputs: dict[str, str] = {}
    cv_pages: list[tuple[Lang, str]] = []
    for lang in langs:
        outputs[lang.folder + "index.html"] = site_page(Page(lang, langs))
        outputs[lang.folder + "cv/index.html"] = cv_page(Page(lang, langs, "cv/"))
        cv_pages.append((lang, lang.folder + "cv/index.html"))
    if any(l.stem == "bg" for l in langs):
        outputs["cv/bg.html"] = redirect("../bg/cv/")      # the Bulgarian CV used to live here

    stale = [name for name, text in outputs.items()
             if not (ROOT / name).exists() or (ROOT / name).read_text(encoding="utf-8") != text]
    if check:
        if stale:
            print("Out of date: " + ", ".join(stale) + "\nRun: python3 build.py")
            return 1
        print("The pages are up to date.")
        return 0
    for name, text in outputs.items():
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(f"Wrote {len(outputs)} pages" + (f" ({len(stale)} changed)" if stale else " (nothing changed)") + ".")

    if pdf:
        browser = find_browser()
        if not browser:
            print("No Chrome or Chromium found. Set CHROME=/path/to/browser, or open the CV page and print it to PDF.")
            return 1
        for lang, name in cv_pages:
            target = ROOT / lang.doc.nodes["cv"].get("pdf")
            pages = export_pdf(browser, ROOT / name, target)
            note = "" if pages == 1 else f"  ← {pages} pages: shorten the text in content/{lang.stem}.md"
            print(f"Wrote {target.name}{note}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BuildError as error:
        print(f"build.py: {error}", file=sys.stderr)
        sys.exit(1)
