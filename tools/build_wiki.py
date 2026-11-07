#!/usr/bin/env python3
"""Builds the MatLivre wiki under matlivre/wiki/:

  wiki/                      home (search, guide topics, function categories)
  wiki/<topic>/              the hand-written guide (tools/wiki_guide.py)
  wiki/functions/            every function, searchable
  wiki/categories/<slug>/    one page per category, with a summary of each function
  wiki/fn/<slug>/            one page per function (tools/wiki-data/*.json)
  assets/wiki-search.json    index for the search box
  sitemap.xml

Usage, from the site root:

  python tools/build_wiki.py RELEASE_COVERAGE.md [MASTER_COVERAGE.md] [--cli PATH_TO_matlivre-cli]

RELEASE_COVERAGE.md is docs/matlab-coverage.md at the latest release tag; MASTER_COVERAGE.md (optional)
adds names that are on master but not released yet, marked "next release".
--cli runs every example with matlivre-cli and stores its real output in tools/wiki-cache/outputs.json
(a cache keyed by the example's code; without --cli only cached outputs are used).

    git -C ../matlivre show v0.1.3:docs/matlab-coverage.md > release-cov.md
    python tools/build_wiki.py release-cov.md ../matlivre/docs/matlab-coverage.md --cli ../matlivre/target/release/matlivre-cli.exe
"""
import collections
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import langsplit as LS  # noqa: E402
import wiki_guide as G  # noqa: E402
from wiki_guide import L, esc, slug  # noqa: E402

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://campuslivre.github.io'
REPO = 'https://github.com/campuslivre/matlivre'
VERSION = 'v0.1.4'
TODAY = '2026-11-07'
DATA_DIR = os.path.join(SITE, 'tools', 'wiki-data')
CACHE = os.path.join(SITE, 'tools', 'wiki-cache', 'outputs.json')
WIKI = os.path.join(SITE, 'matlivre', 'wiki')


# ------------------------------------------------------------------ small markup
def md(text):
    """Plain text with `code` spans -> escaped HTML (no paragraphs)."""
    out = esc(text or '')
    out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
    return out


def paras(text, lang, cls=''):
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{c} lang="{lang}">{md(p.strip())}</p>\n' for p in (text or '').split('\n\n') if p.strip())


def bi_paras(d, cls=''):
    if not d:
        return ''
    return paras(d.get('en', ''), 'en', cls) + paras(d.get('pt', ''), 'pt-BR', cls)


def bi_inline(d):
    if not d:
        return ''
    return f'<span lang="en">{md(d.get("en", ""))}</span><span lang="pt-BR">{md(d.get("pt", ""))}</span>'


# ------------------------------------------------------------------ names -> slugs
OPS = {'+': 'plus', '-': 'minus', '*': 'mtimes', '.*': 'times', '/': 'mrdivide', './': 'rdivide', '\\': 'mldivide',
       '.\\': 'ldivide', '^': 'mpower', '.^': 'power', "'": 'ctranspose', ".'": 'transpose', '==': 'eq', '~=': 'ne',
       '<': 'lt', '<=': 'le', '>': 'gt', '>=': 'ge', '&': 'and', '|': 'or', '~': 'not',
       'Short-Circuit &&': 'short-circuit-and', 'Short-Circuit ||': 'short-circuit-or'}
RESERVED = {'con', 'prn', 'aux', 'nul'} | {f'com{i}' for i in range(1, 10)} | {f'lpt{i}' for i in range(1, 10)}


def make_slugs(names):
    slugs, used = {}, set()
    for n in sorted(names, key=lambda s: (s.lower(), s)):
        if n in OPS:
            s = 'op-' + OPS[n]
        else:
            s = re.sub(r'[^a-z0-9._]+', '-', n.lower()).strip('-.') or 'fn'
        if s in RESERVED:
            s += '-fn'
        base, k = s, 2
        while s in used:
            s = f'{base}-{k}'
            k += 1
        used.add(s)
        slugs[n] = s
    return slugs


# ------------------------------------------------------------------ coverage
def parse_cov(text):
    out = collections.OrderedDict()
    for m in re.finditer(r'^## (.+?)\n(.*?)(?=^## |\Z)', text, re.S | re.M):
        key, body = m.group(1).strip(), m.group(2)
        names = []
        for im in re.finditer(r'^Implemented: (`.*)$', body, re.M):
            names += [html.unescape(x) for x in re.findall(r'`([^`]+)`', im.group(1))]
        out[key] = list(dict.fromkeys(names))
    return out


def load_subgroups(repo):
    subs = {}
    d = os.path.join(repo, 'tools', 'coverage')
    for fn, cols in (('documented.tsv', 3), ('classes.tsv', 2)):
        p = os.path.join(d, fn)
        if not os.path.exists(p):
            continue
        for l in open(p, encoding='utf-8'):
            f = l.rstrip('\r\n').split('\t')
            if len(f) != cols:
                continue
            prod, cat, name = (f[0], f[1], f[2]) if cols == 3 else ('matlab', f[0], f[1])
            parts = cat.split(' > ')
            key = ('MATLAB > ' if prod == 'matlab' else 'Symbolic Math Toolbox > ') + ' > '.join(parts[:2])
            subs.setdefault(key, {}).setdefault(html.unescape(name), parts[2] if len(parts) > 2 else '')
    return subs


# ------------------------------------------------------------------ authored data + example outputs
def load_data():
    data = {}
    if os.path.isdir(DATA_DIR):
        for fn in sorted(os.listdir(DATA_DIR)):
            if fn.endswith('.json'):
                d = json.load(open(os.path.join(DATA_DIR, fn), encoding='utf-8'))
                for name, e in d.get('functions', {}).items():
                    data[name] = e
    return data


def load_cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding='utf-8'))
    return {}


def run_example(code, cli, cache):
    key = hashlib.sha1(code.encode('utf-8')).hexdigest()
    if key in cache:
        return cache[key]
    if not cli:
        return None
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'ex.m')
        open(p, 'w', encoding='utf-8', newline='\n').write(code + '\n')
        try:
            r = subprocess.run([cli, p], capture_output=True, timeout=60, cwd=d)
            out = (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')).replace('\r\n', '\n').rstrip()
            res = {'out': out, 'err': bool(re.search(r'^Error', out, re.M)) or r.returncode != 0}
        except subprocess.TimeoutExpired:
            res = {'out': '', 'err': True}
    cache[key] = res
    return res


# ------------------------------------------------------------------ page shell
ICON_FLAG = ('<svg class="flag-br" viewBox="0 0 20 14" aria-hidden="true"><rect width="20" height="14" rx="2" fill="#009c3b"/>'
             '<path d="M10 1.6 18 7l-8 5.4L2 7z" fill="#ffdf00"/><circle cx="10" cy="7" r="3.1" fill="#002776"/>'
             '<path d="M7.1 6.2c2-.5 4.3-.2 5.9 1.2" fill="none" stroke="#fff" stroke-width=".6"/></svg>')


class Ctx:
    """Per-page relative paths."""

    def __init__(self, rel):  # rel: path under matlivre/wiki/, e.g. 'fn/abs'
        depth = 2 + len([p for p in rel.split('/') if p])  # matlivre/wiki/<rel...>
        self.rel = rel
        self.root = '../' * depth          # site root
        self.ml = self.root + 'matlivre/'  # matlivre/
        self.wiki = self.root + 'matlivre/wiki/'
        self.url = f'{BASE}/matlivre/wiki/' + (rel + '/' if rel else '')

    def fix(self, s):
        return s.replace('@ML@', self.ml).replace('@WIKI@', self.wiki)


def sidebar(ctx, topics, current):
    items = ''.join(
        f'<li><a href="{ctx.wiki}{i}/"' + (' aria-current="page"' if current == i else '') + f'>{L(en, pt)}</a></li>'
        for i, en, pt in topics)
    cur = ' aria-current="page"' if current == 'functions' else ''
    return f'''<aside class="wiki-nav" aria-label="Wiki">
      <div class="wiki-nav-title">{L("Guide", "Guia")}</div>
      <ol>{items}</ol>
      <div class="wiki-nav-title" style="margin-top:1.2rem">{L("Reference", "Referência")}</div>
      <ol>
        <li><a href="{ctx.wiki}functions/"{cur}>{L("All functions", "Todas as funções")}</a></li>
        <li><a href="{ctx.wiki}#categories">{L("Categories", "Categorias")}</a></li>
      </ol>
    </aside>'''


def shell(ctx, *, title_en, title_pt, desc_en, desc_pt, keywords, body, topics, current, crumbs, noindex=False, scripts='', otype='article'):
    og = f'{BASE}/assets/img/og-matlivre.png'
    items = [{"@type": "ListItem", "position": 1, "name": "Campus Livre", "item": f'{BASE}/'},
             {"@type": "ListItem", "position": 2, "name": "MatLivre", "item": f'{BASE}/matlivre/'},
             {"@type": "ListItem", "position": 3, "name": "Wiki", "item": f'{BASE}/matlivre/wiki/'}]
    for i, (name, url) in enumerate(crumbs):
        items.append({"@type": "ListItem", "position": 4 + i, "name": name, "item": url or ctx.url})
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": title_en, "description": desc_en,
         "url": ctx.url, "image": og, "inLanguage": ["en", "pt-BR"], "dateModified": TODAY,
         "about": {"@type": "SoftwareApplication", "name": "MatLivre", "url": f'{BASE}/matlivre/'},
         "publisher": {"@type": "Organization", "name": "Campus Livre", "url": f'{BASE}/'}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}], ensure_ascii=False)
    robots = 'noindex, follow' if noindex else 'index, follow, max-image-preview:large'
    desc = f'{desc_en} / {desc_pt}'
    r = ctx.root
    crumb_html = f'<a href="{ctx.ml}">MatLivre</a> › <a href="{ctx.wiki}">Wiki</a>' + ''.join(
        ' › ' + (f'<a href="{u.replace(BASE + "/", ctx.root)}">{esc(n)}</a>' if u else f'<span>{esc(n)}</span>') for n, u in crumbs)
    return f'''<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title data-en="{html.escape(title_en)}" data-pt="{html.escape(title_pt)}">{esc(title_en)}</title>
  <meta name="description" content="{html.escape(desc_en)}" data-pt="{html.escape(desc_pt)}">
  <meta name="keywords" content="{html.escape(keywords)}">
  <meta name="theme-color" content="#00693e">
  <link rel="icon" href="{r}assets/icons/matlivre-16.svg" type="image/svg+xml">
  <link rel="icon" href="{r}assets/icons/matlivre-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="{r}assets/icons/matlivre-180.png">
  <!-- seo:start -->
  <link rel="canonical" href="{ctx.url}">
  <meta name="robots" content="{robots}">
  <meta name="author" content="Campus Livre">
  <meta property="og:site_name" content="Campus Livre">
  <meta property="og:type" content="{otype}">
  <meta property="og:url" content="{ctx.url}">
  <meta property="og:title" content="{html.escape(title_en)}" data-pt="{html.escape(title_pt)}">
  <meta property="og:description" content="{html.escape(desc_en)}" data-pt="{html.escape(desc_pt)}">
  <meta property="og:image" content="{og}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="MatLivre showing a live script with code, results and a plot. Free MATLAB and Octave alternative." data-pt="MatLivre mostrando um live script com código, resultados e um gráfico. Alternativa gratuita ao MATLAB e ao Octave.">
  <meta property="og:locale" content="en_US">
  <meta property="og:locale:alternate" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title_en)}" data-pt="{html.escape(title_pt)}">
  <meta name="twitter:description" content="{html.escape(desc_en)}" data-pt="{html.escape(desc_pt)}">
  <meta name="twitter:image" content="{og}">
  <meta name="twitter:image:alt" content="MatLivre showing a live script with code, results and a plot. Free MATLAB and Octave alternative." data-pt="MatLivre mostrando um live script com código, resultados e um gráfico. Alternativa gratuita ao MATLAB e ao Octave.">
  <script type="application/ld+json">{ld}</script>
  <!-- seo:end -->
  <link rel="stylesheet" href="{r}assets/style.css">
  <script src="{r}assets/site.js" defer></script>
  <script src="{r}assets/wiki.js" defer></script>
  <script src="{r}assets/highlight.js" defer></script>{scripts}
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{r}">
      <img src="{r}assets/icons/campuslivre-32.svg" width="28" height="28" alt="">
      Campus Livre
    </a>
    <span class="made-br" title="Made in Brazil · Feito no Brasil">{ICON_FLAG}<span lang="en">Made in Brazil</span><span lang="pt-BR">Feito no Brasil</span></span>
    <nav aria-label="Main">
      <a class="hide-sm" href="{ctx.wiki}"{' aria-current="page"' if current == 'home' else ''}>{L('Wiki', 'Wiki')}</a>
      <a class="hide-sm" href="{ctx.wiki}functions/">{L('Functions', 'Funções')}</a>
      <a href="{ctx.ml}" class="with-ico"><img class="ico" src="{r}assets/icons/matlivre-16.svg" width="18" height="18" alt="">MatLivre</a>
      <div class="lang-toggle" role="group" aria-label="Language / Idioma">
        <button type="button" data-set="en" aria-pressed="true">EN</button>
        <button type="button" data-set="pt-BR" aria-pressed="false">PT</button>
      </div>
    </nav>
  </div>
</header>
<div class="stripe" aria-hidden="true"></div>

<main>
<section class="wiki">
  <div class="wrap wiki-grid">
    {sidebar(ctx, topics, current)}
    <div class="wiki-main">
      <div class="wiki-bar">
        <div class="wiki-search">
          <label for="wiki-q" class="sr-only">{L('Search the wiki', 'Pesquisar na wiki')}</label>
          <input id="wiki-q" type="search" autocomplete="off" spellcheck="false" placeholder="plot, ode45, containers.Map ..." data-index="{r}assets/wiki-search.json" data-base="{ctx.wiki}fn/">
          <div id="wiki-results" class="wiki-results" hidden></div>
        </div>
      </div>
      <nav class="crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
      <article class="wiki-body">
{body}
      </article>
    </div>
  </div>
</section>
</main>

{footer(ctx)}

</body>
</html>
'''


def footer(ctx):
    r = ctx.root
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand" href="{r}" style="margin-bottom:.8rem">
          <img src="{r}assets/icons/campuslivre-32.svg" width="28" height="28" alt="">
          Campus Livre
        </a>
        <p lang="en" style="max-width:26em">Free software for academic and scientific work.<br>Made in Brazil. 🇧🇷</p>
        <p lang="pt-BR" style="max-width:26em">Software livre para o trabalho acadêmico e científico.<br>Feito no Brasil. 🇧🇷</p>
      </div>
      <div>
        <h4 class="with-ico"><img class="ico" src="{r}assets/icons/matlivre-16.svg" width="18" height="18" alt=""><a href="{ctx.ml}">MatLivre</a></h4>
        <ul>
          <li><a href="{ctx.wiki}"><span lang="en">Wiki</span><span lang="pt-BR">Wiki</span></a></li>
          <li><a href="{ctx.wiki}functions/"><span lang="en">Functions</span><span lang="pt-BR">Funções</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre/releases/latest"><span lang="en">Download</span><span lang="pt-BR">Baixar</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre">GitHub</a></li>
          <li><a href="https://github.com/campuslivre/matlivre/issues"><span lang="en">Report an issue</span><span lang="pt-BR">Relatar um problema</span></a></li>
          <li><a href="https://github.com/campuslivre/matlivre/blob/master/LICENSE"><span lang="en">MIT licence</span><span lang="pt-BR">Licença MIT</span></a></li>
        </ul>
      </div>
      <div>
        <h4 lang="en">Campus Livre</h4><h4 lang="pt-BR">Campus Livre</h4>
        <ul>
          <li><a href="{r}"><span lang="en">Home</span><span lang="pt-BR">Início</span></a></li>
          <li><a href="{r}#principles"><span lang="en">Principles</span><span lang="pt-BR">Princípios</span></a></li>
        </ul>
      </div>
    </div>
    <p class="fine" lang="en">This site sets no cookies, loads no third-party fonts or scripts, and tracks no one. MATLAB is a registered trademark of The MathWorks, Inc. MatLivre is an independent project and is not affiliated with or endorsed by The MathWorks or the GNU Octave project. Function descriptions are written independently for this wiki.</p>
    <p class="fine" lang="pt-BR">Este site não usa cookies, não carrega fontes nem scripts de terceiros e não rastreia ninguém. MATLAB é marca registrada da The MathWorks, Inc. O MatLivre é um projeto independente e não é afiliado nem endossado pela The MathWorks nem pelo projeto GNU Octave. As descrições das funções são escritas de forma independente para esta wiki.</p>
  </div>
</footer>'''


# ------------------------------------------------------------------ page builders
def write(rel, content):
    """Writes the bilingual page `content` as an English page and a Portuguese page (under /pt/)."""
    full = 'matlivre/wiki/' + (rel + '/' if rel else '')
    emit(full, content)


def emit(full, content):
    for lang, prefix in (('en', ''), ('pt-BR', 'pt/')):
        out = LS.render(content, full, lang)
        d = os.path.join(SITE, *(prefix + full).split('/'))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n').write(out)


def guide_pages(topics_full):
    ids = [t[0] for t in topics_full]
    topics = [(i, en, pt) for i, en, pt, _ in topics_full]
    out = []
    for n, (i, en, pt, body) in enumerate(topics_full):
        ctx = Ctx(i)
        prev = topics_full[n - 1] if n else None
        nxt = topics_full[n + 1] if n + 1 < len(topics_full) else None
        nav = '<div class="pager">' + (
            f'<a class="prev" href="{ctx.wiki}{prev[0]}/">← {L(prev[1], prev[2])}</a>' if prev else '<span></span>') + (
            f'<a class="next" href="{ctx.wiki}{nxt[0]}/">{L(nxt[1], nxt[2])} →</a>' if nxt else '<span></span>') + '</div>'
        page_body = G.H('h1', en, pt) + ctx.fix(body) + nav
        out.append((i, shell(
            ctx, title_en=f'{en} | MatLivre wiki', title_pt=f'{pt} | Wiki do MatLivre',
            desc_en=f'MatLivre guide: {en.lower()}. How to use the free MATLAB alternative.',
            desc_pt=f'Guia do MatLivre: {pt.lower()}. Como usar a alternativa gratuita ao MATLAB.',
            keywords=f'MatLivre, {en}, {pt}, MatLivre tutorial, MatLivre documentation, documentação MatLivre, como usar o MatLivre',
            body=page_body, topics=topics, current=i, crumbs=[(en, None)])))
    return out


def pretty(rest):
    """Display name of a category: the undocumented public functions of a toolbox folder get a readable title."""
    if rest.startswith('matlab/'):
        return 'Other public functions: ' + rest[len('matlab/'):]
    return rest


def cat_slug(key):
    return slug(key)


def build(release_md, master_md, repo, cli):
    rel = parse_cov(open(release_md, encoding='utf-8').read())
    mas = parse_cov(open(master_md, encoding='utf-8').read()) if master_md else rel
    subs = load_subgroups(repo) if repo else {}
    data = load_data()
    cache = load_cache()

    rel_names = {n for v in rel.values() for n in v}
    all_names = sorted({n for v in mas.values() for n in v} | rel_names, key=lambda s: (s.lower(), s))
    slugs = make_slugs(all_names)
    nxt_names = set(all_names) - rel_names
    n_rel = len(rel_names)
    n_pt = f'{n_rel:,}'.replace(',', '.')

    topics_full = G.docs_sections()
    topics = [(i, en, pt) for i, en, pt, _ in topics_full]

    # categories
    keys = [k for k in mas if mas.get(k) or rel.get(k)]
    cats = collections.OrderedDict()
    for k in keys:
        names = list(dict.fromkeys(rel.get(k, []) + mas.get(k, [])))
        cats[k] = names
    name_cat = {}   # a name listed in several categories lives in the most specific (smallest) one
    for k, names in sorted(cats.items(), key=lambda kv: len(kv[1]), reverse=True):
        for n in names:
            name_cat[n] = k

    # clean old output
    for d in (WIKI, os.path.join(SITE, 'pt')):
        if os.path.isdir(d):
            shutil.rmtree(d)
    for old in ('docs', 'functions'):
        shutil.rmtree(os.path.join(SITE, 'matlivre', old), ignore_errors=True)
    os.makedirs(WIKI)

    # ---- guide pages
    sitemap = [('matlivre/wiki/', '0.8')]
    for i, page in guide_pages(topics_full):
        write(i, page)
        sitemap.append((f'matlivre/wiki/{i}/', '0.7'))

    # ---- function pages
    problems, missing = [], []
    for n, name in enumerate(all_names):
        e = data.get(name)
        cat = name_cat.get(name, '')
        ctx = Ctx(f'fn/{slugs[name]}')
        in_next = name in nxt_names
        if not e:
            missing.append(name)
        page, indexed = function_page(ctx, name, e, cat, in_next, slugs, set(all_names), cats, topics, cli, cache, problems)
        write(f'fn/{slugs[name]}', page)
        if indexed:
            sitemap.append((f'matlivre/wiki/fn/{slugs[name]}/', '0.5'))

    # ---- category pages
    for k, names in cats.items():
        ctx = Ctx(f'categories/{cat_slug(k)}')
        write(f'categories/{cat_slug(k)}', category_page(ctx, k, names, rel, subs, slugs, data, topics))
        sitemap.append((f'matlivre/wiki/categories/{cat_slug(k)}/', '0.6'))

    # ---- functions index + home
    ctx = Ctx('functions')
    write('functions', functions_index(ctx, cats, rel, subs, slugs, nxt_names, n_rel, n_pt, topics))
    sitemap.append(('matlivre/wiki/functions/', '0.8'))
    ctx = Ctx('')
    write('', home_page(ctx, cats, topics, n_rel, n_pt))

    # ---- search index
    idx = []
    cat_list = list(cats)
    for name in all_names:
        e = data.get(name) or {}
        s = e.get('summary') or {}
        idx.append([name, slugs[name], cat_list.index(name_cat.get(name, cat_list[0])), s.get('en', ''), s.get('pt', ''), 1 if name in nxt_names else 0])
    json.dump({'cats': [pretty(c.split(' > ', 1)[1] if ' > ' in c else c) for c in cat_list], 'f': idx},
              open(os.path.join(SITE, 'assets', 'wiki-search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

    # ---- home and product page (sources in tools/src, bilingual like the wiki pages)
    for src, rel in (('index.html', ''), ('matlivre.html', 'matlivre/')):
        emit(rel, open(os.path.join(SITE, 'tools', 'src', src), encoding='utf-8').read())

    # ---- sitemap: every page in both languages, with hreflang alternates
    urls = [('', '1.0'), ('matlivre/', '0.9')] + sitemap

    def entry(u, p, prefix):
        en, pt = f'{BASE}/{u}', f'{BASE}/pt/{u}'
        loc = pt if prefix else en
        alts = (f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="pt-BR" href="{pt}"/>'
                f'<xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>')
        return f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority>{alts}</url>\n'

    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + ''.join(entry(u, p, '') + entry(u, p, 'pt') for u, p in urls) + '</urlset>\n')

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)

    print(f'{len(all_names)} function pages ({n_rel} released, {len(nxt_names)} next release), {len(cats)} categories, {len(topics)} guide topics')
    print(f'authored: {len(all_names) - len(missing)}; missing (fallback page, noindex): {len(missing)}')
    if problems:
        print(f'{len(problems)} example problems:')
        for p in problems[:40]:
            print('  ', p)
    json.dump(missing, open(os.path.join(SITE, 'tools', 'wiki-cache', 'missing.json'), 'w', encoding='utf-8'))


def function_page(ctx, name, e, cat, in_next, slugs, known, cats, topics, cli, cache, problems):
    cat_name = pretty(cat.split(' > ', 1)[1] if ' > ' in cat else cat)
    cslug = cat_slug(cat) if cat else ''
    names = cats.get(cat, [])
    badge = ''
    if in_next:
        badge = f' <span class="badge-next" title="Next release / Próxima versão">{L("next release", "próxima versão")}</span>'
    if e:
        summ = e['summary']
        title_en = f'{name} | MatLivre function reference'
        title_pt = f'{name} | Referência de funções do MatLivre'
        desc_en, desc_pt = summ.get('en', ''), summ.get('pt', '')
    else:
        summ = {'en': f'A function in the category {cat_name}.', 'pt': f'Uma função da categoria {cat_name}.'}
        title_en, title_pt = f'{name} | MatLivre function reference', f'{name} | Referência de funções do MatLivre'
        desc_en, desc_pt = summ['en'], summ['pt']

    parts = [f'<h1 class="fn-title"><code>{esc(name)}</code>{badge}</h1>\n<p class="lead" lang="en">{md(summ.get("en", ""))}</p>\n<p class="lead" lang="pt-BR">{md(summ.get("pt", ""))}</p>\n']
    if cat:
        parts.append(f'<p class="fn-cat"><span lang="en">Category:</span><span lang="pt-BR">Categoria:</span> <a href="{ctx.wiki}categories/{cslug}/">{esc(cat_name)}</a></p>\n')

    if e:
        syn = e.get('syntax') or []
        if syn:
            parts.append(G.H('h2', 'Syntax', 'Sintaxe'))
            for s in syn:
                parts.append(f'<div class="syn"><pre><code>{esc(s["code"])}</code></pre>\n{bi_paras(s)}</div>\n')
        if e.get('description'):
            parts.append(G.H('h2', 'Description', 'Descrição') + bi_paras(e['description']))
        for key, h_en, h_pt in (('inputs', 'Input arguments', 'Argumentos de entrada'), ('outputs', 'Output arguments', 'Argumentos de saída')):
            items = e.get(key) or []
            if items:
                dl = ''.join(f'<dt><code>{esc(i["name"])}</code></dt><dd lang="en">{md(i.get("en", ""))}</dd><dd lang="pt-BR">{md(i.get("pt", ""))}</dd>' for i in items)
                parts.append(G.H('h2', h_en, h_pt) + f'<dl class="args">{dl}</dl>\n')
        exs = e.get('examples') or []
        if exs:
            parts.append(G.H('h2', 'Examples', 'Exemplos') if len(exs) > 1 else G.H('h2', 'Example', 'Exemplo'))
            for ex in exs:
                code = ex['code'].strip('\n')
                res = run_example(code, cli, cache)
                title = ex.get('title')
                if title:
                    parts.append(G.H('h3', esc(title.get('en', '')), esc(title.get('pt', ''))))
                parts.append(f'<pre><code>{esc(code)}</code></pre>\n')
                if res is None:
                    pass
                elif res['err']:
                    problems.append(f'{name}: example fails: {res["out"][:100]!r}')
                elif res['out'].strip():
                    parts.append(f'<div class="out-label">{L("Output", "Saída")}</div>\n<pre class="out"><code>{esc(res["out"])}</code></pre>\n')
                if ex.get('note'):
                    parts.append(bi_paras(ex['note'], 'note'))
        if e.get('notes'):
            parts.append(G.H('h2', 'Notes', 'Observações') + bi_paras(e['notes']))
        see = [s for s in (e.get('see') or []) if s in known and s != name]
        if see:
            links = ' '.join(f'<a class="fn-chip" href="{ctx.wiki}fn/{slugs[s]}/"><code>{esc(s)}</code></a>' for s in see)
            parts.append(G.H('h2', 'See also', 'Veja também') + f'<p class="fn-see">{links}</p>\n')
    else:
        parts.append(G.P('This page is still being written. The function is part of MatLivre; see the <a href="@ML@#get">repository</a> to try it or to help document it.',
                         'Esta página ainda está sendo escrita. A função faz parte do MatLivre; veja o <a href="@ML@#get">repositório</a> para testá-la ou ajudar a documentá-la.', ' class="note"'))

    # prev / next inside the category
    pager = ''
    if cat and name in names:
        i = names.index(name)
        sort_names = sorted(names, key=lambda s: (s.lower(), s))
        j = sort_names.index(name)
        pv = sort_names[j - 1] if j else None
        nx = sort_names[j + 1] if j + 1 < len(sort_names) else None
        pager = '<div class="pager">' + (
            f'<a class="prev" href="{ctx.wiki}fn/{slugs[pv]}/">← <code>{esc(pv)}</code></a>' if pv else '<span></span>') + (
            f'<a class="next" href="{ctx.wiki}fn/{slugs[nx]}/"><code>{esc(nx)}</code> →</a>' if nx else '<span></span>') + '</div>\n'
    body = ctx.fix(''.join(parts)) + pager
    page = shell(ctx, title_en=title_en, title_pt=title_pt, desc_en=desc_en, desc_pt=desc_pt,
                 keywords=f'{name}, MatLivre {name}, MATLAB {name}, {name} function, função {name}, {cat_name}',
                 body=body, topics=topics, current='fn',
                 crumbs=[('Functions', f'{BASE}/matlivre/wiki/functions/')] + ([(cat_name, f'{BASE}/matlivre/wiki/categories/{cslug}/')] if cat else []) + [(name, None)],
                 noindex=not e)
    return page, bool(e)


def category_page(ctx, key, names, rel, subs, slugs, data, topics):
    prod, rest = key.split(' > ', 1)
    rest = pretty(rest)
    groups = collections.OrderedDict()
    for x in sorted(names, key=lambda s: (s.lower(), s)):
        groups.setdefault(subs.get(key, {}).get(x, ''), []).append(x)
    rows = []
    for g, ns in groups.items():
        if g:
            rows.append(f'<h3 class="fn-sub">{esc(g)}</h3>')
        trs = []
        for x in ns:
            s = (data.get(x) or {}).get('summary') or {}
            nxt = '' if x in {n for n in rel.get(key, [])} else f' <span class="badge-next">{L("next release", "próxima versão")}</span>'
            trs.append(f'<tr><td><a href="{ctx.wiki}fn/{slugs[x]}/"><code>{esc(x)}</code></a>{nxt}</td><td>{bi_inline(s)}</td></tr>')
        rows.append('<div class="table-wrap"><table class="compare fn-table"><tbody>' + ''.join(trs) + '</tbody></table></div>')
    body = (G.H('h1', esc(rest), esc(rest)) + G.P(f'{len(names)} functions in {esc(prod)} › {esc(rest)}.', f'{len(names)} funções em {esc(prod)} › {esc(rest)}.', ' class="lead"') + ''.join(rows))
    return shell(ctx, title_en=f'{rest} | MatLivre function reference', title_pt=f'{rest} | Referência de funções do MatLivre',
                 desc_en=f'The {len(names)} {prod} functions in {rest} that MatLivre implements, with a summary of each.',
                 desc_pt=f'As {len(names)} funções de {prod} em {rest} que o MatLivre implementa, com um resumo de cada uma.',
                 keywords=f'MatLivre, {rest}, {prod} functions, MATLAB {rest}, funções MATLAB, {rest}',
                 body=body, topics=topics, current='cat',
                 crumbs=[('Functions', f'{BASE}/matlivre/wiki/functions/'), (rest, None)])


def functions_index(ctx, cats, rel, subs, slugs, nxt_names, n_rel, n_pt, topics):
    prods = collections.OrderedDict()
    for k in cats:
        prod, rest = k.split(' > ', 1)
        rest = pretty(rest)
        prods.setdefault(prod, []).append((k, rest))
    jump, secs = [], []
    for prod, items in prods.items():
        secs.append(f'<h2 class="fn-prod" id="{slug(prod)}">{esc(prod)}</h2>')
        for key, rest in items:
            names = cats[key]
            sid = cat_slug(key)
            jump.append(f'<a href="#{sid}">{esc(rest)} <span>{len(names)}</span></a>')
            groups = collections.OrderedDict()
            for x in sorted(names, key=lambda s: (s.lower(), s)):
                groups.setdefault(subs.get(key, {}).get(x, ''), []).append(x)
            gh = []
            for g, ns in groups.items():
                chips = ' '.join(f'<a href="{ctx.wiki}fn/{slugs[x]}/"{" class=\"next\"" if x in nxt_names else ""}><code>{esc(x)}</code></a>' for x in ns)
                gh.append(f'<div class="fn-group">{"<h4 class=\"fn-sub\">" + esc(g) + "</h4>" if g else ""}<p class="fn-list">{chips}</p></div>')
            secs.append(f'<section class="fn-sec" id="{sid}"><h3><a href="{ctx.wiki}categories/{sid}/">{esc(rest)}</a> <span class="fn-count">{len(names)}</span></h3>{"".join(gh)}</section>')
    nxt_note = G.P(f'Names with a dashed outline are in the repository and will be in the next release ({len(nxt_names)} so far).',
                   f'Os nomes com contorno tracejado estão no repositório e estarão na próxima versão ({len(nxt_names)} até agora).', ' class="note"') if nxt_names else ''
    body = (G.H('h1', 'Every function MatLivre covers', 'Todas as funções que o MatLivre cobre')
            + G.P(f'{n_rel:,} functions, methods and operators from MATLAB R2023b and the Symbolic Math Toolbox, as of MatLivre {VERSION[1:]}. Each name opens its own page.',
                  f'{n_pt} funções, métodos e operadores do MATLAB R2023b e do Symbolic Math Toolbox, na versão {VERSION[1:]} do MatLivre. Cada nome abre a sua própria página.', ' class="lead"')
            + f'<div class="fn-search"><label for="fn-q" class="sr-only">{L("Filter", "Filtrar")}</label><input id="fn-q" type="search" autocomplete="off" spellcheck="false" placeholder="plot, ode45, containers.Map ..."><span id="fn-status" class="fn-status" aria-live="polite"></span></div>'
            + G.P('Category names follow the MATLAB function reference. Language keywords (<code>if</code>, <code>for</code>, <code>while</code>, <code>switch</code>, <code>try</code>, <code>classdef</code>, <code>function</code> and so on) are part of the language and not listed.',
                  'Os nomes das categorias seguem a referência de funções do MATLAB. As palavras-chave da linguagem (<code>if</code>, <code>for</code>, <code>while</code>, <code>switch</code>, <code>try</code>, <code>classdef</code>, <code>function</code> e outras) fazem parte da linguagem e não aparecem na lista.')
            + nxt_note
            + f'<details class="fn-jump" open><summary>{L("Categories", "Categorias")}</summary><nav class="fn-jump-list" aria-label="Categories">{"".join(jump)}</nav></details>'
            + f'<div id="fn-all">{"".join(secs)}</div><p id="fn-none" class="note" hidden>{L("No function matches your search.", "Nenhuma função corresponde à pesquisa.")}</p>')
    return shell(ctx, title_en=f'MatLivre function reference | {n_rel:,} MATLAB functions covered', title_pt=f'Referência de funções do MatLivre | {n_pt} funções do MATLAB cobertas',
                 desc_en=f'Searchable list of the {n_rel:,} MATLAB R2023b and Symbolic Math Toolbox functions MatLivre implements, each with its own page.',
                 desc_pt=f'Lista pesquisável das {n_pt} funções do MATLAB R2023b e do Symbolic Math Toolbox implementadas pelo MatLivre, cada uma com sua página.',
                 keywords='MatLivre functions, MATLAB function list, MATLAB compatibility, which MATLAB functions work in MatLivre, Octave vs MATLAB functions, Symbolic Math Toolbox functions, funções MATLAB, compatibilidade MATLAB, lista de funções MatLivre',
                 body=body, topics=topics, current='functions', crumbs=[('Functions', None)],
                 scripts=f'\n  <script src="{ctx.root}assets/functions.js" defer></script>')


def home_page(ctx, cats, topics, n_rel, n_pt):
    topic_cards = ''.join(f'<li><a href="{ctx.wiki}{i}/">{L(en, pt)}</a></li>' for i, en, pt in topics)
    cat_cards = []
    for k, names in cats.items():
        prod, rest = k.split(' > ', 1)
        rest = pretty(rest)
        cat_cards.append(f'<a class="cat-card" href="{ctx.wiki}categories/{cat_slug(k)}/"><b>{esc(rest)}</b><span>{esc(prod)} · {len(names)}</span></a>')
    body = (G.H('h1', 'MatLivre wiki', 'Wiki do MatLivre')
            + G.P(f'How to use MatLivre, and a page for each of the {n_rel:,} functions it covers: what it does, how it works, its inputs and outputs, and a tested example.',
                  f'Como usar o MatLivre, e uma página para cada uma das {n_pt} funções que ele cobre: o que faz, como funciona, entradas, saídas e um exemplo testado.', ' class="lead"')
            + f'<div class="home-cols"><div><h2>{L("Guide", "Guia")}</h2><ul class="topic-list">{topic_cards}</ul></div>'
            + f'<div><h2>{L("Function reference", "Referência de funções")}</h2>'
            + G.P(f'Search above, or <a href="{ctx.wiki}functions/">browse all {n_rel:,} functions</a>, or pick a category.',
                  f'Pesquise acima, ou <a href="{ctx.wiki}functions/">veja as {n_pt} funções</a>, ou escolha uma categoria.') + '</div></div>'
            + f'<h2 id="categories">{L("Categories", "Categorias")}</h2><div class="cat-grid">{"".join(cat_cards)}</div>')
    return shell(ctx, title_en='MatLivre wiki | Guide and function reference for the free MATLAB alternative',
                 title_pt='Wiki do MatLivre | Guia e referência de funções da alternativa gratuita ao MATLAB',
                 desc_en=f'The MatLivre wiki: how to use the program and a page for each of its {n_rel:,} MATLAB-compatible functions.',
                 desc_pt=f'A wiki do MatLivre: como usar o programa e uma página para cada uma de suas {n_pt} funções compatíveis com o MATLAB.',
                 keywords='MatLivre wiki, MatLivre documentation, MATLAB function reference, free MATLAB alternative docs, wiki MatLivre, documentação MatLivre, referência de funções MATLAB',
                 body=body, topics=topics, current='home', crumbs=[], otype='website')


def main():
    args = sys.argv[1:]
    cli = None
    if '--cli' in args:
        i = args.index('--cli')
        cli = os.path.abspath(args[i + 1])
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    release_md = args[0]
    master_md = args[1] if len(args) > 1 else None
    repo = os.path.dirname(os.path.dirname(os.path.abspath(master_md))) if master_md else None
    build(release_md, master_md, repo, cli)


if __name__ == '__main__':
    main()
