"""Dimensión: prefijos Turtle/SPARQL usados, declarados y bien formados."""
import re

import pytest

from util import ROOT, extraer_prefijos, prefijos_usados, NS_DEF


def ficheros():
    out = []
    for d in ("kos", "shapes", "examples", "mappings"):
        base = ROOT / d
        if base.is_dir():
            out += [p for p in sorted(base.rglob("*.ttl")) if "mapping_doc" not in p.parts]
    req = ROOT / "requirements"
    if req.is_dir():
        out += sorted(req.rglob("*.sparql"))
    return out


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_prefijos_usados_declarados(path):
    texto = path.read_text(errors="replace")
    declarados = extraer_prefijos(texto)
    usados = prefijos_usados(texto)
    sin_declarar = sorted(usados - set(declarados))
    assert not sin_declarar, f"prefijos usados sin declarar: {sin_declarar}"


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_prefijos_sin_duplicar(path):
    if path.suffix == ".sparql":
        pytest.skip("los ficheros multi-consulta repiten PREFIX por consulta")
    texto = path.read_text(errors="replace")
    decl = re.findall(r"(?:@prefix|PREFIX)\s+([A-Za-z][\w-]*)\s*:\s*<([^>]+)>", texto)
    alias = [a for a, _ in decl]
    duplicados = sorted({a for a in alias if alias.count(a) > 1})
    assert not duplicados, f"alias declarados más de una vez: {duplicados}"


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_prefijos_edint_bien_formados(path):
    texto = path.read_text(errors="replace")
    for alias, uri in extraer_prefijos(texto).items():
        if uri.startswith(NS_DEF):
            assert uri.endswith("#"), f"prefijo {alias}: {uri} debe acabar en #"
