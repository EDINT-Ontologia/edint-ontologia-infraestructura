"""Dimensión: las consultas de requirements parsean y citan términos existentes."""
import re

import pytest
from rdflib import URIRef
from rdflib.plugins.sparql import prepareQuery

from util import ROOT, extraer_prefijos, prefijos_usados, NS_DEF


RE_CONSULTA = re.compile(r"(?m)^\s*(SELECT|ASK|CONSTRUCT|DESCRIBE)\b")
RE_PREFIX = re.compile(r"(?m)^\s*PREFIX\s+\S+\s*<[^>]+>\s*$")


def separar_consultas(src: str) -> list[str]:
    """Una entrada por consulta del fichero, con sus PREFIX disponibles.

    Corta en consultas de nivel superior (SELECT/ASK/CONSTRUCT/DESCRIBE en
    columna 0); los sub-SELECT indentados no se separan. Los PREFIX pueden
    estar declarados una sola vez arriba o repetidos entre consultas: se
    deduplican conservando el orden.
    """
    vistos: set[str] = set()
    cabecera = "\n".join(
        p for p in RE_PREFIX.findall(src)
        if not (p in vistos or vistos.add(p))
    )
    posiciones = [m.start() for m in re.finditer(r"(?m)^(SELECT|ASK|CONSTRUCT|DESCRIBE)\b", src)]
    if not posiciones:
        return []
    trozos = [
        src[a:b] for a, b in zip(posiciones, posiciones[1:] + [len(src)])
    ]
    return [f"{cabecera}\n\n{trozo}" for trozo in trozos]


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
    consultas = separar_consultas(src)
    if not consultas:
        pytest.fail("el fichero no contiene ninguna consulta")
    for consulta in consultas:
        prepareQuery(consulta)


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
