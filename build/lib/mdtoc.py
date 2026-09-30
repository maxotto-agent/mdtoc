#!/usr/bin/env python3
"""mdtoc: insert or update a table of contents in Markdown files.

Put markers in the file:
    <!-- toc -->
    <!-- tocstop -->
and run `mdtoc FILE` (rewrite) or `mdtoc --check FILE` (exit 1 if stale).
"""
import argparse
import re
import sys

START, END = '<!-- toc -->', '<!-- tocstop -->'
FENCE = re.compile(r'^\s{0,3}(```|~~~)')
ATX = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$')
SETEXT = re.compile(r'^ {0,3}(=+|-+)[ \t]*$')


def slug(text):
    text = re.sub(r'[`*_]', '', text.strip().lower())
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')


def plain(text):
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    return text


def headings(lines):
    """Yield (level, text) skipping fenced code and the TOC block."""
    fenced = False
    in_toc = False
    prev = None
    for line in lines:
        if line.strip() == START:
            in_toc = True
        if in_toc:
            if line.strip() == END:
                in_toc = False
            prev = None
            continue
        if FENCE.match(line):
            fenced = not fenced
            prev = None
            continue
        if fenced:
            continue
        m = ATX.match(line)
        if m:
            yield len(m.group(1)), m.group(2)
            prev = None
            continue
        m = SETEXT.match(line)
        if m and prev and prev.strip() and not ATX.match(prev):
            yield (1 if m.group(1)[0] == '=' else 2), prev.strip()
            prev = None
            continue
        prev = line


def build_toc(lines, min_level=2, max_level=4):
    seen = {}
    out = []
    items = [(l, t) for l, t in headings(lines)]
    # slugs must count every heading, including ones outside the level range
    for level, text in items:
        s = slug(plain(text))
        n = seen.get(s, 0)
        seen[s] = n + 1
        if min_level <= level <= max_level:
            anchor = s if n == 0 else f'{s}-{n}'
            out.append(f"{'  ' * (level - min_level)}- [{plain(text)}](#{anchor})")
    return out


def update(text, min_level=2, max_level=4):
    lines = text.split('\n')
    try:
        a = next(i for i, l in enumerate(lines) if l.strip() == START)
        b = next(i for i, l in enumerate(lines) if i > a and l.strip() == END)
    except StopIteration:
        return None
    toc = build_toc(lines, min_level, max_level)
    return '\n'.join(lines[:a + 1] + [''] + toc + [''] + lines[b:])


def main(argv=None):
    p = argparse.ArgumentParser(prog='mdtoc', description=__doc__.split('\n')[0])
    p.add_argument('files', nargs='*', help="files to process; with none, filter stdin to stdout")
    p.add_argument('--check', action='store_true', help='exit 1 if any TOC is stale')
    p.add_argument('--min-level', type=int, default=2)
    p.add_argument('--max-level', type=int, default=4)
    a = p.parse_args(argv)
    rc = 0
    if not a.files:
        old = sys.stdin.read()
        new = update(old, a.min_level, a.max_level)
        if new is None:
            print(f'stdin: no {START} / {END} markers', file=sys.stderr)
            return 2
        sys.stdout.write(new)
        return 0
    for f in a.files:
        old = open(f, encoding='utf-8').read()
        new = update(old, a.min_level, a.max_level)
        if new is None:
            print(f'{f}: no {START} / {END} markers', file=sys.stderr)
            rc = 2
        elif new != old:
            if a.check:
                print(f'{f}: TOC out of date')
                rc = rc or 1
            else:
                open(f, 'w', encoding='utf-8').write(new)
                print(f'{f}: updated')
    return rc


if __name__ == '__main__':
    sys.exit(main())
