"""Dimensión: declaración y metadatos de la ontología."""
import pytest
from rdflib import URIRef
from rdflib.namespace import OWL, RDF, RDFS

VANN = URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")
DCT_LICENSE = URIRef("http://purl.org/dc/terms/license")


@pytest.fixture(scope="module")
def ontologia(modelo):
    if modelo is None:
        pytest.skip("sin fichero de modelo")
    onts = list(modelo.subjects(RDF.type, OWL.Ontology))
    if len(onts) != 1:
        pytest.fail(f"{len(onts)} sujetos owl:Ontology (debe ser exactamente 1): {sorted(map(str, onts))}")
    return onts[0]


def test_prefijo_vann(modelo, ontologia):
    assert list(modelo.objects(ontologia, VANN)), "falta vann:preferredNamespacePrefix"


def test_version_iri(modelo, ontologia):
    assert list(modelo.objects(ontologia, OWL.versionIRI)), "falta owl:versionIRI"


def test_licencia(modelo, ontologia):
    assert list(modelo.objects(ontologia, DCT_LICENSE)), "falta dcterms:license"


def test_titulo(modelo, ontologia):
    assert list(modelo.objects(ontologia, RDFS.label)), "falta rdfs:label de la ontología"


def test_fechas_coherentes(modelo, ontologia):
    from rdflib import URIRef
    DCT = "http://purl.org/dc/terms/"
    fechas = {}
    for nombre in ("created", "issued", "modified"):
        v = next(modelo.objects(ontologia, URIRef(DCT + nombre)), None)
        assert v is not None, f"falta dcterms:{nombre}"
        fechas[nombre] = str(v)[:10]
    assert fechas["created"] <= fechas["issued"] <= fechas["modified"], (
        f"fechas incoherentes: {fechas}"
    )


@pytest.mark.usefixtures("root")
def test_ontology_bloque_unico_xml(root):
    """El fichero ontology.owl debe contener UN solo bloque <owl:Ontology>.

    Un segundo bloque (mismo rdf:about) es un artefacto de regeneración de
    Widoco: el grafo RDF lo fusiona y los tests semánticos no lo ven, pero
    corrompe la serialización y confunde a validadores y humanos."""
    owl = None
    for cand in ("ontology/ontology.owl", "documentation/ontology.owl"):
        p = root / cand
        if p.exists():
            owl = p
            break
    if owl is None:
        pytest.skip("sin ontology.owl")
    n = owl.read_text(errors="replace").count("<owl:Ontology")
    assert n == 1, f"{owl}: {n} bloques <owl:Ontology> (debe ser 1) — fusiona los metadatos en un único bloque"
