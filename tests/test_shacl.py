"""Dimensión: los ejemplos del repo validan contra sus shapes."""

import pytest
import subprocess
import sys
from pathlib import Path

from util import ROOT, TIMEOUT_SHACL_S, sniff_parse


def test_ejemplos_conformes(ficheros_shapes, datos_ejemplos):
    if not ficheros_shapes or datos_ejemplos is None:
        pytest.skip("sin shapes o sin ejemplos")
    shg = type(datos_ejemplos)()
    for p in ficheros_shapes:
        sniff_parse(p, shg)
    d = ROOT / "tests" / ".shacl_data.ttl"
    s = ROOT / "tests" / ".shacl_shapes.ttl"
    datos_ejemplos.serialize(destination=str(d), format="turtle")
    shg.serialize(destination=str(s), format="turtle")
    code = (
        "import sys; from rdflib import RDF, URIRef; from pyshacl import validate;"
        f"r=validate(data_graph={str(d)!r}, shacl_graph={str(s)!r}, inference='none', advanced=True);"
        "rg=r[1]; VR=URIRef('http://www.w3.org/ns/shacl#ValidationResult');"
        "print('CONFORMS' if r[0] else 'VIOLATIONS:'+str(len(set(rg.subjects(RDF.type, VR))))); sys.exit(0)"
    )
    try:
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=TIMEOUT_SHACL_S).stdout.strip()
        assert out.startswith("CONFORMS"), f"ejemplos no conformes: {out}"
    finally:
        Path(d).unlink(missing_ok=True)
        Path(s).unlink(missing_ok=True)
