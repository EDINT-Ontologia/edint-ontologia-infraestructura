"""Dimensión: los prefijos citados en los diagramas existen en el modelo del repo."""
from util import ROOT, prefijos_declarados_repo, prefijos_usados

# Prefijos estructurales de los formatos XML de diagramas, no del modelo.
IGNORADOS = {"xml", "mx", "html", "xhtml"}


def test_prefijos_de_diagramas_declarados():
    d = ROOT / "diagrams"
    if not d.is_dir():
        return
    declarados = prefijos_declarados_repo()
    mal = []
    for p in sorted(d.rglob("*.xml")):
        usados = prefijos_usados(p.read_text(errors="replace"))
        for alias in sorted(usados - declarados - IGNORADOS):
            mal.append(f"{p.name}: {alias}:")
    assert not mal, (
        "prefijos de diagrama no declarados en el modelo del repo:\n  "
        + "\n  ".join(sorted(set(mal)))
    )
