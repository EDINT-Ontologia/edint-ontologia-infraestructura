"""Dimensión: jerarquía de clases sin ciclos."""
import pytest
from rdflib import URIRef
from rdflib.namespace import RDFS


def test_sin_ciclos_subclassof(modelo):
    if modelo is None:
        pytest.skip("sin fichero de modelo")
    hijos = {}
    for s, o in modelo.subject_objects(RDFS.subClassOf):
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            hijos.setdefault(str(s), set()).add(str(o))

    def ciclo_desde(inicio):
        pila, vistos = [(inicio, [inicio])], set()
        while pila:
            nodo, camino = pila.pop()
            for padre in hijos.get(nodo, ()):
                if padre == inicio:
                    return camino + [padre]
                if padre not in vistos:
                    vistos.add(padre)
                    pila.append((padre, camino + [padre]))
        return None

    for clase in hijos:
        c = ciclo_desde(clase)
        if c:
            pytest.fail(f"ciclo en subClassOf: {' -> '.join(c)}")
