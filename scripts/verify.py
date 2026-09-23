#!/usr/bin/env python
"""Self-testing EDINT: verificación local de un repositorio de modelo.

Uso:
    python scripts/verify.py                 # verifica (respeta la baseline)
    python scripts/verify.py --strict        # ignora la baseline (todo debe estar a 0)
    python scripts/verify.py --update-baseline  # reescribe scripts/known-issues.json

Sale 0 si cada código de problema está por debajo o igual de su baseline
(0 por defecto); sale 1 en cuanto algún código la supera (regresión o deuda
creciente). Sin red: todo se comprueba contra ficheros locales.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "known-issues.json"

# ---------------------------------------------------------------- helpers
RDF_FILES = {
    "ttl": "turtle", "nt": "nt", "rdf": "xml", "jsonld": "json-ld",
    "owl": "owl-sniff", "xml": "xml",
}

URI_BLACKLIST = [
    ("hhttps://", "typo hhttps"),
    ("httos://", "typo httos"),
    ("edint.es/def/censovehiculos", "slug sin guion"),
    ("edint.es/def/medioambiente#", "slug sin guion"),
    ("edint.es/def/contaminacionacustica", "slug sin guion"),
    ("edint.es/def/zone#", "namespace fantasma"),
    ("edint.github.io", "namespace legacy"),
    ("w3id.org/medioambiente", "namespace legacy"),
    ("github.com/edint/", "organizacion incorrecta"),
    ("www.w3.org/TR/vocab-data-cube", "IRI de documento W3C como ontologia"),
]

SRC_DIRS = ["ontology", "kos", "shapes", "examples", "mappings", "requirements", "tests"]


def issues() -> Counter:
    return Counter()


def sniff_and_parse(path: Path, g: Graph | None = None) -> Graph:
    g = g if g is not None else Graph()
    fmt = "turtle"
    head = path.read_text(errors="replace")[:400]
    if "<rdf:RDF" in head or head.lstrip().startswith("<?xml"):
        fmt = "xml"
    g.parse(str(path), format=fmt)
    return g


def iter_rdf_files(*dirs: str):
    for d in dirs:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lstrip(".") in RDF_FILES:
                yield p


# ---------------------------------------------------------------- checks
def check_parse(cnt: Counter):
    """C-PARSE: todo RDF del repo parsea (fuente y serializaciones publicadas)."""
    for p in iter_rdf_files("ontology", "kos", "shapes", "examples", "mappings"):
        try:
            sniff_and_parse(p)
        except Exception as e:  # noqa: BLE001
            cnt["C-PARSE"] += 1
            print(f"  [C-PARSE] {p.relative_to(ROOT)}: {str(e).splitlines()[0][:100]}")
    for name in ("ontology.ttl", "ontology.rdf", "ontology.jsonld", "ontology.nt", "ontology.owl"):
        p = ROOT / "documentation" / name
        if p.exists():
            try:
                Graph().parse(str(p), format=RDF_FILES.get(p.suffix.lstrip("."), "turtle"))
            except Exception as e:  # noqa: BLE001
                cnt["C-PARSE"] += 1
                print(f"  [C-PARSE] documentation/{name}: {str(e).splitlines()[0][:100]}")


def check_single_ontology(cnt: Counter, model: Graph):
    """C-ONTOLOGY: un unico owl:Ontology por fichero de modelo."""
    onts = set(model.subjects(RDF.type, OWL.Ontology))
    if len(onts) != 1:
        cnt["C-ONTOLOGY"] += 1
        print(f"  [C-ONTOLOGY] {len(onts)} sujetos owl:Ontology (debe ser exactamente 1)")


def check_blacklist(cnt: Counter):
    """C-URIBLACKLIST: URIs rotas/legacy conocidas en fuente (incluye README)."""
    files = []
    for base in [ROOT / d for d in SRC_DIRS if (ROOT / d).is_dir()]:
        files += [p for p in base.rglob("*") if p.is_file() and p.suffix in (".owl", ".ttl", ".sparql", ".py", ".md", ".yml", ".csv", ".html")]
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    for p in files:
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for pat, why in URI_BLACKLIST:
            for _ in re.finditer(re.escape(pat), text):
                cnt["C-URIBLACKLIST"] += 1
                print(f"  [C-URIBLACKLIST] {p.relative_to(ROOT)}: {pat} ({why})")


def check_sparql(cnt: Counter):
    """C-SPARQL: cada fichero de requirements parsea (entero o por bloques PREFIX)."""
    base = ROOT / "requirements"
    if not base.is_dir():
        return
    for p in sorted(base.rglob("*.sparql")):
        src = p.read_text(errors="replace")
        try:
            prepareQuery(src)
            continue
        except Exception:  # noqa: BLE001
            pass
        try:
            blocks = re.split(r"(?m)^(?=PREFIX\s+\S+\s*<)", src)
            ok = True
            for b in [b for b in blocks if b.strip()]:
                try:
                    prepareQuery(b)
                except Exception:  # noqa: BLE001
                    ok = False
            if ok:
                continue
        except Exception:  # noqa: BLE001
            pass
        cnt["C-SPARQL"] += 1
        print(f"  [C-SPARQL] {p.relative_to(ROOT)}: no parsea (entero ni por bloques PREFIX)")


def check_kos(cnt: Counter, kos: list[Graph]):
    """C-KOSSCHEME: todo skos:inScheme apunta a un ConceptScheme declarado."""
    declared: set[str] = set()
    for g in kos:
        for s in g.subjects(RDF.type, URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme")):
            declared.add(str(s))
    SKOS_INSCHEME = URIRef("http://www.w3.org/2004/02/skos/core#inScheme")
    seen: set[str] = set()
    for g in kos:
        for _, _, o in g.triples((None, SKOS_INSCHEME, None)):
            if isinstance(o, URIRef) and str(o) not in declared and str(o) not in seen:
                seen.add(str(o))
                cnt["C-KOSSCHEME"] += 1
                print(f"  [C-KOSSCHEME] esquema citado sin declarar: {o}")


def check_owl_meta(cnt: Counter, model: Graph):
    """C-OWLMETA: metadatos minimos de la ontologia."""
    VANN = URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")
    onts = list(model.subjects(RDF.type, OWL.Ontology))
    if not onts:
        return
    o = onts[0]
    for pred, code, nombre in [
        (VANN, "C-OWLMETA", "vann:preferredNamespacePrefix"),
        (OWL.versionIRI, "C-OWLMETA", "owl:versionIRI"),
        (URIRef("http://purl.org/dc/terms/license"), "C-OWLMETA", "dcterms:license"),
        (RDFS.label, "C-OWLMETA", "rdfs:label"),
    ]:
        if not list(model.objects(o, pred)):
            cnt[code] += 1
            print(f"  [C-OWLMETA] falta {nombre}")


def check_config(cnt: Counter):
    """C-CONFIG: los paths declarados en .config existen."""
    p = ROOT / ".config"
    if not p.exists():
        return
    for line in p.read_text(errors="replace").splitlines():
        m = re.match(r"\s*(\w+)\s*=\s*(\./\S+)", line)
        if not m:
            continue
        key, rel = m.group(1), m.group(2).rstrip("/")
        if key in ("shapes", "examples", "tests", "requirements", "ontology", "kos", "documentation", "mappings"):
            if not (ROOT / rel).exists():
                cnt["C-CONFIG"] += 1
                print(f"  [C-CONFIG] {key} = {rel} no existe")


def check_shape_ghosts(cnt: Counter, model: Graph, shapes: list[Path]):
    """C-SHAPEGHOST: targetClass y path de las shapes existen en el grafo local."""
    if not shapes:
        return
    local = Graph()
    for p in iter_rdf_files("ontology", "kos"):
        try:
            sniff_and_parse(p, local)
        except Exception:  # noqa: BLE001
            pass
    SH_TARGET = URIRef("http://www.w3.org/ns/shacl#targetClass")
    SH_PATH = URIRef("http://www.w3.org/ns/shacl#path")
    seen: set[str] = set()
    for p in shapes:
        try:
            g = sniff_and_parse(p)
        except Exception:  # noqa: BLE001
            continue
        for pred in (SH_TARGET, SH_PATH):
            for _, o in g.subject_objects(pred):
                if isinstance(o, URIRef) and str(o).startswith("https://edint.es/"):
                    if (o, None, None) not in local and str(o) not in seen:
                        seen.add(str(o))
                        cnt["C-SHAPEGHOST"] += 1
                        print(f"  [C-SHAPEGHOST] {p.name}: {pred.split('#')[-1]} inexistente localmente: {o}")


def check_shacl(cnt: Counter, model: Graph, shapes: list[Path]):
    """C-SHAACL: examples+ontologia validan contra shapes (subproceso con timeout)."""
    if not shapes or not (ROOT / "examples").is_dir():
        return
    data = Graph()
    for t in model:
        data.add(t)
    for p in iter_rdf_files("examples"):
        try:
            sniff_and_parse(p, data)
        except Exception:  # noqa: BLE001
            pass
    if not len(data):
        return
    shg = Graph()
    for p in shapes:
        try:
            sniff_and_parse(p, shg)
        except Exception:  # noqa: BLE001
            pass
    tmp_data = ROOT / "scripts" / ".shacl_data.ttl"
    tmp_shg = ROOT / "scripts" / ".shacl_shapes.ttl"
    data.serialize(destination=str(tmp_data), format="turtle")
    shg.serialize(destination=str(tmp_shg), format="turtle")
    code = (
        "import sys; from rdflib import RDF, URIRef; from pyshacl import validate;"
        f"r=validate(data_graph=str({str(tmp_data)!r}), shacl_graph=str({str(tmp_shg)!r}),"
        " inference='none', advanced=True);"
        " rg=r[1]; SH=URIRef('http://www.w3.org/ns/shacl#ValidationResult');"
        " n=len(set(rg.subjects(RDF.type, SH)));"
        " print('CONFORMS' if r[0] else 'VIOLATIONS:'+str(n)); sys.exit(0)"
    )
    try:
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, timeout=600
        ).stdout.strip()
        if out.startswith("VIOLATIONS"):
            n = int(out.split(":")[1])
            cnt["C-SHAACL"] += n
            print(f"  [C-SHAACL] examples NO conformes: {n} violaciones")
    except subprocess.TimeoutExpired:
        cnt["C-SHAACL"] += 1
        print("  [C-SHAACL] timeout en la validacion")
    finally:
        tmp_data.unlink(missing_ok=True)
        tmp_shg.unlink(missing_ok=True)


def check_labels(cnt: Counter, model: Graph, own_ns: str | None):
    """C-LABELS: terminos propios con rdfs:label en es y en."""
    if not own_ns:
        return
    total = sin_es = sin_en = sin_lang = 0
    for t in set(model.subjects(RDF.type, OWL.Class)) | set(model.subjects(RDF.type, OWL.ObjectProperty)) | set(model.subjects(RDF.type, OWL.DatatypeProperty)):
        if not isinstance(t, URIRef) or not str(t).startswith(own_ns):
            continue
        total += 1
        labels = [l for l in model.objects(t, RDFS.label) if isinstance(l, Literal)]
        langs = {l.language for l in labels}
        if "es" not in langs:
            sin_es += 1
        if "en" not in langs:
            sin_en += 1
        for l in labels:
            if not l.language:
                sin_lang += 1
    if total:
        missing = sin_es + sin_en
        if missing / (total * 2) > 0.05:
            cnt["C-LABELS"] += missing
            print(f"  [C-LABELS] {sin_es} terminos sin @es y {sin_en} sin @en (de {total}); {sin_lang} labels sin idioma")


def check_readme_links(cnt: Counter):
    """C-README: enlaces relativos del README existen."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(errors="replace")
    for m in re.finditer(r"\]\(([^)#?]+)(?:#[^)]*)?\)", text):
        rel = m.group(1).strip()
        if rel.startswith(("http://", "https://", "mailto:")):
            continue
        if not (ROOT / rel).exists():
            cnt["C-README"] += 1
            print(f"  [C-README] enlace roto: {rel}")


CHECKS_FATAL_ORDER = [
    "C-PARSE", "C-ONTOLOGY", "C-URIBLACKLIST", "C-SPARQL", "C-KOSSCHEME",
    "C-OWLMETA", "C-CONFIG", "C-SHAPEGHOST", "C-SHAACL", "C-LABELS", "C-README",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="ignora la baseline")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    print(f"== verify {ROOT.name} ==")
    cnt: Counter = Counter()

    model = Graph()
    model_path = None
    for cand in ("ontology/ontology.owl", "ontology/data-cube.owl"):
        if (ROOT / cand).exists():
            model_path = ROOT / cand
            break
    if model_path:
        try:
            sniff_and_parse(model_path, model)
        except Exception as e:  # noqa: BLE001
            print(f"  [C-PARSE] {model_path}: {e}")

    kos = []
    for p in iter_rdf_files("kos"):
        try:
            kos.append(sniff_and_parse(p))
        except Exception:  # noqa: BLE001  (ya reportado por C-PARSE)
            pass
    shapes = [p for p in (ROOT / "shapes").glob("*.ttl")] if (ROOT / "shapes").is_dir() else []
    own_ns = None
    if model_path:
        for s in model.subjects(RDF.type, OWL.Ontology):
            own_ns = str(s)

    check_parse(cnt)
    if model_path and len(model):
        check_single_ontology(cnt, model)
        check_owl_meta(cnt, model)
        check_labels(cnt, model, own_ns)
    check_blacklist(cnt)
    check_sparql(cnt)
    check_kos(cnt, kos)
    check_config(cnt)
    check_shape_ghosts(cnt, model, shapes)
    check_shacl(cnt, model, shapes)
    check_readme_links(cnt)

    if not cnt:
        print("Sin incidencias.")
    else:
        print("\n== resumen ==")
        for code in CHECKS_FATAL_ORDER:
            if cnt[code]:
                print(f"  {code}: {cnt[code]}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(dict(cnt), indent=2, sort_keys=True) + "\n")
        print(f"baseline actualizada: {BASELINE.relative_to(ROOT)}")
        return 0

    baseline = {}
    if BASELINE.exists() and not args.strict:
        baseline = json.loads(BASELINE.read_text())

    failed = False
    for code in CHECKS_FATAL_ORDER:
        allowed = baseline.get(code, 0)
        if cnt[code] > allowed:
            print(f"FALLO: {code} = {cnt[code]} > baseline {allowed}")
            failed = True
    print("resultado:", "FALLO" if failed else "OK")
    return 1 if failed else 0


def _try(fn):
    try:
        fn()
        return True
    except Exception:  # noqa: BLE001
        return False


if __name__ == "__main__":
    sys.exit(main())
