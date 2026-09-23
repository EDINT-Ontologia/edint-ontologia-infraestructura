"""Dimensión: enlaces relativos del README existen en el repo."""
import re

import pytest

from util import ROOT


def enlaces():
    p = ROOT / "README.md"
    if not p.exists():
        return []
    out = []
    for m in re.finditer(r"\]\(([^)#?]+)(?:#[^)]*)?\)", p.read_text(errors="replace")):
        rel = m.group(1).strip()
        if not rel.startswith(("http://", "https://", "mailto:")):
            out.append(rel)
    return out


@pytest.mark.parametrize("rel", enlaces(), ids=lambda r: r)
def test_enlace_existe(rel):
    assert (ROOT / rel).exists(), f"enlace roto en README: {rel}"
