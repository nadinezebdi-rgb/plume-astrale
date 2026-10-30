#!/usr/bin/env python3
"""eslint_quickfix — Nettoie 2 patterns ESLint ultra-répétitifs sur frontend/src :

  1. `import React[, ...]` quand React n'est pas référencé dans le fichier
     (JSX transform auto en React 17+).
  2. `catch (e) { ... }` où `e` n'est pas utilisé → renomme en `catch (_e)` pour
     respecter l'option `caughtErrorsIgnorePattern: '^_'`.

Usage :
    python scripts/eslint_quickfix.py        # dry-run : liste
    python scripts/eslint_quickfix.py --apply
"""
import os
import re
import sys
from pathlib import Path

SRC = Path('/app/frontend/src')
APPLY = '--apply' in sys.argv

RE_IMPORT_REACT_ONLY = re.compile(r"^import React from ['\"]react['\"];?\s*\n", re.M)
RE_IMPORT_REACT_WITH = re.compile(r"^import React,\s*\{(.+?)\} from ['\"]react['\"];?\s*\n", re.M)
RE_IMPORT_REACT_STAR = re.compile(r"^import \* as React from ['\"]react['\"];?\s*\n", re.M)
RE_CATCH_E = re.compile(r"catch\s*\(\s*e\s*\)\s*\{")
RE_CATCH_ERR = re.compile(r"catch\s*\(\s*err\s*\)\s*\{")

# Si on voit React.X ou JSX pragma, on garde l'import
RE_REACT_USAGE = re.compile(r"\bReact\.")

changed = []
for js in list(SRC.rglob('*.js')) + list(SRC.rglob('*.jsx')):
    txt = js.read_text(encoding='utf-8')
    orig = txt

    # 1a) import React from 'react' seul, et pas d'usage React.X
    if RE_IMPORT_REACT_ONLY.search(txt) and not RE_REACT_USAGE.search(txt):
        txt = RE_IMPORT_REACT_ONLY.sub('', txt, count=1)

    # 1b) import React, { ... } from 'react' et pas d'usage React.X
    m = RE_IMPORT_REACT_WITH.search(txt)
    if m and not RE_REACT_USAGE.search(txt):
        inside = m.group(1).strip()
        txt = RE_IMPORT_REACT_WITH.sub(f"import {{{inside}}} from 'react';\n", txt, count=1)

    # 1c) import * as React from 'react' et pas d'usage → remove
    if RE_IMPORT_REACT_STAR.search(txt) and not RE_REACT_USAGE.search(txt):
        txt = RE_IMPORT_REACT_STAR.sub('', txt, count=1)

    # 2) catch (e) → catch (_e) si `e` n'est pas référencé dans les 400 car qui suivent
    def _patch_catch(match, var='e'):
        start = match.end()
        snippet = txt[start:start + 500]
        # Trouve la fin du bloc { ... } naïvement
        depth = 1
        i = 0
        while i < len(snippet) and depth > 0:
            if snippet[i] == '{': depth += 1
            elif snippet[i] == '}': depth -= 1
            i += 1
        block = snippet[:i]
        # Si `e` ou `err` n'apparaît pas dans ce bloc comme identifiant, on peut renommer
        if re.search(rf'\b{var}\b', block):
            return match.group(0)
        return match.group(0).replace(f'({var})', f'(_{var})').replace(f'( {var})', f'(_{var})')

    # Catch e
    new_txt = []
    pos = 0
    for m2 in RE_CATCH_E.finditer(txt):
        new_txt.append(txt[pos:m2.start()])
        start = m2.end()
        snippet = txt[start:start + 500]
        depth = 1
        i = 0
        while i < len(snippet) and depth > 0:
            if snippet[i] == '{': depth += 1
            elif snippet[i] == '}': depth -= 1
            i += 1
        block = snippet[:i]
        if re.search(r'\be\b', block):
            new_txt.append(m2.group(0))
        else:
            new_txt.append(m2.group(0).replace('(e)', '(_e)').replace('( e )', '(_e)').replace('( e)', '(_e)').replace('(e )', '(_e)'))
        pos = m2.end()
    new_txt.append(txt[pos:])
    txt = ''.join(new_txt)

    # Catch err
    new_txt = []
    pos = 0
    for m2 in RE_CATCH_ERR.finditer(txt):
        new_txt.append(txt[pos:m2.start()])
        start = m2.end()
        snippet = txt[start:start + 500]
        depth = 1
        i = 0
        while i < len(snippet) and depth > 0:
            if snippet[i] == '{': depth += 1
            elif snippet[i] == '}': depth -= 1
            i += 1
        block = snippet[:i]
        if re.search(r'\berr\b', block):
            new_txt.append(m2.group(0))
        else:
            new_txt.append(m2.group(0).replace('(err)', '(_err)'))
        pos = m2.end()
    new_txt.append(txt[pos:])
    txt = ''.join(new_txt)

    if txt != orig:
        changed.append(js)
        if APPLY:
            js.write_text(txt, encoding='utf-8')

print(f'{len(changed)} fichiers {"modifiés" if APPLY else "à modifier"}')
for f in changed[:50]:
    print(f'  {f.relative_to(SRC.parent)}')
if len(changed) > 50:
    print(f'  … et {len(changed) - 50} autres')
