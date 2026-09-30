import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mdtoc

DOC = """# Title
<!-- toc -->
old
<!-- tocstop -->
## One
### Sub `code`
```
## not a heading
```
Two
---
## One
"""


def test_update_and_idempotent():
    new = mdtoc.update(DOC)
    assert '- [One](#one)' in new
    assert '  - [Sub `code`](#sub-code)' in new
    assert '- [Two](#two)' in new
    assert '- [One](#one-1)' in new
    assert 'not a heading' not in new.split('<!-- tocstop -->')[0]
    assert mdtoc.update(new) == new


def test_no_markers():
    assert mdtoc.update('# x\n') is None


def test_check(tmp_path):
    f = tmp_path / 'a.md'
    f.write_text(DOC)
    assert mdtoc.main(['--check', str(f)]) == 1
    assert mdtoc.main([str(f)]) == 0
    assert mdtoc.main(['--check', str(f)]) == 0
