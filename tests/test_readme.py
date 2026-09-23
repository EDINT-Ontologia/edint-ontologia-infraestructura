"""Dimensión: estructura y enlaces del README."""
import re

import pytest

from util import ROOT


def lineas():
    p = ROOT / "README.md"
    return p.read_text(errors="replace").splitlines() if p.exists() else None


def test_un_solo_h1():
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    h1 = [l for l in ls if l.startswith("# ")]
    assert len(h1) == 1, f"{len(h1)} encabezados H1 (debe ser 1: el título)"


def test_linea_en_blanco_tras_badges():
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    for i, l in enumerate(ls):
        if l.startswith(("![", "[![")) and i + 1 < len(ls):
            sig = ls[i + 1]
            if sig.strip() and not sig.startswith(("![", "[![")):
                pytest.fail(f"badge pegado al texto (línea {i + 2}): {sig[:60]!r}")


def test_enlaces_bien_formados():
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    texto = "\n".join(ls)
    mal = re.findall(r"\[[^\]]{1,60}\]\s+\(", texto)
    assert not mal, f"enlaces con espacio antes del paréntesis: {mal[:3]}"


def test_imagenes_existen():
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    texto = "\n".join(ls)
    rels = [m for m in re.findall(r"\]\(([^)#?]+)(?:#[^)]*)?\)", texto) if not m.startswith(("http://", "https://", "mailto:"))]
    rels += [m for m in re.findall(r'<img[^>]+src="([^"]+)"', texto) if not m.startswith(("http://", "https://"))]
    rotos = [r for r in rels if not (ROOT / r.strip()).exists()]
    assert not rotos, f"imágenes/enlaces rotos: {sorted(set(rotos))}"


def test_badge_de_licencia():
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    texto = "\n".join(ls)
    assert "img.shields.io" in texto and "licencia" in texto.lower(), (
        "falta el badge de licencia en el README"
    )


def test_readme_cita_prefijo_y_namespace(modelo):
    if modelo is None:
        pytest.skip("sin modelo")
    ls = lineas()
    if ls is None:
        pytest.skip("sin README")
    texto = "\n".join(ls)
    from rdflib import URIRef
    from rdflib.namespace import OWL, RDF
    vann = next(modelo.objects(None, URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")), None)
    iri = next(modelo.subjects(RDF.type, OWL.Ontology), None)
    if vann:
        assert f"`{vann}`" in texto, f"el README no cita el prefijo `{vann}`"
    if iri and str(iri).startswith("https://edint.es/"):
        assert str(iri).rstrip("#") in texto, f"el README no cita el namespace {str(iri).rstrip('#')}"
