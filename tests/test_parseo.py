"""Dimensión: todo el RDF del repo parsea (fuente y serializaciones publicadas)."""
import pytest
from rdflib import Graph

from util import ROOT, rdf_files, sniff_parse

FUENTES = rdf_files("ontology", "kos", "shapes", "examples", "mappings")
DOCS = [ROOT / "documentation" / n for n in ("ontology.ttl", "ontology.rdf", "ontology.jsonld", "ontology.nt", "ontology.owl")]
DOCS = [p for p in DOCS if p.exists()]


@pytest.mark.parametrize("path", FUENTES, ids=lambda p: str(p.relative_to(ROOT)))
def test_parsea_fuente(path):
    sniff_parse(path)


@pytest.mark.parametrize("path", DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_parsea_serializacion_publicada(path):
    suffix = path.suffix.lstrip(".")
    fmt = {"ttl": "turtle", "rdf": "xml", "owl": None, "jsonld": "json-ld", "nt": "nt"}[suffix]
    if fmt is None:
        sniff_parse(path)
    else:
        Graph().parse(str(path), format=fmt)
