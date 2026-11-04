"""Dimensión: cada fichero .sparql es UNA consulta y devuelve resultados sobre examples.

Política del org: 1 fichero = 1 consulta. Las variantes se documentan como
comentarios dentro del fichero o se separan en ficheros -a/-b/-c.

La comprobación se hace con el parser SPARQL de rdflib (la gramática solo
acepta una consulta por parseo), no con regex: los sub-SELECTs legítimos
dentro del WHERE no se cuentan como consultas adicionales.
"""
import re
import pytest
from pathlib import Path
from pyparsing import ParseException
from rdflib.plugins.sparql.parser import parseQuery
from util import ROOT, cargar_grafo_ejemplos

MARCADOR = re.compile(r"<(URI|FECHA)[-_A-Za-z0-9]*>")


def ficheros():
    d = ROOT / "requirements"
    return sorted(d.rglob("*.sparql")) if d.is_dir() else []


def consulta_unica(path: Path) -> str | None:
    """Devuelve la consulta del fichero (íntegra), o None si no hay exactamente 1.

    Usa el parser SPARQL de rdflib: si el fichero contiene 0, 2 o más
    consultas (o sintaxis inválida), parseQuery lanza ParseException.
    """
    texto = path.read_text(errors="replace")
    try:
        parseQuery(texto)
        return texto
    except ParseException:
        return None


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
