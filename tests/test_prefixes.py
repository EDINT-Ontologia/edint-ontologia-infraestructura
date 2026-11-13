"""Dimensión: prefijos Turtle/SPARQL usados, declarados y bien formados."""
import re

import pytest
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.algebra import translateQuery

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


PREFIJOS_ESTANDAR = {"rdf", "rdfs", "xsd", "owl", "xml", "skos"}


def _decls_fichero(path):
    """Declaraciones (alias, IRI) literalmente escritas en el fichero.

    Regex a propósito: rdflib colapsa las redeclaraciones del mismo alias
    (la última gana) y no permitiría ver lo que literalmente está escrito.
    """
    texto = path.read_text(errors="replace")
    return re.findall(r"(?:@prefix|PREFIX)\s+([A-Za-z][\w-]*)\s*:\s*<([^>]+)>", texto)


def _binds_efectivos_ttl(path):
    """Bindings Turtle según rdflib (semántica real del fichero)."""
    g = Graph()
    try:
        g.parse(path.as_posix(), format="turtle")
    except Exception:
        return {}  # ya lo reporta test_parseo
    por_defecto = dict(Graph().namespaces())
    out = {}
    for alias, uri in g.namespaces():
        a, u = str(alias), str(uri)
        if por_defecto.get(a) == u:
            continue  # binding por defecto de rdflib, no del fichero
        out[a] = u
    return out


def _binds_efectivos_sparql(path):
    """Bindings SPARQL según el parser de rdflib (prologue traducido)."""
    try:
        q = translateQuery(parseQuery(path.read_text(errors="replace")))
    except Exception:
        return {}  # ya lo reporta test_cobertura/parseo
    por_defecto = dict(Graph().namespaces())
    out = {}
    for alias, uri in q.prologue.namespace_manager.namespaces():
        a, u = str(alias), str(uri)
        if por_defecto.get(a) == u:
            continue
        out[a] = u
    return out


def _binds_efectivos(path):
    if path.suffix == ".ttl":
        return _binds_efectivos_ttl(path)
    return _binds_efectivos_sparql(path)


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_prefijos_usados_declarados(path):
    texto = path.read_text(errors="replace")
    declarados = extraer_prefijos(texto)
    usados = prefijos_usados(texto)
    sin_declarar = sorted(usados - set(declarados) - PREFIJOS_ESTANDAR)
    assert not sin_declarar, f"prefijos usados sin declarar: {sin_declarar}"


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_declaraciones_sin_repetir(path):
    """Dentro de un fichero no se repite ninguna declaración: ni el mismo
    alias declarado dos veces, ni la misma namespace bajo dos alias."""
    decls = _decls_fichero(path)
    alias = [a for a, _ in decls]
    iris = [i for _, i in decls]
    alias_rep = sorted({a for a in alias if alias.count(a) > 1})
    ns_rep = sorted({i for i in iris if iris.count(i) > 1})
    assert not alias_rep, f"alias declarados más de una vez: {alias_rep}"
    assert not ns_rep, f"namespaces declaradas bajo varios alias: {ns_rep}"


def test_prefijo_unico_por_namespace_repo():
    """En el repositorio, una misma namespace no debe declararse bajo
    prefijos distintos en ficheros diferentes (p. ej., dct: en un mapping
    y dcterms: en otro para http://purl.org/dc/terms/)."""
    por_ns: dict[str, dict[str, list[str]]] = {}
    for path in ficheros():
        for alias, uri in _binds_efectivos(path).items():
            por_ns.setdefault(uri, {}).setdefault(alias, []).append(str(path.relative_to(ROOT)))
    conflictos = {
        uri: {alias: paths[:3] for alias, paths in als.items()}
        for uri, als in por_ns.items() if len(als) > 1
    }
    assert not conflictos, f"namespaces con varios prefijos en el repo: {conflictos}"


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_prefijos_edint_bien_formados(path):
    texto = path.read_text(errors="replace")
    for alias, uri in extraer_prefijos(texto).items():
        if uri.startswith(NS_DEF):
            assert uri.endswith("#"), f"prefijo {alias}: {uri} debe acabar en #"
