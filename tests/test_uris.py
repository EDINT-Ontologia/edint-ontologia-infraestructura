"""Dimensión: URIs bien formadas en el código fuente (reglas genéricas)."""
import re

import pytest

from util import ESQUEMAS_URI_VALIDOS, ROOT, SLUG_EDINT, SUFIJOS_DATOS, source_files

FICHEROS = source_files()
RE_ESQUEMA = re.compile(r"(?<![\w:/])([A-Za-z][A-Za-z0-9+.\-]*)://")
RE_DEF = re.compile(r"https://edint\.es/def/([A-Za-z0-9._-]+)")


@pytest.mark.parametrize("path", FICHEROS, ids=lambda p: str(p.relative_to(ROOT)))
def test_esquemas_uri_validos(path):
    if path.suffix.lower() in SUFIJOS_DATOS:
        pytest.skip("fichero de datos, no de código")
    esquemas = {e.lower() for e in RE_ESQUEMA.findall(path.read_text(errors="replace"))}
    invalidos = sorted(esquemas - ESQUEMAS_URI_VALIDOS)
    assert not invalidos, f"esquemas de URI no válidos: {invalidos}"


@pytest.mark.parametrize("path", FICHEROS, ids=lambda p: str(p.relative_to(ROOT)))
def test_slugs_edint_bien_formados(path):
    slugs = set(RE_DEF.findall(path.read_text(errors="replace")))
    mal = sorted(s for s in slugs if not SLUG_EDINT.fullmatch(s))
    assert not mal, f"slugs EDINT que no cumplen kebab-case: {mal}"
