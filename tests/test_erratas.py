"""Dimensión: sin erratas conocidas (diccionario de incidentes reales)."""
import re

import pytest

from util import ERRATAS, ROOT


def objetivos():
    out = []
    for d, pat in (("kos", "*.ttl"), ("diagrams", "*.xml")):
        base = ROOT / d
        if base.is_dir():
            out += sorted(base.glob(pat))
    for d in ("ontology",):
        base = ROOT / d
        if base.is_dir():
            out += sorted(base.glob("*.owl"))
    readme = ROOT / "README.md"
    if readme.exists():
        out.append(readme)
    return out


@pytest.mark.parametrize("path", objetivos(), ids=lambda p: str(p.relative_to(ROOT)))
def test_sin_erratas(path):
    texto = path.read_text(errors="replace")
    encontradas = [e for e in ERRATAS if re.search(e, texto)]
    assert not encontradas, f"erratas: {encontradas}"
