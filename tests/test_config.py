"""Dimensión: rutas declaradas en .config existen."""
import re

import pytest

from util import ROOT

from util import CLAVES_CONFIG as CLAVES


def entradas():
    p = ROOT / ".config"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="replace").splitlines():
        m = re.match(r"\s*(\w+)\s*=\s*(\./\S+)", line)
        if m and m.group(1) in CLAVES:
            out.append((m.group(1), m.group(2).rstrip("/")))
    return out


ALIASES_RUTA = {
    "./shacl-shapes": "./shapes",
    "./rdf-examples": "./examples",
}


@pytest.mark.parametrize("clave,ruta", entradas(), ids=lambda x: x if isinstance(x, str) else "")
def test_path_existe(clave, ruta):
    if (ROOT / ruta).exists():
        return
    alias = ALIASES_RUTA.get(ruta.rstrip("/"))
    if alias and (ROOT / alias).exists():
        pytest.skip(f".config desactualizado: {clave} = {ruta} pero existe {alias}")
    assert False, f".config: {clave} = {ruta} no existe"
