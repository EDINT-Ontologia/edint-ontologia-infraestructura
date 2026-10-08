"""Dimensión: cobertura de rdfs:label es/en en los términos propios."""

import pytest
from util import UMBRAL_LABELS
from rdflib import Literal, URIRef
from rdflib.namespace import OWL, RDFS


def _propios(modelo, ns_propia):
    terminos = set(modelo.subjects(None, OWL.Class)) | set(modelo.subjects(None, OWL.ObjectProperty)) | set(modelo.subjects(None, OWL.DatatypeProperty))
    return [t for t in terminos if isinstance(t, URIRef) and str(t).startswith(ns_propia)]


def test_labels_es_en(modelo, ns_propia):
    if modelo is None or ns_propia is None:
        pytest.skip("sin modelo")
    propios = _propios(modelo, ns_propia)
    sin_es, sin_en = [], []
    for t in propios:
        langs = {l.language for l in modelo.objects(t, RDFS.label) if isinstance(l, Literal)}
        if "es" not in langs:
            sin_es.append(str(t).split("#")[-1])
        if "en" not in langs:
            sin_en.append(str(t).split("#")[-1])
    total = len(propios)
    frac = (len(sin_es) + len(sin_en)) / max(1, total * 2)
    assert frac <= UMBRAL_LABELS, (
        f"labels incompletos: {len(sin_es)} sin @es y {len(sin_en)} sin @en de {total} "
        f"({frac:.0%} > 5%). Sin @es: {sin_es[:10]}"
    )


def test_labels_con_idioma(modelo, ns_propia):
    if modelo is None or ns_propia is None:
        pytest.skip("sin modelo")
    sin = [str(t).split("#")[-1] for t in _propios(modelo, ns_propia)
           for l in modelo.objects(t, RDFS.label)
           if isinstance(l, Literal) and not l.language]
    assert not sin, f"labels sin etiqueta de idioma: {sin[:15]}"
