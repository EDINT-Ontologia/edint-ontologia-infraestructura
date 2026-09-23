"""Dimensión: las consultas de requirements parsean (enteras o por bloques PREFIX)."""
import re

import pytest
from rdflib.plugins.sparql import prepareQuery

from util import ROOT


def ficheros():
    d = ROOT / "requirements"
    return sorted(d.rglob("*.sparql")) if d.is_dir() else []


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_consulta_parsea(path):
    src = path.read_text(errors="replace")
    try:
        prepareQuery(src)
        return
    except Exception:
        pass
    for bloque in [b for b in re.split(r"(?m)^(?=PREFIX\s+\S+\s*<)", src) if b.strip()]:
        prepareQuery(bloque)  # si algún bloque falla, la aserción de abajo no se alcanza
    pytest.fail("no parsea ni entera ni por bloques PREFIX")
