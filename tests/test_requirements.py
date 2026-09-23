"""Dimensión: requirements.csv, ficheros .sparql y queries.html sincronizados."""
import csv
import re

import pytest

from util import ROOT


def _todo():
    d = ROOT / "requirements"
    if not d.is_dir():
        return None
    csvs = list(d.glob("*.csv"))
    sparql = sorted(d.rglob("*.sparql"))
    return csvs, sparql


def test_csv_delimitador_uniforme():
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    for c in todo[0]:
        primera = c.read_text(errors="replace").splitlines()[0]
        assert ";" not in primera, f"{c.name} usa ';' como delimitador (el resto de la org usa ',')"


def test_ids_csv_con_fichero():
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    ficheros = " ".join(p.name for p in todo[1])
    sin_fichero = []
    for c in todo[0]:
        texto = c.read_text(errors="replace")
        for fila in csv.DictReader(texto.splitlines()):
            idv = (fila.get("ID") or fila.get("Id") or "").strip()
            if re.fullmatch(r"[A-Za-z]+\d+", idv) and idv not in ficheros:
                sin_fichero.append(f"{c.name}: {idv}")
    assert not sin_fichero, f"IDs en CSV sin fichero .sparql:\n  " + "\n  ".join(sin_fichero[:15])


def test_ficheros_en_csv():
    todo = _todo()
    if not todo or not todo[0]:
        pytest.skip("sin requirements.csv")
    ids = set()
    for c in todo[0]:
        for fila in csv.DictReader(c.read_text(errors="replace").splitlines()):
            idv = (fila.get("ID") or fila.get("Id") or "").strip()
            if idv:
                ids.add(idv)
    huerfanos = []
    for p in todo[1]:
        m = re.match(r"([A-Za-z]+\d+)", p.name)
        if m and m.group(1) not in ids:
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
    ids = set()
    for c in todo[0]:
        for fila in csv.DictReader(c.read_text(errors="replace").splitlines()):
            idv = (fila.get("ID") or fila.get("Id") or "").strip()
            if idv:
                ids.add(idv)
    ausentes = sorted(i for i in ids if i not in html)
    assert not ausentes, f"IDs del CSV que no aparecen en queries.html: {ausentes[:15]}"
