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

To preview locally, run `python3 -m http.server` in this folder and open
<http://localhost:8000>.
