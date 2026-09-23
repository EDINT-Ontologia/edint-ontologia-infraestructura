"""Fixtures de sesión: cada grafo se carga una sola vez para toda la suite."""
from pathlib import Path

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

from util import ROOT, model_path, rdf_files, sniff_parse


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def path_modelo() -> Path | None:
    return model_path()


@pytest.fixture(scope="session")
def modelo(path_modelo) -> Graph | None:
    if path_modelo is None:
        return None
    return sniff_parse(path_modelo)


@pytest.fixture(scope="session")
def ns_propia(modelo) -> str | None:
    if modelo is None:
        return None
    for s in modelo.subjects(RDF.type, OWL.Ontology):
        return str(s)
    return None


@pytest.fixture(scope="session")
def grafos_kos() -> list[Graph]:
    out = []
    for p in rdf_files("kos"):
        try:
            out.append(sniff_parse(p))
        except Exception:
            pass  # ya lo reporta test_parseo
    return out


@pytest.fixture(scope="session")
def ficheros_shapes() -> list[Path]:
    d = ROOT / "shapes"
    return sorted(d.glob("*.ttl")) if d.is_dir() else []


@pytest.fixture(scope="session")
def grafo_local(modelo, grafos_kos) -> Graph:
    """Ontología + KOS del repo: para resolver términos citados."""
    g = Graph()
    if modelo:
        for t in modelo:
            g.add(t)
    for k in grafos_kos:
        for t in k:
            g.add(t)
    return g


@pytest.fixture(scope="session")
def datos_ejemplos(modelo) -> Graph | None:
    files = rdf_files("examples")
    if not files or modelo is None:
        return None
    g = Graph()
    for t in modelo:
        g.add(t)
    for p in files:
        try:
            sniff_parse(p, g)
        except Exception:
            pass
    return g


@pytest.fixture(scope="session")
def slug() -> str:
    from util import repo_slug
    return repo_slug()


@pytest.fixture(scope="session")
def grafo_ejemplos() -> Graph | None:
    files = rdf_files("examples")
    if not files:
        return None
    g = Graph()
    for p in files:
        try:
            sniff_parse(p, g)
        except Exception:
            pass
    return g
