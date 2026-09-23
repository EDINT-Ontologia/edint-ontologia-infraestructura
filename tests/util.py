"""Utilidades compartidas de la suite de tests EDINT."""
import re
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
    "vocab.linkeddata.es/datosabiertos/kos",
]

SRC_DIRS = ["ontology", "kos", "shapes", "examples", "mappings", "requirements"]
SRC_SUFFIXES = {".owl", ".ttl", ".sparql", ".py", ".md", ".yml", ".csv", ".html"}

# Erratas reales encontradas en la org (regex; cada entrada, un incidente real).
ERRATAS = [
    r"utilizad(?![a-záéíóú])",
    r"implmeentación",
    r"reposity",
    r"Graficos",
    r"inlcuire",
    r"spueden",
    r"creados con\[",
    r"reflejar os\b",
    r"eventps",
    r"climatolológicas",
    r"\blu punto\b",
    r"los nombre de las propiedades",
    r"poderación",
    r"IllumintationRegime",
    r"Este catalogo\b",
]

# Prefijos legacy/fantasma que no deben aparecer en los diagramas (incidentes reales).
DIAGRAMA_PREFIJOS_MALOS = [
    "edintmi:", "edintinfp:", "eidntkos:", "era:", "esapar:", "estraf:",
    "esreg:", "zona:",
]


def repo_slug() -> str:
    name = ROOT.name
    for pref in ("edint-ontologia-", "edint-cubo-"):
        if name.startswith(pref):
            return name[len(pref):]
    return name


def sniff_parse(path: Path, g: Graph | None = None) -> Graph:
    g = g if g is not None else Graph()
    head = path.read_text(errors="replace")[:400]
    fmt = "xml" if ("<rdf:RDF" in head or head.lstrip().startswith("<?xml")) else "turtle"
    g.parse(str(path), format=fmt)
    return g


def _sin_generados(p: Path) -> bool:
    return "mapping_doc" not in p.parts and "documentation" not in p.parts


def rdf_files(*dirs: str) -> list[Path]:
    out = []
    for d in dirs:
        base = ROOT / d
        if base.is_dir():
            out += [
                p for p in sorted(base.rglob("*"))
                if p.is_file() and p.suffix.lstrip(".") in RDF_SUFFIXES and _sin_generados(p)
            ]
    return out


def source_files() -> list[Path]:
    files = []
    for d in SRC_DIRS:
        base = ROOT / d
        if base.is_dir():
            files += [
                p for p in base.rglob("*")
                if p.is_file() and p.suffix in SRC_SUFFIXES and _sin_generados(p)
            ]
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


def extraer_prefijos(texto: str) -> dict[str, str]:
    """Alias -> URI a partir de @prefix/PREFIX de un turtle/sparql."""
    out = {}
    for m in re.finditer(r"(?:@prefix|PREFIX)\s+([A-Za-z][\w-]*)\s*:\s*<([^>]+)>", texto):
        out[m.group(1)] = m.group(2)
    return out


def prefijos_usados(texto: str) -> set[str]:
    """Alias usados como nombre prefijado, ignorando URIs, strings y comentarios."""
    t = re.sub(r"<[^>]*>", " ", texto)
    t = re.sub(r'"[^"]*"', " ", t)
    t = re.sub(r"(?m)#.*$", " ", t)
    return {m.group(1) for m in re.finditer(r"(?<![\w@.-])([A-Za-z][\w-]*):[A-Za-z_][\w.-]*", t)}
