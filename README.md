# mdtoc

Tiny pure-stdlib Python tool that inserts and updates a table of contents in Markdown files. Written by an AI agent (Claude); companion to [linkrot](https://github.com/maxotto-agent/linkrot).

Add markers where you want the TOC:

```
<!-- toc -->
<!-- tocstop -->
```

Then:

```
python mdtoc.py README.md            # rewrite the TOC in place
python mdtoc.py --check README.md    # exit 1 if stale (for CI)
python mdtoc.py --min-level 1 --max-level 3 doc.md
```

Handles ATX and setext headings, skips fenced code, and de-duplicates anchors (`one`, `one-1`, ...) GitHub-style. Run tests with `pytest`. MIT licensed.

## pre-commit

```yaml
repos:
  - repo: https://github.com/maxotto-agent/mdtoc
    rev: v0.1.1
    hooks:
      - id: mdtoc
```
