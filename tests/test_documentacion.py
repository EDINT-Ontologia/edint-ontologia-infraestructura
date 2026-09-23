"""Dimensión: documentación completa y coherente con la fuente.

La lista de ficheros exigidos se deriva del propio workflow de deploy del
repo (test -s documentation/...), no de una lista fija.
"""
import re

import pytest
from rdflib import Graph
from rdflib.namespace import OWL, RDF

from util import ROOT, sniff_parse, UMBRAL_SECCION_BYTES


def ficheros_del_deploy():
    for yml in sorted((ROOT / ".github" / "workflows").glob("*.yml")) if (ROOT / ".github" / "workflows").is_dir() else []:
        encontrados = re.findall(
            r"documentation/([A-Za-z0-9_.\-]+\.(?:html|rdf|ttl|jsonld|nt))",
            yml.read_text(errors="replace"),
        )
        if encontrados:
            return sorted(set(encontrados))
    return None


def test_ficheros_que_exige_el_deploy(path_modelo):
    if path_modelo is None:
        pytest.skip("sin fichero de modelo")
    exigidos = ficheros_del_deploy()
    if not exigidos:
        pytest.skip("el repo no declara ficheros de documentation/ en su workflow")
    faltan = [f for f in exigidos if not (ROOT / "documentation" / f).exists()]
    assert not faltan, f"faltan en documentation/ (el deploy aborta): {faltan}"


def test_iri_publicado_igual_a_fuente(path_modelo, modelo):
    ttl = ROOT / "documentation" / "ontology.ttl"
    if path_modelo is None or not ttl.exists():
        pytest.skip("sin serialización publicada")
    publicado = Graph().parse(str(ttl), format="turtle")
    iri_pub = next(publicado.subjects(RDF.type, OWL.Ontology), None)
    iri_fuente = next(modelo.subjects(RDF.type, OWL.Ontology), None)
    assert iri_pub is not None, "la serialización publicada no declara owl:Ontology"
    assert str(iri_pub) == str(iri_fuente), (
        f"deriva de serialización: publicado {iri_pub} != fuente {iri_fuente}"
    )


def test_secciones_es_en_parejadas():
    sec = ROOT / "documentation" / "sections"
    if not sec.is_dir():
        pytest.skip("sin sections/")
    mal = []
    for es in sorted(sec.glob("*-es.html")):
        en = es.with_name(es.name.replace("-es.html", "-en.html"))
        if not en.exists():
            mal.append(f"sin pareja -en: {es.name}")
        elif en.stat().st_size < UMBRAL_SECCION_BYTES or es.stat().st_size < UMBRAL_SECCION_BYTES:
            mal.append(f"pareja casi vacía: {es.name} ({es.stat().st_size}B) / {en.name} ({en.stat().st_size}B)")
    assert not mal, "\n  ".join(mal)
