"""Dimensión: las consultas de requirements parsean y citan términos existentes."""
import re

import pytest
from rdflib import URIRef
from rdflib.plugins.sparql import prepareQuery

from util import ROOT, extraer_prefijos, prefijos_usados, NS_DEF


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
    consultas = [
        b for b in re.split(r"(?m)^(?=PREFIX\s+\S+\s*<)", src)
        if re.search(r"(?m)^\s*(SELECT|ASK|CONSTRUCT|DESCRIBE)\b", b)
    ]
    if not consultas:
        pytest.fail("el fichero no contiene ninguna consulta")
    for bloque in consultas:
        prepareQuery(bloque)
    pytest.fail("no parsea ni entera ni por bloques PREFIX")


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_terminos_citados_existen(path, grafo_local, slug):
    src = path.read_text(errors="replace")
    propia = f"{NS_DEF}{slug}#"
    prefijos = extraer_prefijos(src)
    mal = []
    for alias in prefijos_usados(src) & set(prefijos):
        for m in re.finditer(rf"\b{re.escape(alias)}:([A-Za-z_][\w.-]*)", src):
            iri = URIRef(prefijos[alias] + m.group(1))
            if str(iri).startswith(propia) and (iri, None, None) not in grafo_local:
                mal.append(f"{alias}:{m.group(1)}")
    assert not mal, f"términos del namespace propio citados y no declarados: {sorted(set(mal))[:10]}"
