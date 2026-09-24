"""Utilidades compartidas de la suite de tests EDINT.

Toda constante vive en tests/config.toml; aquí solo se carga y se exponen
los nombres que usan los módulos de test.
"""
import re
import tomllib
from pathlib import Path

from rdflib import Graph

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
CONFIG = tomllib.loads((TESTS_DIR / "config.toml").read_text(encoding="utf-8"))

RDF_SUFFIXES = set(CONFIG["estructura"]["sufijos_rdf"])
SRC_DIRS = CONFIG["estructura"]["carpetas_fuente"]
SRC_SUFFIXES = set(CONFIG["estructura"]["sufijos_fuente"])
CLAVES_CONFIG = set(CONFIG["estructura"]["claves_config"])

ESQUEMAS_URI_VALIDOS = set(CONFIG["reglas"]["esquemas_uri_validos"])
SLUG_EDINT = re.compile(CONFIG["reglas"]["slug_edint"])
PREFIJO_REGEX = CONFIG["reglas"]["prefijo"]
PATRONES_BASURA = CONFIG["reglas"]["patrones_basura"]
SUFIJOS_DATOS = set(CONFIG["reglas"]["sufijos_datos"])

NS_DEF = CONFIG["namespaces"]["def"]
NS_KOS = CONFIG["namespaces"]["kos"]
INSTANCIAS_EJEMPLO = tuple(CONFIG["namespaces"]["instancias_ejemplo"])

UMBRAL_LABELS = CONFIG["umbrales"]["labels_es_en"]
PARIDAD_SECCIONES = CONFIG["umbrales"]["paridad_secciones"]
PALABRAS_MINIMAS = CONFIG["umbrales"]["palabras_minimas"]
TIMEOUT_SHACL_S = CONFIG["umbrales"]["shacl_timeout_s"]


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
    """Excluye artefactos generados (documentación y mapping_doc)."""
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


def prefijos_declarados_repo() -> set[str]:
    """Prefijos declarados por el propio repo (xmlns de los .owl + @prefix de turtle)."""
    out = set()
    for p in rdf_files("ontology"):
        if p.suffix != ".owl":
            continue
        out |= set(re.findall(r'xmlns:([A-Za-z][\w-]*)=', p.read_text(errors="replace")))
    for d in ("kos", "shapes", "examples", "mappings"):
        base = ROOT / d
        if base.is_dir():
            for p in base.rglob("*.ttl"):
                if _sin_generados(p):
                    out |= set(extraer_prefijos(p.read_text(errors="replace")))
    return out
