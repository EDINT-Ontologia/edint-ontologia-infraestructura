"""Utilidades compartidas de la suite de tests EDINT."""
from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent

RDF_SUFFIXES = {"ttl", "nt", "rdf", "jsonld", "xml", "owl"}

URI_BLACKLIST = [
    "hhttps://",
    "httos://",
    "edint.es/def/censovehiculos",
    "edint.es/def/medioambiente#",
    "edint.es/def/contaminacionacustica",
    "edint.es/def/zone#",
    "edint.github.io",
    "w3id.org/medioambiente",
    "github.com/edint/",
    "www.w3.org/TR/vocab-data-cube",
]

SRC_DIRS = ["ontology", "kos", "shapes", "examples", "mappings", "requirements"]
SRC_SUFFIXES = {".owl", ".ttl", ".sparql", ".py", ".md", ".yml", ".csv", ".html"}


def sniff_parse(path: Path, g: Graph | None = None) -> Graph:
    """Parsea un fichero RDF detectando turtle/xml por contenido (los .owl pueden ser cualquiera)."""
    g = g if g is not None else Graph()
    head = path.read_text(errors="replace")[:400]
    fmt = "xml" if ("<rdf:RDF" in head or head.lstrip().startswith("<?xml")) else "turtle"
    g.parse(str(path), format=fmt)
    return g


def rdf_files(*dirs: str) -> list[Path]:
    out = []
    for d in dirs:
        base = ROOT / d
        if base.is_dir():
            out += [p for p in sorted(base.rglob("*")) if p.is_file() and p.suffix.lstrip(".") in RDF_SUFFIXES]
    return out


def source_files() -> list[Path]:
    files = []
    for d in SRC_DIRS:
        base = ROOT / d
        if base.is_dir():
            files += [p for p in base.rglob("*") if p.is_file() and p.suffix in SRC_SUFFIXES]
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    return files


def model_path() -> Path | None:
    for cand in ("ontology/ontology.owl", "ontology/data-cube.owl"):
        p = ROOT / cand
        if p.exists():
            return p
    return None
