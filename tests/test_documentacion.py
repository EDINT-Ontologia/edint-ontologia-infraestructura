"""Dimensión: documentación completa y coherente con la fuente.

La lista de ficheros exigidos se deriva del propio workflow de deploy del
repo. La paridad es/en se mide sobre el texto visible (palabras), no sobre
el tamaño del HTML: el markup de Widoco domina el byte y falsea la señal.
"""
import re

import pytest
from rdflib import Graph
from rdflib.namespace import OWL, RDF

from util import PALABRAS_MINIMAS, PARIDAD_SECCIONES, ROOT


def _palabras(path) -> int:
    """Palabras de texto visible de un HTML (sin script/style ni etiquetas)."""
    html = path.read_text(errors="replace")
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return len(re.sub(r"(?s)<[^>]+>", " ", html).split())


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
        else:
            pe, pi = _palabras(es), _palabras(en)
            if max(pe, pi) < PALABRAS_MINIMAS:
                mal.append(f"sección sin contenido: {es.name} ({pe} palabras) / {en.name} ({pi} palabras)")
            elif min(pe, pi) / max(pe, pi) < PARIDAD_SECCIONES:
                mal.append(
                    f"secciones descuadradas: {es.name} ({pe} palabras) / {en.name} ({pi} palabras), "
                    f"la corta es {min(pe, pi) / max(pe, pi):.0%} de la larga"
                )
    assert not mal, "\n  ".join(mal)
