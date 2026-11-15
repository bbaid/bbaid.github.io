# bbaid.github.io

Portfolio of Bojan Baidanoff — live at [bbaid.github.io](https://bbaid.github.io).

A static site with no build step: GitHub Pages serves the files as they are.

```
index.html           the whole page: hero, work, GIS Club SU, code, about, contact
assets/css/style.css styles, light and dark themes
assets/js/main.js    theme toggle, project filter, map viewer, scroll reveal
assets/img/          maps as WebP: <name>.webp (full size) and <name>-sm.webp (card)
CV_Bojan_GIS.pdf     CV linked from the page
```

## Adding a project

1. Export the map and save two WebP files in `assets/img/`: the full size
   (about 2200 px on the long side) and a `-sm` version (about 1000 px wide).
2. Copy one `<article class="card">` block in `index.html` and change the image
   paths, the text, and `data-cat` (`nature`, `climate`, `terrain` or `people`).
   Images that share a `data-group` open together in the map viewer.

## Adding sheets to the atlas book

The V4+2 atlas is shown as a book with turning pages. Each `<li class="page">`
inside `<ol class="book-pages">` in `index.html` is one page, in reading order.

1. Save the sheet as WebP in `assets/img/atlas/`, about 1400 px wide
   (A3 portrait, so 1414 × 2000 works well).
2. Copy one `<li class="page page-map">` block and change `data-title`,
   `data-full`, `data-caption`, and the image `src` and `alt`.

Keep the cover first and the back cover last. On wide screens the pages pair up
as spreads after the cover, so companion sheets (for example 10 and 10a) face
each other when the first of the pair sits on an even position after the cover.

To preview locally, run `python3 -m http.server` in this folder and open
<http://localhost:8000>.
