"""Turns one bilingual page (paired elements lang="en" / lang="pt-BR") into a single-language page.

Used by build_wiki.py for every page of the site, so English lives at the normal URL and Portuguese at the same
path under /pt/ (hreflang alternates, canonical URLs and a real <a> language toggle included).

  render(html, rel, lang)   rel: the page's folder relative to the site root, e.g. '' (home), 'matlivre/',
                            'matlivre/wiki/fn/abs/'. lang: 'en' or 'pt-BR'.
"""
import html as _html
import re
from html.parser import HTMLParser

BASE = 'https://campuslivre.github.io'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
LANGS = ('en', 'pt-BR')


class _Filter(HTMLParser):
    def __init__(self, keep):
        super().__init__(convert_charrefs=False)
        self.keep, self.out, self.skip, self.depth = keep, [], None, 0

    @staticmethod
    def _lang(attrs):
        for k, v in attrs:
            if k == 'lang':
                return v
        return None

    def _drop(self, tag, attrs):
        l = self._lang(attrs)
        return tag != 'html' and l in LANGS and l != self.keep

    def handle_starttag(self, tag, attrs):
        if self.skip:
            if tag == self.skip:
                self.depth += 1
            return
        if self._drop(tag, attrs):
            if tag not in VOID:
                self.skip, self.depth = tag, 1
            return
        self.out.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.skip or self._drop(tag, attrs):
            return
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip:
                self.depth -= 1
                if self.depth == 0:
                    self.skip = None
            return
        self.out.append(f'</{tag}>')

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)

    def handle_entityref(self, name):
        if not self.skip:
            self.out.append(f'&{name};')

    def handle_charref(self, name):
        if not self.skip:
            self.out.append(f'&#{name};')

    def handle_comment(self, data):
        if not self.skip:
            self.out.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        self.out.append(f'<!{decl}>')

    def handle_pi(self, data):
        self.out.append(f'<?{data}>')


def _depth(rel):
    return len([p for p in rel.split('/') if p])


def urls(rel):
    return f'{BASE}/{rel}', f'{BASE}/pt/{rel}'


def render(src, rel, lang):
    pt = lang == 'pt-BR'
    d = _depth(rel)
    alt = ('../' * (d + 1) + rel) if pt else ('../' * d + 'pt/' + rel)
    en_url, pt_url = urls(rel)

    # 1. attribute pairs: <title data-en data-pt>, <meta content=".." data-pt="..">
    def title(m):
        v = m.group('pt') if pt else m.group('en')
        return '<title>' + _html.escape(_html.unescape(v), quote=False) + '</title>'
    src = re.sub(r'<title data-en="(?P<en>[^"]*)" data-pt="(?P<pt>[^"]*)">[^<]*</title>', title, src)

    def meta(m):
        v = m.group('pt') if pt else m.group('en')
        return f'<meta {m.group("pre")}content="{v}"{m.group("post")}>'
    src = re.sub(r'<meta (?P<pre>[^>]*?)content="(?P<en>[^"]*)" data-pt="(?P<pt>[^"]*)"(?P<post>[^>]*)>', meta, src)

    # 2. drop the other language's elements
    f = _Filter(lang)
    f.feed(src)
    f.close()
    out = ''.join(f.out)

    # 3. <html>
    out = re.sub(r'<html[^>]*>', f'<html lang="{lang}" data-lang="{lang}" data-static data-alt="{alt}">', out, count=1)

    # 4. absolute URLs of pages -> this language's URLs (assets stay shared)
    if pt:
        out = re.sub(r'https://campuslivre\.github\.io/(?!assets/|pt/)', BASE + '/pt/', out)
        out = out.replace('content="en_US"', 'content="__pt__"').replace('content="pt_BR"', 'content="en_US"').replace('content="__pt__"', 'content="pt_BR"')
        # shared assets live one level up
        out = re.sub(r'(?<=["\'])((?:\.\./)*)assets/', r'\1../assets/', out)

    # 5. hreflang alternates and the early language redirect, then the toggle as real links
    alt_tags = (f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
                f'  <link rel="alternate" hreflang="pt-BR" href="{pt_url}">\n'
                f'  <link rel="alternate" hreflang="x-default" href="{en_url}">\n  ')
    out = out.replace('<!-- seo:end -->', alt_tags + '<!-- seo:end -->', 1)
    m = re.search(r'<link rel="stylesheet" href="((?:\.\./)*)(?:\.\./)?assets/style\.css">', out)
    if m:
        href = re.search(r'href="([^"]*assets/)style\.css"', m.group(0)).group(1)
        out = out.replace(m.group(0), f'<script src="{href}lang-redirect.js"></script>\n  ' + m.group(0), 1)

    en_href, pt_href = ('./', alt) if not pt else (alt, './')
    toggle = ('<div class="lang-toggle" role="group" aria-label="Language / Idioma">'
              f'<a href="{en_href}" hreflang="en" data-set="en"' + (' aria-current="true"' if not pt else '') + '>EN</a>'
              f'<a href="{pt_href}" hreflang="pt-BR" data-set="pt-BR"' + (' aria-current="true"' if pt else '') + '>PT</a></div>')
    out = re.sub(r'<div class="lang-toggle".*?</div>', toggle, out, count=1, flags=re.S)
    return out
