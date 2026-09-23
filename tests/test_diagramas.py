"""Dimensión: diagramas sin prefijos legacy/fantasma."""
from util import DIAGRAMA_PREFIJOS_MALOS, ROOT


def test_sin_prefijos_malos():
    d = ROOT / "diagrams"
    mal = []
    for p in sorted(d.rglob("*.xml")) if d.is_dir() else []:
        texto = p.read_text(errors="replace")
        for pref in DIAGRAMA_PREFIJOS_MALOS:
            if pref in texto:
                mal.append(f"{p.name}: {pref}")
    assert not mal, "prefijos legacy/fantasma en diagramas:\n  " + "\n  ".join(sorted(set(mal)))
