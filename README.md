# Campus Livre website

Static site for Campus Livre and MatLivre, in English and Brazilian Portuguese. Plain HTML, CSS and a
few lines of JS. There is no build step, no external fonts, no CDN and no tracking.

```
index.html            Campus Livre home
matlivre/index.html   MatLivre product page
assets/               style.css, site.js, favicon, screenshots
.nojekyll             tells GitHub Pages to serve files as they are
```

## Publish on GitHub Pages

1. Create a repository (`campuslivre/campuslivre.github.io` serves at the root of
   `https://campuslivre.github.io/`; any other name serves under `/<repo-name>/`).
2. Push these files to `main`.
3. Settings, Pages, Source: "Deploy from a branch", branch `main`, folder `/ (root)`.

All links are relative, so it works at either kind of URL. For a custom domain, add a `CNAME` file.

## Preview locally

```bash
python -m http.server 8000
```

## Editing text

Every translatable element comes as an `lang="en"` / `lang="pt-BR"` pair; `assets/site.js` shows the
one that matches the visitor's choice (browser language by default). Edit both when you change copy.
Benchmark numbers and limits on the MatLivre page come from the MatLivre README; update them when the
README changes.
