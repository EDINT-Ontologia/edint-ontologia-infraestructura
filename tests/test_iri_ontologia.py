"""Dimensión: IRI y versionIRI de la ontología bien formados y coherentes con el README."""
import re

import pytest
from rdflib import URIRef
from rdflib.namespace import OWL, RDF

from util import NS_DEF, PREFIJO_REGEX, ROOT

VANN = URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")


@pytest.fixture(scope="module")
def iri_ontologia(modelo):
    if modelo is None:
        pytest.skip("sin fichero de modelo")
    onts = list(modelo.subjects(RDF.type, OWL.Ontology))
    if len(onts) != 1:
        pytest.skip("bloque owl:Ontology anómalo (lo reporta test_ontologia)")
    return str(onts[0])


def test_iri_sin_almohadilla(iri_ontologia):
    assert not iri_ontologia.endswith("#"), f"el IRI termina en #: {iri_ontologia}"


def test_namespace_del_repo(iri_ontologia, slug):
    if not iri_ontologia.startswith(NS_DEF):
        pytest.skip("namespace externo (p. ej. SEGITTUR)")
    assert iri_ontologia == f"{NS_DEF}{slug}", (
        f"IRI {iri_ontologia} != edint.es/def/{slug} derivado del nombre del repo"
    )


def test_version_iri_semver(modelo):
    if modelo is None:
        pytest.skip("sin fichero de modelo")
    vis = [str(v) for v in modelo.objects(None, OWL.versionIRI)]
    assert vis, "falta owl:versionIRI"
    for vi in vis:
        assert re.fullmatch(r"https://edint\.es/def/[a-z0-9-]+/\d+\.\d+\.\d+", vi), (
            f"versionIRI mal formado: {vi}"
        )


def test_prefijo_coherente_con_readme(modelo, iri_ontologia):
    readme = modelo and None
    p = ROOT / "README.md"
    if not p.exists():
        pytest.skip("sin README")
    vann = [str(v) for v in modelo.objects(None, VANN)]
    assert vann, "falta vann:preferredNamespacePrefix"
    texto = p.read_text(errors="replace")
    citados = re.findall(r"prefijo[^.`\n]*?`([a-z][a-z0-9]+)`", texto, re.I)
    assert citados, "el README no documenta el prefijo (frase: el prefijo de esta ontología es `X`)"
    assert vann[0] in citados, f"prefijo del OWL ({vann[0]}) != prefijo citado en el README ({citados})"
    if iri_ontologia.startswith("https://edint.es/"):
        assert re.fullmatch(PREFIJO_REGEX, vann[0]), f"prefijo no convencional: {vann[0]}"
