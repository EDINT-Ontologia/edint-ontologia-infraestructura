"""Dimensión: cobertura de rdfs:label es/en en los términos propios."""
from rdflib import Literal, URIRef
from rdflib.namespace import OWL, RDFS


def test_labels_es_en(modelo, ns_propia):
    if modelo is None or ns_propia is None:
        pytest.skip("sin modelo")
    sin_es, sin_en, sin_idioma = [], [], 0
    terminos = set(modelo.subjects(None, OWL.Class)) | set(modelo.subjects(None, OWL.ObjectProperty)) | set(modelo.subjects(None, OWL.DatatypeProperty))
    for t in terminos:
        if not isinstance(t, URIRef) or not str(t).startswith(ns_propia):
            continue
        labels = [l for l in modelo.objects(t, RDFS.label) if isinstance(l, Literal)]
        langs = {l.language for l in labels}
        if "es" not in langs:
            sin_es.append(str(t).split("#")[-1])
        if "en" not in langs:
            sin_en.append(str(t).split("#")[-1])
        sin_idioma += sum(1 for l in labels if not l.language)
    total = len([t for t in terminos if isinstance(t, URIRef) and str(t).startswith(ns_propia)])
    umbral = 0.05
    frac = (len(sin_es) + len(sin_en)) / max(1, total * 2)
    assert frac <= umbral, f"labels incompletos: {len(sin_es)} sin @es y {len(sin_en)} sin @en de {total} términos ({frac:.0%} > {umbral:.0%}); {sin_idioma} labels sin idioma. Sin @es: {sin_es[:10]}"
