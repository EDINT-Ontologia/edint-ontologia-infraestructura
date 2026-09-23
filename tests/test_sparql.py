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
    # Los ficheros pueden contener varias consultas y declarar los PREFIX una
    # sola vez arriba: se separa por consulta y se antepone la cabecera.
    cabecera = "\n".join(re.findall(r"(?m)^\s*PREFIX\s+\S+\s*<[^>]+>\s*$", src))
    consultas = [c for c in re.split(r"(?m)^(?=SELECT|ASK|CONSTRUCT|DESCRIBE\b)", src)[1:]]
    if not consultas:
        pytest.fail("el fichero no contiene ninguna consulta")
    for consulta in consultas:
        prepareQuery(f"{cabecera}\n{consulta}")
    pytest.fail("alguna consulta del fichero no parsea")


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
