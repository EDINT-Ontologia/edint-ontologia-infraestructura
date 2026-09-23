"""Dimensión: esquemas SKOS citados y declarados."""
from rdflib import URIRef

SKOS = "http://www.w3.org/2004/02/skos/core#"
IN_SCHEME = URIRef(SKOS + "inScheme")
CONCEPT_SCHEME = URIRef(SKOS + "ConceptScheme")


def test_esquemas_citados_declarados(grafos_kos):
    if not grafos_kos:
        pytest.skip("sin KOS")
    declarados = {str(s) for g in grafos_kos for s in g.subjects(None, CONCEPT_SCHEME)}
    citados = {str(o) for g in grafos_kos for o in g.objects(None, IN_SCHEME) if isinstance(o, URIRef)}
    sin_declarar = sorted(citados - declarados)
    assert not sin_declarar, f"esquemas citados vía skos:inScheme sin declarar: {sin_declarar}"
