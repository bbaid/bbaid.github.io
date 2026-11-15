# bbaid.github.io

Portfolio of Bojan Baidanoff — live at [bbaid.github.io](https://bbaid.github.io).

All the text of the site and the CV lives in two markdown files, one per
language. A small script turns them into the pages. GitHub Pages then serves
those pages as they are.

```bash
python3 build.py
```

Run that after every change to the text, then commit both the markdown and the
pages it wrote. The script needs Python 3.9 or newer and nothing else.

## Where things are

```
content/en.md              all the English text; also names the images and links
content/bg.md              the Bulgarian text
templates/atlas-book.html  the pages of the V4+2 atlas book (the one part not in markdown)
build.py                   turns content/ into the pages below

index.html      cv/index.html         English site and CV      ┐ written by build.py:
bg/index.html   bg/cv/index.html      Bulgarian site and CV    ┘ do not edit by hand
CV_Bojan_GIS.pdf   CV_Bojan_GIS_BG.pdf   the two CVs as PDF

assets/css/style.css   cv/cv.css      styles for the site and for the CV
assets/js/main.js                     theme and language toggles, filter, map viewer, atlas book
assets/img/                           maps as WebP: <name>.webp and <name>-sm.webp
```

## How the markdown works

`content/en.md` is the master. Each piece of the site is a heading with an id:

```markdown
### Forests of Burgas province {#burgas}

Broadleaf, coniferous and mixed forest from CORINE Land Cover 2018. …

- `kicker`: Nature · Map
- `tags`: QGIS, CORINE 2018
- `image`: burgas-forests
- **40 %** of the province          ← a list entry with a label
```

- The heading is the title. The `{#id}` ties it to the same item in the other
  language, so never change an id.
- Plain paragraphs are the body text.
- `` - `key`: value `` is a named piece of text or data. Never change a `key`.
- Inside text you can use `**bold**`, `*italic*` and `[links](https://…)`.
- `<!-- comments -->` are ignored.

## Writing the Bulgarian version

`content/bg.md` follows `en.md` section by section and holds only text; images,
links and categories come from `en.md`. Replace the English text in it with
Bulgarian, keeping every `{#id}` and every `` `key` `` as it is.

Anything `bg.md` leaves out falls back to English, so the Bulgarian pages always
build, and you can translate a section at a time. Each build reports progress:

```
bg.md: 55 of 281 texts differ from English (226 still to translate, or the same in both)
```

It also warns if `bg.md` has an id that `en.md` does not (usually a typo), or a
different number of paragraphs or list entries in a section.

## Adding a project

1. Save the map as two WebP files in `assets/img/`: the full size (about
   2200 px on the long side) and a `-sm` version (about 1000 px wide).
2. In `content/en.md`, copy one `### … {#id}` block under `## Projects`, give it
   a new id, and change the text, `image` and `cat` (`nature`, `climate`,
   `terrain` or `people`; more than one is allowed).
3. Add the same heading with the same id to `content/bg.md` and write the
   Bulgarian text. Until you do, the Bulgarian page shows the English.
4. Run `python3 build.py`.

## The CV

The CV is the `# … {#cv}` part at the end of each content file. It is one A4
page, so keep the text short. To export the PDFs:

```bash
python3 build.py --pdf
```

This needs Chrome, Chromium, Edge or Brave. If the script cannot find one, give
it the path:

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" python3 build.py --pdf
```

If a CV no longer fits on one page, the script says so and names the file to
shorten.

## The atlas book

The V4+2 atlas is shown as a book with turning pages. Its pages are in
`templates/atlas-book.html`, in English for both languages: one
`<li class="page">` per page, in reading order. The labels around the book
(buttons, hint) are in the content files, under `{#atlas}`.

To add a sheet, save it as WebP in `assets/img/atlas/` (about 1400 px wide) and
copy one `<li class="page page-map">` block, changing `data-title`, `data-full`,
`data-caption`, and the image `src` and `alt`. Write image paths as
`{{root}}assets/img/atlas/…`. Keep the cover first and the back cover last.

## Checking and previewing

```bash
python3 build.py --check
```

says whether the committed pages match the markdown, without writing anything.

```bash
python3 -m http.server
```

serves the site at <http://localhost:8000> for a look before you push.
