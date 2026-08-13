#!/usr/bin/env python3
"""Audit lexical Phase 3 · repositionnement Plume Astrale.

Recense toutes les occurrences des mots à bannir dans le code frontend
et propose des remplacements. Ne modifie RIEN — c'est un scan diagnostic.
"""
import re
from pathlib import Path
from collections import defaultdict

FRONTEND = Path('/app/frontend/src')

# Mots à bannir (avec variantes de casse et morphologie)
BANNED = {
    'destin':      r'\bdestin(s|ée|ées|é|és)?\b',
    'magie':       r'\bmagi(e|es|que|ques|quement)\b',
    'prédiction':  r'\bprédiction(s)?\b|\bprédire\b|\bprédisent\b',
    'voyance':     r'\bvoyance\b|\bvoyant(e|s|es)?\b',
    'pouvoirs':    r'\bpouvoirs?\b(?!\s+(de\s+|d\'|dire|faire|voir|décider))',  # évite les "pouvoir de faire", "pouvoir décider"
    'révélation':  r'\brévélation(s)?\b|\brévèle(nt|s|r)?\b|\brévéler\b',
    'oracle':      r'\boracle(s)?\b',
    'esotérique':  r'\bésotéri(que|ques|sme)\b',
    'mystique':    r'\bmystique(s)?\b|\bmysticisme\b',
    'occulte':     r'\bocculte(s)?\b|\boccultisme\b',
}

# Extensions à scanner
EXTS = {'.js', '.jsx', '.ts', '.tsx', '.md', '.json'}
SKIP_DIRS = {'node_modules', 'build', 'dist', '.git'}

def scan():
    hits = defaultdict(list)  # {banned_key: [(file, line_num, line_text), ...]}
    for p in FRONTEND.rglob('*'):
        if not p.is_file() or p.suffix not in EXTS: continue
        if any(part in SKIP_DIRS for part in p.parts): continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            for key, pattern in BANNED.items():
                # Case-insensitive
                if re.search(pattern, line, re.IGNORECASE):
                    hits[key].append((str(p.relative_to(FRONTEND)), i, line.strip()[:180]))
    return hits

def report(hits):
    print('═══ AUDIT LEXICAL · PHASE 3 REPOSITIONNEMENT ═══\n')
    total = 0
    for key in BANNED.keys():
        occ = hits.get(key, [])
        if not occ: continue
        print(f"### {key.upper()} ({len(occ)} occurrences)")
        for f, ln, snippet in occ[:12]:  # top 12
            print(f"  {f}:{ln}")
            print(f"    → {snippet[:150]}")
        if len(occ) > 12:
            print(f"  ... et {len(occ) - 12} autres")
        print()
        total += len(occ)
    print(f'TOTAL : {total} occurrences réparties sur {len(hits)} termes.')

    # Résumé par fichier
    per_file = defaultdict(int)
    for occ_list in hits.values():
        for f, _, _ in occ_list:
            per_file[f] += 1
    print('\nTop fichiers impactés :')
    for f, n in sorted(per_file.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:>3} · {f}")

if __name__ == '__main__':
    report(scan())
