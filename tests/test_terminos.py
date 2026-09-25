"""Dimensión: IRIs del propio namespace usados en posiciones estructurales existen.

Los términos de OTROS repos EDINT no se pueden validar sin red ni datos
externos: eso queda para el job org-level. Aquí: todo IRI del namespace
propio usado como clase/propiedad/objetivo estructural debe estar declarado
en algún fichero local del repo.
"""
import pytest

from util import NS_DEF
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS

SH = "http://www.w3.org/ns/shacl#"


def test_terminos_propios_definidos(grafo_local, grafo_ejemplos, slug):
    propia = f"{NS_DEF}{slug}"
    g = type(grafo_local)()
    for t in grafo_local:
        g.add(t)
    if grafo_ejemplos:
        for t in grafo_ejemplos:
            g.add(t)
    posiciones = [RDFS.domain, RDFS.range, RDFS.subClassOf, RDF.type,
                  URIRef(SH + "targetClass"), URIRef(SH + "path")]
    fantasmas = set()
    for pred in posiciones:
        for s, o in g.subject_objects(pred):
            for nodo in (s, o):
                if isinstance(nodo, URIRef) and str(nodo).startswith(propia):
                    if (nodo, None, None) not in g:
                        fantasmas.add(f"{pred.split('#')[-1]}: {nodo}")
    assert not fantasmas, (
        "IRIs del namespace propio usados pero no declarados en el repo:\n  "
        + "\n  ".join(sorted(fantasmas))
    )
