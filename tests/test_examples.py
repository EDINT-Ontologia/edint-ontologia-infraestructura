"""Dimensión: los ejemplos usan IRIs de instancia estándar y predicados válidos."""
import pytest

from util import INSTANCIAS_EJEMPLO, NS_DEF
from rdflib import URIRef
from rdflib.namespace import OWL, RDF

PROPS = {OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDF.Property}


def test_instancias_bajo_example_org(grafo_ejemplos):
    if grafo_ejemplos is None or not len(grafo_ejemplos):
        pytest.skip("sin ejemplos")
    mal = set()
    for s in grafo_ejemplos.subjects(RDF.type, None):
        if isinstance(s, URIRef) and not str(s).startswith("https://edint.es/"):
            if not str(s).startswith(INSTANCIAS_EJEMPLO):
                mal.add(str(s))
    assert not mal, (
        "sujetos de instancia fuera de example.org:\n  " + "\n  ".join(sorted(mal)[:15])
    )


def test_predicados_propios_son_propiedades(grafo_ejemplos, grafo_local, slug):
    if grafo_ejemplos is None or not len(grafo_ejemplos):
        pytest.skip("sin ejemplos")
    propia = f"{NS_DEF}{slug}"
    mal = set()
    for p in set(grafo_ejemplos.predicates()):
        if isinstance(p, URIRef) and str(p).startswith(propia):
            tipos = set(grafo_ejemplos.objects(p, RDF.type)) | set(grafo_local.objects(p, RDF.type))
            if not tipos & PROPS:
                mal.add(f"{p} (tipos: {sorted(map(str, tipos)) or 'sin declarar'})")
    assert not mal, (
        "predicados del namespace propio que no son propiedades:\n  "
        + "\n  ".join(sorted(mal))
    )
