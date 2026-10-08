"""Dimensión: coherencia de licencia entre LICENSE, badge del README y OWL."""
import re

import pytest
from rdflib import URIRef

from util import ROOT

DCT_LICENSE = URIRef("http://purl.org/dc/terms/license")


def test_license_existe():
    assert (ROOT / "LICENSE").exists(), "falta el fichero LICENSE"


def test_badge_coherente_con_owl(modelo):
    if modelo is None:
        pytest.skip("sin fichero de modelo")
    readme = (ROOT / "README.md").read_text(errors="replace") if (ROOT / "README.md").exists() else ""
    owl = next(modelo.objects(None, DCT_LICENSE), None)
    if owl is None:
        pytest.fail("el OWL no declara dcterms:license")
    badge = " ".join(re.findall(r"img\.shields\.io/badge/[^\s)]*licencia[^\s)]*", readme, re.I))
    assert badge, "el README no tiene badge de licencia"
    con_sa_owl = "/by-sa/" in str(owl).lower() or "by-sa" in str(owl).lower()
    con_sa_badge = "by--sa" in badge.lower().replace("%20", "") or "by-sa" in badge.lower().replace("%20", " ")
    assert con_sa_owl == con_sa_badge, (
        f"licencia incoherente: OWL={owl} ({'BY-SA' if con_sa_owl else 'BY'}) vs badge={badge[:80]}"
    )
