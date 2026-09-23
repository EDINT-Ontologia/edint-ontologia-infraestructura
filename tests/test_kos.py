"""Dimensión: coherencia de los vocabularios SKOS del repo."""
from rdflib import URIRef

SKOS = "http://www.w3.org/2004/02/skos/core#"
IN_SCHEME = URIRef(SKOS + "inScheme")
CONCEPT_SCHEME = URIRef(SKOS + "ConceptScheme")
CONCEPT = URIRef(SKOS + "Concept")
PREF_LABEL = URIRef(SKOS + "prefLabel")

from util import ROOT, extraer_prefijos, rdf_files, sniff_parse, NS_KOS


def ficheros_kos():
    return [p for p in rdf_files("kos") if p.suffix == ".ttl"]


def grafos():
    out = []
    for p in ficheros_kos():
        try:
            out.append((p, sniff_parse(p)))
        except Exception:
            pass
    return out


def test_esquemas_citados_declarados():
    gs = grafos()
    if not gs:
        pytest.skip("sin KOS")
    declarados = {str(s) for _, g in gs for s in g.subjects(None, CONCEPT_SCHEME)}
    citados = {str(o) for _, g in gs for o in g.objects(None, IN_SCHEME) if isinstance(o, URIRef)}
    sin_declarar = sorted(citados - declarados)
    assert not sin_declarar, f"esquemas citados vía skos:inScheme sin declarar: {sin_declarar}"


def test_esquemas_unicos_por_fichero():
    vistos = {}
    duplicados = []
    for p, g in grafos():
        for s in g.subjects(None, CONCEPT_SCHEME):
            if str(s) in vistos and vistos[str(s)] != p.name:
                duplicados.append(f"{str(s)} en {vistos[str(s)]} y {p.name}")
            vistos[str(s)] = p.name
    assert not duplicados, f"esquemas declarados en varios ficheros: {duplicados}"


def test_esquemas_con_etiqueta():
    sin = []
    for p, g in grafos():
        for s in g.subjects(None, CONCEPT_SCHEME):
            labels = list(g.objects(s, URIRef("http://www.w3.org/2000/01/rdf-schema#label")))
            labels += list(g.objects(s, PREF_LABEL))
            if not labels:
                sin.append(f"{p.name}: {s}")
    assert not sin, f"esquemas sin rdfs:label/skos:prefLabel: {sin}"


def test_prefijo_de_conceptos_coherente_con_esquema():
    mal = []
    for p, g in grafos():
        prefijos = extraer_prefijos(p.read_text(errors="replace"))
        for s in g.subjects(None, CONCEPT_SCHEME):
            esperado = str(s) + "/"
            if str(s).startswith(NS_KOS) and esperado not in prefijos.values():
                mal.append(f"{p.name}: esquema {s} sin prefijo de conceptos {esperado}")
    assert not mal, str(mal)


def test_conceptos_con_esquema_y_preflabel():
    mal = []
    for p, g in grafos():
        for c in g.subjects(None, CONCEPT):
            if not list(g.objects(c, IN_SCHEME)):
                mal.append(f"{p.name}: {c} sin skos:inScheme")
            if not list(g.objects(c, PREF_LABEL)):
                mal.append(f"{p.name}: {c} sin skos:prefLabel")
    assert not mal, "\n  ".join(mal[:15])


def test_labels_de_esquemas_no_compartidas():
    labels = {}
    for p, g in grafos():
        for s in g.subjects(None, CONCEPT_SCHEME):
            for l in g.objects(s, URIRef("http://www.w3.org/2000/01/rdf-schema#label")):
                labels.setdefault(str(l), set()).add(str(s))
    compartidas = {l: sorted(ss) for l, ss in labels.items() if len(ss) > 1}
    assert not compartidas, f"labels idénticas en esquemas distintos: {compartidas}"
