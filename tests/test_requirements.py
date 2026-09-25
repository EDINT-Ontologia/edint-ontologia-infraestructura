"""Dimensión: requirements.csv, ficheros .sparql y queries.html sincronizados."""
import csv
import re

import pytest

from util import ROOT


def _columna_id(cabeceras: list[str]) -> str:
    """La columna de identificadores: la que se llame id/identifier, o la primera."""
    for c in cabeceras:
        if re.fullmatch(r"\s*(id|identifier)\s*", (c or ""), re.I):
            return c
    return cabeceras[0] if cabeceras else ""


def _delimitador(csv_path) -> str:
    """Delimitador real del CSV: ',' o ';' según la cabecera."""
    primera = csv_path.read_text(errors="replace").splitlines()[0]
    return ";" if primera.count(";") > primera.count(",") else ","


def _filas(csv_path):
    with csv_path.open(errors="replace", newline="") as f:
        lector = csv.DictReader(f, delimiter=_delimitador(csv_path))
        col = _columna_id(lector.fieldnames or [])
        for fila in lector:
            yield (fila.get(col) or "").strip()


def _ids(csv_path) -> set[str]:
    return {i for i in _filas(csv_path) if i}


def _normalizar(identificador: str) -> str:
    """SUM06 y SUM6 son el mismo identificador: normaliza el relleno de ceros."""
    m = re.fullmatch(r"([A-Za-z]+)0*(\d+)", identificador.strip())
    return f"{m.group(1)}{int(m.group(2))}" if m else identificador.strip()


def _todo():
    d = ROOT / "requirements"
    if not d.is_dir():
        return None
    csvs = list(d.glob("*.csv"))
    sparql = sorted(d.rglob("*.sparql"))
    return csvs, sparql


def test_csv_delimitador_uniforme():
    """Todos los CSV de requirements/ deben usar el mismo delimitador (',' o ';')."""
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    delimitadores = {c.name: _delimitador(c) for c in todo[0]}
    usados = set(delimitadores.values())
    assert len(usados) == 1, (
        f"delimitadores mezclados en requirements/: {delimitadores}"
    )


def test_ids_csv_con_fichero():
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    presentes = {_normalizar(p.name.split(".")[0]) for p in todo[1]}
    sin_fichero = []
    for c in todo[0]:
        for idv in sorted(_ids(c)):
            if re.fullmatch(r"[A-Za-z]+\d+", idv) and _normalizar(idv) not in presentes:
                sin_fichero.append(f"{c.name}: {idv}")
    assert not sin_fichero, f"IDs en CSV sin fichero .sparql:\n  " + "\n  ".join(sin_fichero[:15])


def test_ficheros_en_csv():
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    ids = {_normalizar(i) for c in todo[0] for i in _ids(c)}
    huerfanos = []
    for p in todo[1]:
        m = re.match(r"([A-Za-z]+\d+)", p.name)
        if m and _normalizar(m.group(1)) not in ids:
            huerfanos.append(p.name)
    assert not huerfanos, f"ficheros .sparql sin fila en el CSV: {huerfanos}"


def test_queries_html_actualizado():
    todo = _todo()
    if not todo:
        pytest.skip("sin requirements/")
    qh = ROOT / "requirements" / "queries.html"
    if not qh.exists() or not todo[0]:
        pytest.skip("sin queries.html o sin CSV")
    html = qh.read_text(errors="replace")
    ausentes = []
    for c in todo[0]:
        for i in sorted(_ids(c)):
            if i in html:
                continue
            # tolera diferencia de padding de ceros (VEH7 vs VEH07)
            m = re.fullmatch(r"([A-Za-z]+)(\d+)", i)
            alternativas = {f"{m.group(1)}{int(m.group(2))}", f"{m.group(1)}{m.group(2).zfill(2)}"} if m else {i}
            if not any(a in html for a in alternativas):
                ausentes.append(i)
    assert not ausentes, f"IDs del CSV que no aparecen en queries.html: {ausentes[:15]}"
