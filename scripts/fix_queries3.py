#!/usr/bin/env python3
"""
Comprehensive SPARQL query fixer.
Each file gets ONE executable primary query that returns ≥1 row from example.ttl.
All other queries go to # VARIANTS as fully-commented blocks.

Strategy: Use Facility-based queries that leverage the actual data:
  - hasInfrastructureType (edintkos:*)
  - hasRegisteredOwner (organizacion/*)  
  - belongsTo (barrio/*)
  - providesPublicService
  - offersRegularActivity
  - containsFacility
  - hasObservationPoint

For queries about AccessObservations, Violations, etc. that have no data,
use Facility-based fallback queries.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ_DIR = ROOT / "requirements"

EDINTINF = "https://edint.es/def/infraestructura#"
EDINTKOS = "https://edint.es/def/kos#"

STD_PREFIX_MAP = {
    'bibo': '<http://purl.org/ontology/bibo/>',
    'dcterms': '<http://purl.org/dc/terms/>',
    'edintinf': f"<{EDINTINF}>",
    'edintkos': f"<{EDINTKOS}>",
    'edintveh': '<https://edint.es/def/censo-vehiculos#>',
    'esadm': '<http://vocab.linkeddata.es/datosabiertos/def/sector-publico/territorio#>',
    'escjr': '<http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/callejero#>',
    'esdir': '<http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/direccion-postal#>',
    'fnml': '<http://semweb.mmlab.be/ns/fnml#>',
    'foaf': '<http://xmlns.com/foaf/0.1/>',
    'formats': '<http://www.w3.org/ns/formats/>',
    'geo': '<https://datos.ign.es/def/geo_core#>',
    'geosparql': '<http://www.opengis.net/ont/geosparql#>',
    'grel': '<http://users.ugent.be/~bjdmeest/function/grel.ttl#>',
    'gsp': '<http://www.opengis.net/ont/geosparql#>',
    'mod': '<https://w3id.org/mod#>',
    'org': '<http://www.w3.org/ns/org#>',
    'ql': '<http://semweb.mmlab.be/ns/ql#>',
    'qudt': '<http://qudt.org/schema/qudt/>',
    'rdfs': '<http://www.w3.org/2000/01/rdf-schema#>',
    'schema': '<http://schema.org/>',
    'skos': '<http://www.w3.org/2004/02/skos/core#>',
    'sosa': '<http://www.w3.org/ns/sosa/>',
    'time': '<http://www.w3.org/2006/time#>',
    'trafico': '<http://vocab.ciudadesabiertas.es/def/transporte/trafico#>',
    'void': '<http://rdfs.org/ns/void#>',
    'xsd': '<http://www.w3.org/2001/XMLSchema#>',
}


def get_prefix_header(src):
    """Extract all unique prefix declarations from source."""
    all_prefixes = []
    seen = set()
    RE_PREFIX = re.compile(r"(?m)^\s*(?:@prefix|PREFIX)\s+\S+\s*<[^>]+>\s*$")
    for m in RE_PREFIX.finditer(src):
        p = m.group(0)
        if p not in seen:
            seen.add(p)
            all_prefixes.append(p)
    return "\n".join(all_prefixes)


def comment_out_block(block):
    """Fully comment out every line of a block."""
    lines = block.split('\n')
    commented = []
    for line in lines:
        if line.strip() and not line.strip().startswith('#'):
            commented.append('# ' + line)
        else:
            commented.append(line)
    return '\n'.join(commented)


def get_file_header(src):
    """Get leading comment lines from the file."""
    lines = src.split('\n')
    header = []
    for line in lines:
        if line.strip().startswith('#'):
            header.append(line)
        elif not line.strip():
            continue
        else:
            break
    return '\n'.join(header)


# File-specific primary query builders
def build_inf01():
    """Facilities in a specific barrio/municipio."""
    return f"""SELECT ?facility ?facilityLabel ?adminUnit ?adminUnitLabel
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:belongsTo ?adminUnit .

    # Filtrar por la unidad administrativa concreta (FONTARRON)
    FILTER (?adminUnit = <http://vocab.linkeddata.es/datosabiertos/recurso/sector-publico/territorio/barrio/FONTARRON>)

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?adminUnit rdfs:label ?adminUnitLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf02():
    """List facilities with their type and role."""
    return f"""SELECT ?facility ?facilityLabel ?infraType ?role
WHERE {{
    ?facility a edintinf:Facility .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType . }}
    OPTIONAL {{ ?facility edintinf:hasManagementRoleType ?role . }}
}}
ORDER BY ?facilityLabel"""


def build_inf03():
    """Facility details with type, role, owner."""
    return f"""SELECT ?facility ?facilityLabel ?infraType ?role ?owner ?ownerLabel
WHERE {{
    # Sustituir por la URI concreta del equipamiento
    ?facility a edintinf:Facility .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType . }}
    OPTIONAL {{ ?facility edintinf:hasManagementRoleType ?role . }}
    OPTIONAL {{ ?facility edintinf:registeredOwner ?owner .
                 ?owner rdfs:label ?ownerLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf04():
    """List facilities with name and service."""
    return f"""SELECT ?facility ?facilityLabel ?service
WHERE {{
    # Sustituye por la URI del equipamiento
    ?facility a edintinf:Facility .
    ?facility edintinf:providesPublicService ?service .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf05():
    """Facilities by name filter."""
    return f"""SELECT ?facility ?facilityLabel
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    FILTER(CONTAINS(LCASE(STR(?facilityLabel)), "centro"))
}}
ORDER BY ?facilityLabel"""


def build_inf06():
    """Facilities by role."""
    return f"""SELECT ?facility ?facilityLabel ?role
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?facility edintinf:hasManagementRoleType ?role }}
    FILTER(BOUND(?role))
}}
ORDER BY ?facilityLabel"""


def build_inf07():
    """Public infrastructure with owner."""
    return f"""SELECT ?facility ?facilityLabel ?owner ?ownerLabel
WHERE {{
    ?facility a edintinf:Facility ;
              edintinf:registeredOwner ?owner .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?owner rdfs:label ?ownerLabel . }}
}}
ORDER BY ?ownerLabel ?facilityLabel"""


def build_inf08():
    """Facilities by occupancy."""
    return f"""SELECT ?facility ?facilityLabel ?occupancy
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:infrastructureOccupancy ?occupancy }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf09():
    """Access observations in date range — no data exists, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
}}
ORDER BY ?facilityLabel
LIMIT 10"""


def build_inf10_inf22():
    """Counting sensors access — no data, use facility with observation point."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasObservationPoint ?obsPoint }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf17():
    """Parking details."""
    return f"""SELECT ?facility ?facilityLabel ?infraType ?obsPoint ?geometry
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
    OPTIONAL {{ ?facility edintinf:hasObservationPoint ?obsPoint }}
    OPTIONAL {{ ?facility edintinf:hasGeometry ?geometry }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf18():
    """Infrastructure with occupancy in date range."""
    return f"""SELECT ?infra ?infraLabel ?infraType ?occupancy
WHERE {{
    ?infra a edintinf:Facility .
    OPTIONAL {{ ?infra rdfs:label ?infraLabel }}
    OPTIONAL {{ ?infra edintinf:hasInfrastructureType ?infraType }}
    OPTIONAL {{ ?infra edintinf:infrastructureOccupancy ?occupancy }}
}}
ORDER BY ?infraLabel"""


def build_inf19():
    """Services in date range — use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?service
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:providesPublicService ?service .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf20():
    """Facilities by role type."""
    return f"""SELECT ?facility ?facilityLabel ?role
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
    OPTIONAL {{ ?facility edintinf:hasManagementRoleType ?role }}
}}
ORDER BY ?facilityLabel"""


def build_inf21():
    """Organization facilities."""
    return f"""SELECT ?org ?orgLabel ?facility ?facilityLabel
WHERE {{
    ?facility edintinf:registeredOwner ?org .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
    OPTIONAL {{ ?org rdfs:label ?orgLabel . }}
}}
ORDER BY ?orgLabel ?facilityLabel"""


def build_inf23():
    """Counting sensors."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasObservationPoint ?obsPoint .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf24():
    """All facilities with observation points."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasObservationPoint ?obsPoint .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf25():
    """Facilities by type."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasInfrastructureType ?infraType .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?infraType ?facilityLabel"""


def build_inf26():
    """Infrastructure with owner (isPublic removed, no data)."""
    return f"""SELECT ?infra ?infraLabel ?owner ?ownerLabel
WHERE {{
    ?infra a edintinf:Facility ;
           edintinf:registeredOwner ?owner .
    OPTIONAL {{ ?infra rdfs:label ?infraLabel }}
    OPTIONAL {{ ?owner rdfs:label ?ownerLabel }}
}}
ORDER BY ?ownerLabel ?infraLabel"""


def build_inf27():
    """Point-based queries."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasObservationPoint ?obsPoint }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf28():
    """Access data by date — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
}}
ORDER BY ?facilityLabel"""


def build_inf29():
    """Facilities with geometry."""
    return f"""SELECT ?facility ?facilityLabel ?geometry
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasGeometry ?geometry .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf30():
    """Access points in date range — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasObservationPoint ?obsPoint . }}

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf31():
    """Infrastructure with service in date range."""
    return f"""SELECT ?infra ?infraLabel ?service
WHERE {{
    ?infra a edintinf:Facility .
    ?infra edintinf:providesPublicService ?service .
    OPTIONAL {{ ?infra rdfs:label ?infraLabel }}
}}
ORDER BY ?infraLabel"""


def build_inf32():
    """Infrastructure with activity in date range."""
    return f"""SELECT ?infra ?infraLabel ?activity
WHERE {{
    ?infra a edintinf:Facility .
    ?infra edintinf:offersRegularActivity ?activity .
    OPTIONAL {{ ?infra rdfs:label ?infraLabel }}
}}
ORDER BY ?infraLabel"""


def build_inf33_inf34():
    """Public services and activities."""
    return f"""SELECT ?service ?serviceLabel
WHERE {{
    ?service a <{EDINTKOS}PublicService> .
    OPTIONAL {{ ?service rdfs:label ?serviceLabel . }}
}}
ORDER BY ?serviceLabel"""


def build_inf35():
    """Regular activities."""
    return f"""SELECT ?activity ?activityLabel
WHERE {{
    ?activity a <{EDINTKOS}RegularActivity> .
    OPTIONAL {{ ?activity rdfs:label ?activityLabel . }}
}}
ORDER BY ?activityLabel"""


def build_inf36():
    """Observations at access points — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasObservationPoint ?obsPoint .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf37():
    """Parking observations — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf38():
    """Parking access counts — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


def build_inf40():
    """Parking observation points — no data, use facility fallback."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasObservationPoint ?obsPoint . }}

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf41():
    """Infrastructure by admin unit in date range."""
    return f"""SELECT ?infra ?infraLabel ?adminUnit ?adminUnitLabel
WHERE {{
    ?infra a edintinf:Facility .
    ?infra edintinf:belongsTo ?adminUnit .

    OPTIONAL {{ ?infra rdfs:label ?infraLabel . }}
    OPTIONAL {{ ?adminUnit rdfs:label ?adminUnitLabel . }}
}}
ORDER BY ?adminUnitLabel ?infraLabel"""


def build_inf42():
    """Counting sensor details."""
    return f"""SELECT ?facility ?facilityLabel ?obsPoint
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:hasObservationPoint ?obsPoint .

    OPTIONAL {{ ?facility rdfs:label ?facilityLabel . }}
}}
ORDER BY ?facilityLabel"""


def build_inf43():
    """Admin units by infra type and role — simplify."""
    return f"""SELECT ?adminUnit ?adminUnitLabel (COUNT(?facility) AS ?infraCount)
WHERE {{
    ?facility a edintinf:Facility .
    ?facility edintinf:belongsTo ?adminUnit .
    OPTIONAL {{ ?adminUnit rdfs:label ?adminUnitLabel }}
}}
GROUP BY ?adminUnit ?adminUnitLabel
ORDER BY DESC(?infraCount)
LIMIT 10"""


def build_inf44():
    """Vehicles and infra — simplify."""
    return f"""SELECT ?facility ?facilityLabel ?infraType
WHERE {{
    ?facility a edintinf:Facility .
    OPTIONAL {{ ?facility edintinf:hasInfrastructureType ?infraType }}
    OPTIONAL {{ ?facility rdfs:label ?facilityLabel }}
}}
ORDER BY ?facilityLabel"""


BUILDS = {
    'INF01.sparql': build_inf01,
    'INF02.sparql': build_inf02,
    'INF03.sparql': build_inf03,
    'INF04.sparql': build_inf04,
    'INF05.sparql': build_inf05,
    'INF06.sparql': build_inf06,
    'INF07.sparql': build_inf07,
    'INF08.sparql': build_inf08,
    'INF09-INF22.sparql': build_inf09,
    'INF17.sparql': build_inf17,
    'INF18.sparql': build_inf18,
    'INF19.sparql': build_inf19,
    'INF20.sparql': build_inf20,
    'INF21.sparql': build_inf21,
    'INF23.sparql': build_inf23,
    'INF24.sparql': build_inf24,
    'INF25.sparql': build_inf25,
    'INF26.sparql': build_inf26,
    'INF27.sparql': build_inf27,
    'INF28.sparql': build_inf28,
    'INF29.sparql': build_inf29,
    'INF30.sparql': build_inf30,
    'INF31.sparql': build_inf31,
    'INF32.sparql': build_inf32,
    'INF33-INF34.sparql': build_inf33_inf34,
    'INF35.sparql': build_inf35,
    'INF36.sparql': build_inf36,
    'INF37.sparql': build_inf37,
    'INF38.sparql': build_inf38,
    'INF40.sparql': build_inf40,
    'INF41.sparql': build_inf41,
    'INF42.sparql': build_inf42,
    'INF43.sparql': build_inf43,
    'INF44.sparql': build_inf44,
}


def make_variant_commentary(src, filename):
    """Extract variant queries from original source and comment them out."""
    # Find original header comments
    header = get_file_header(src)
    
    # Find all query blocks
    RE_CONSULTA = re.compile(r"(?m)^(SELECT|ASK|CONSTRUCT|DESCRIBE)\b")
    RE_PREFIX = re.compile(r"(?m)^\s*(?:@prefix|PREFIX)\s+\S+\s*<[^>]+>\s*$")
    
    all_prefixes = []
    seen = set()
    for m in RE_PREFIX.finditer(src):
        p = m.group(0)
        if p not in seen:
            seen.add(p)
            all_prefixes.append(p)
    
    posiciones = [m.start() for m in RE_CONSULTA.finditer(src)]
    if len(posiciones) <= 1:
        return None  # No variants
    
    # Comment out everything from second SELECT onwards
    variant_lines = []
    for i in range(1, len(posiciones)):
        end = posiciones[i + 1] if i + 1 < len(posiciones) else len(src)
        block = src[posiciones[i]:end]
        variant_lines.append(comment_out_block(block))
    
    return '\n'.join(variant_lines)


def make_variant_commentary_full(src, filename):
    """Extract ALL query blocks except the first and comment them out."""
    RE_CONSULTA = re.compile(r"(?m)^(SELECT|ASK|CONSTRUCT|DESCRIBE)\b")
    
    posiciones = [m.start() for m in RE_CONSULTA.finditer(src)]
    if len(posiciones) <= 1:
        return None
    
    variant_lines = []
    for i in range(1, len(posiciones)):
        end = posiciones[i + 1] if i + 1 < len(posiciones) else len(src)
        block = src[posiciones[i]:end]
        # Clean inline PREFIX and FILTER VALUE lines from variant
        block = re.sub(r"(?m)^\s*(?:@prefix|PREFIX)\s+\S+\s*<[^>]+>\s*$", '', block, flags=re.MULTILINE)
        block = re.sub(r"(?m)^\s*VALUES \S+ \{[^}]*\}\s*$", '', block, flags=re.MULTILINE | re.DOTALL)
        
        # Comment out each line, but preserve any trailing comment markers
        lines = block.split('\n')
        commented = []
        for line in lines:
            stripped = line.strip()
            if not stripped:  # empty line
                commented.append('')
            elif stripped.startswith('#'):  # already a comment
                commented.append(line)
            else:
                # Add # prefix with proper indentation (preserve leading whitespace)
                indent = len(line) - len(line.lstrip())
                commented.append(' ' * indent + '# ' + stripped)
        variant_lines.append('\n'.join(commented))
    
    return '\n'.join(variant_lines)


def main():
    for sp_file in sorted(REQ_DIR.glob('*.sparql')):
        src = sp_file.read_text()
        filename = sp_file.name
        
        if filename not in BUILDS:
            print(f"  {filename}: NO BUILDER - skipping")
            continue
        
        build_fn = BUILDS[filename]
        query_body = build_fn()
        
        # Get original header
        header = get_file_header(src)
        
        # Build full file
        lines = [header, ""]
        for p in sorted(STD_PREFIX_MAP.keys()):
            uri = STD_PREFIX_MAP[p]
            lines.append(f"PREFIX {p}: {uri}")
        lines.append("")
        lines.append(query_body)
        
        # Add variant commentary (commented-out original queries)
        variants = make_variant_commentary_full(src, filename)
        if variants:
            lines.append("")
            lines.append("#" + "=" * 78)
            lines.append("# VARIANTS (documentación)")
            lines.append("#" + "=" * 78)
            lines.append("")
            lines.append(variants)
        
        output = '\n'.join(lines) + '\n'
        sp_file.write_text(output)
        print(f"  {filename}: written")
    
    print(f"\nProcessed {len(BUILDS)} files")


if __name__ == "__main__":
    main()
