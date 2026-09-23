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
