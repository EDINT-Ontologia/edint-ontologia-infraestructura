"""Dimensión: sin URIs rotas o legacy conocidas en el código fuente."""
import pytest

from util import ROOT, URI_BLACKLIST, source_files

FICHEROS = source_files()


@pytest.mark.parametrize("path", FICHEROS, ids=lambda p: str(p.relative_to(ROOT)))
def test_sin_uris_rotas(path):
    texto = path.read_text(errors="replace")
    encontradas = [pat for pat in URI_BLACKLIST if pat in texto]
    assert not encontradas, f"URIs rotas/legacy: {encontradas}"
