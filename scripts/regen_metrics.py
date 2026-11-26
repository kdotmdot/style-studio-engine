"""Regenerate every shipped metrics file (src/engine/metrics/*.json) with scripts/font_metrics.py's character set.

Refuses to write a file if any value that was already there would change: a regeneration may only add characters.
Run: python3 scripts/regen_metrics.py [--check]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import font_metrics as FM  # noqa: E402

# metrics key -> (weight key, font file under public/, wght for a variable font or '')
SHIPPED = {
    'anton': ('400', 'fonts/volt/Anton-Regular.woff2', '400'),
    'archivo-black': ('400', 'fonts/pop/ArchivoBlack-Regular.ttf', ''),
    'caveat-400': ('400', 'fonts/sketch/Caveat-400.woff2', '400'),
    'caveat-700': ('700', 'fonts/sketch/Caveat-700.woff2', '700'),
    'eb-garamond-400': ('400', 'fonts/ledger/EBGaramond-400.woff2', '400'),
    'eb-garamond-700': ('700', 'fonts/ledger/EBGaramond-700.woff2', '700'),
    'inter-500': ('500', 'fonts/volt/Inter-500.woff2', '500'),
    'inter-600-italic': ('600', 'fonts/volt/Inter-600-Italic.woff2', '600'),
    'inter-700': ('700', 'fonts/volt/Inter-700.woff2', '700'),
    'inter-900': ('900', 'fonts/volt/Inter-900.woff2', '900'),
    'jetbrains-mono': ('400', 'fonts/shared/JetBrainsMono-400.woff2', '400'),
    'newsreader': ('400', 'fonts/ledger/Newsreader-Variable.woff2', '400'),
    'sora-400': ('400', 'fonts/glass/Sora-400.woff2', '400'),
    'sora-700': ('700', 'fonts/glass/Sora-700.woff2', '700'),
    'space-grotesk-400': ('400', 'fonts/pop/SpaceGrotesk-400.woff2', '400'),
    'space-grotesk-700': ('700', 'fonts/pop/SpaceGrotesk-700.woff2', '700'),
    'virgil': ('400', 'fonts/sketch/Virgil-Regular.woff2', ''),
    'vt323': ('400', 'fonts/terminal/VT323-Regular.woff2', ''),
}


def build(weight, path, wght):
    font = FM.load(f"{path}@{wght}" if wght else path)
    upm = font['head'].unitsPerEm
    os2 = font['OS/2']
    return {weight: {'advance': FM.advances(font), 'kern': {}},
            'capHeight': round(getattr(os2, 'sCapHeight', 0) / upm, 4), 'xHeight': round(getattr(os2, 'sxHeight', 0) / upm, 4),
            'ascent': round(font['hhea'].ascent / upm, 4), 'descent': round(-font['hhea'].descent / upm, 4)}


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the engine folder
    check = '--check' in sys.argv
    bad = []
    for key, (weight, file, wght) in SHIPPED.items():
        dest = os.path.join('src', 'engine', 'metrics', f'{key}.json')
        old = json.load(open(dest, encoding='utf8'))
        new = build(weight, os.path.join('public', file), wght)
        changed = [k for k in ('capHeight', 'xHeight', 'ascent', 'descent') if old.get(k) != new[k]]
        changed += [c for c, v in old[weight]['advance'].items() if new[weight]['advance'].get(c) != v]
        added = sorted(set(new[weight]['advance']) - set(old[weight]['advance']))
        missing = [c for c in FM.SPANISH if c not in new[weight]['advance']]
        if changed:
            bad.append(f'{key}: would change {changed[:8]}')
            continue
        print(f"{key}: +{len(added)} characters{' (the face has no ' + ''.join(missing) + ')' if missing else ''}")
        if not check:
            with open(dest, 'w', encoding='utf8') as f:
                json.dump(new, f, ensure_ascii=False, indent=1)
    if bad:
        sys.exit('refused:\n  ' + '\n  '.join(bad))


if __name__ == '__main__':
    main()
