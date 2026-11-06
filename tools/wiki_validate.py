#!/usr/bin/env python3
"""Checks a wiki data file (tools/wiki-data/*.json) and runs its examples.

  python tools/wiki_validate.py FILE.json [FILE2.json ...] --cli PATH/matlivre-cli.exe [--names NAMES.txt]

--names: text file, one function name per line; across all the files given, every name must be
present and no others (use it as the last check, with all your part files).
Exit code 0 only when the file is clean.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

BAD = re.compile('[–—‒―]')           # en/em dashes
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿]')


def run(cli, code):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'ex.m')
        open(p, 'w', encoding='utf-8', newline='\n').write(code + '\n')
        try:
            r = subprocess.run([cli, p], capture_output=True, timeout=60, cwd=d)
        except subprocess.TimeoutExpired:
            return 'TIMEOUT', True
        out = (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')).replace('\r\n', '\n').rstrip()
        return out, bool(re.search(r'^Error', out, re.M)) or r.returncode != 0


def main():
    a = sys.argv[1:]
    cli = names_file = None
    if '--cli' in a:
        i = a.index('--cli'); cli = a[i + 1]; del a[i:i + 2]
    if '--names' in a:
        i = a.index('--names'); names_file = a[i + 1]; del a[i:i + 2]
    path = ', '.join(a)
    errs, warns = [], []
    fns = {}
    for fp in a:
        try:
            data = json.load(open(fp, encoding='utf-8'))
        except Exception as ex:
            sys.exit(f'{fp}: invalid JSON: {ex}')
        f = data.get('functions')
        if not isinstance(f, dict):
            sys.exit(f'{fp}: missing "functions" object')
        for k in f:
            if k in fns:
                errs.append(f'{k}: defined twice')
        fns.update(f)

    if names_file:
        want = [l.rstrip('\r\n') for l in open(names_file, encoding='utf-8') if l.strip()]
        miss = [n for n in want if n not in fns]
        extra = [n for n in fns if n not in want]
        if miss:
            errs.append(f'missing functions ({len(miss)}): {miss[:30]}')
        if extra:
            errs.append(f'unexpected functions ({len(extra)}): {extra[:30]}')

    def bi(where, d, required=True):
        if not isinstance(d, dict):
            errs.append(f'{where}: expected {{"en":..., "pt":...}}'); return
        for k in ('en', 'pt'):
            v = d.get(k)
            if not isinstance(v, str) or not v.strip():
                if required:
                    errs.append(f'{where}.{k}: empty')
            else:
                if BAD.search(v):
                    errs.append(f'{where}.{k}: contains an en/em dash (use a comma, colon or period)')
                if EMOJI.search(v):
                    errs.append(f'{where}.{k}: contains an emoji')

    for name, e in fns.items():
        w = name
        if not isinstance(e, dict):
            errs.append(f'{w}: not an object'); continue
        bi(f'{w}.summary', e.get('summary'))
        s = (e.get('summary') or {})
        for k in ('en', 'pt'):
            if len(s.get(k, '')) > 170:
                warns.append(f'{w}.summary.{k}: long ({len(s[k])} chars)')
        syn = e.get('syntax')
        if not isinstance(syn, list) or not syn:
            errs.append(f'{w}.syntax: need at least one form')
        else:
            for n, x in enumerate(syn):
                if not x.get('code'):
                    errs.append(f'{w}.syntax[{n}].code empty')
                bi(f'{w}.syntax[{n}]', x)
        bi(f'{w}.description', e.get('description'))
        for key in ('inputs', 'outputs'):
            for n, x in enumerate(e.get(key) or []):
                if not x.get('name'):
                    errs.append(f'{w}.{key}[{n}].name empty')
                bi(f'{w}.{key}[{n}]', x)
        if e.get('notes'):
            bi(f'{w}.notes', e['notes'])
        exs = e.get('examples')
        if not isinstance(exs, list) or not exs:
            errs.append(f'{w}.examples: need at least one')
        else:
            for n, ex in enumerate(exs):
                code = ex.get('code', '')
                if not code.strip():
                    errs.append(f'{w}.examples[{n}].code empty'); continue
                if ex.get('title'):
                    bi(f'{w}.examples[{n}].title', ex['title'])
                if ex.get('note'):
                    bi(f'{w}.examples[{n}].note', ex['note'])
                if cli:
                    out, bad = run(cli, code)
                    if bad:
                        errs.append(f'{w}.examples[{n}] fails: {out[:160]!r}')
                    elif not out.strip() and not ex.get('silent'):
                        errs.append(f'{w}.examples[{n}] prints nothing: show a result (drop a semicolon or use disp) or set "silent": true for graphics')
        see = e.get('see') or []
        if not isinstance(see, list):
            errs.append(f'{w}.see: expected a list')
    print(f'{path}: {len(fns)} functions, {len(errs)} errors, {len(warns)} warnings')
    for x in warns[:20]:
        print('  warn:', x)
    for x in errs[:60]:
        print('  ERROR:', x)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
