"""Dimensión: las shapes citan términos que existen en el grafo local."""
import pytest
from rdflib import URIRef

from util import NS_DEF, sniff_parse

SH_TARGET = URIRef("http://www.w3.org/ns/shacl#targetClass")
SH_PATH = URIRef("http://www.w3.org/ns/shacl#path")


def test_sin_terminos_fantasma(ficheros_shapes, grafo_local, slug):
    if not ficheros_shapes:
        pytest.skip("sin shapes")
    fantasmas = set()
    for p in ficheros_shapes:
        try:
            g = sniff_parse(p)
        except Exception:
            continue
        for pred in (SH_TARGET, SH_PATH):
            for _, o in g.subject_objects(pred):
                if isinstance(o, URIRef) and str(o).startswith(NS_DEF + slug) and (o, None, None) not in grafo_local:
                    fantasmas.add(f"{p.name}: {pred.split('#')[-1]} -> {o}")
    assert not fantasmas, f"targetClass/path inexistentes localmente:\n  " + "\n  ".join(sorted(fantasmas))


def test_property_shapes_con_path(ficheros_shapes):
    if not ficheros_shapes:
        pytest.skip("sin shapes")
    from rdflib import RDF, URIRef
    SH_PS = URIRef("http://www.w3.org/ns/shacl#PropertyShape")
    SH_PATH = URIRef("http://www.w3.org/ns/shacl#path")
    mal = []
    for p in ficheros_shapes:
        try:
            g = sniff_parse(p)
        except Exception:
            continue
        for s in g.subjects(RDF.type, SH_PS):
            if not list(g.objects(s, SH_PATH)):
                mal.append(f"{p.name}: {s}")
    assert not mal, f"PropertyShape sin sh:path: {mal}"
