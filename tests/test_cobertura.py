"""Dimensión: cada fichero .sparql es UNA consulta y devuelve resultados sobre examples.

Política del org: 1 fichero = 1 consulta. Las variantes se documentan como
comentarios dentro del fichero o se separan en ficheros -a/-b/-c.
"""
import re
import pytest
from pathlib import Path
from util import ROOT, cargar_grafo_ejemplos

PALABRAS = re.compile(r"(?mi)^\s*(SELECT|ASK|CONSTRUCT|DESCRIBE)\b")
MARCADOR = re.compile(r"<(URI|FECHA)[-_A-Za-z0-9]*>")


def ficheros():
    d = ROOT / "requirements"
    return sorted(d.rglob("*.sparql")) if d.is_dir() else []


def consulta_unica(path: Path) -> str | None:
    """Devuelve la consulta del fichero (íntegra), o None si no hay exactamente 1."""
    texto = path.read_text(errors="replace")
    sin_prefijos = "\n".join(
        l for l in texto.splitlines()
        if not re.match(r"(?i)^\s*(PREFIX|BASE)\b", l)
    )
    n = len(PALABRAS.findall(sin_prefijos))
    return texto if n == 1 else None


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_consulta_unica(path):
    assert consulta_unica(path) is not None, (
        "el fichero debe contener exactamente 1 consulta "
        "(separa las variantes en ficheros -a/-b o coméntalas)")


@pytest.mark.parametrize("path", ficheros(), ids=lambda p: str(p.relative_to(ROOT)))
def test_consulta_devuelve_resultados(path, grafo_ejemplos):
    cuerpo = consulta_unica(path)
    if cuerpo is None:
        pytest.skip("fichero no es una consulta única (falla test_consulta_unica)")
    if MARCADOR.search(cuerpo):
        pytest.skip("plantilla con marcadores <URI-...>/<FECHA-...> para el usuario")
    if grafo_ejemplos is None:
        pytest.skip("sin ejemplos parseables (lo reporta test_parseo)")
    r = grafo_ejemplos.query(cuerpo)
    n = r.askAnswer if r.type == "ASK" else len(r)
    assert n > 0, "la consulta no devuelve resultados sobre los ejemplos"
