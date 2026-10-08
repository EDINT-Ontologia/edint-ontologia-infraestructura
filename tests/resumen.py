#!/usr/bin/env python
"""Genera el resumen de la suite (tabla por dimensión y detalle de fallos).

Se escribe en el resumen del run (GITHUB_STEP_SUMMARY) y, si el evento es un
pull_request, se publica o actualiza un comentario en el PR.
"""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

MARCADOR = "<!-- verify-summary -->"


def limpiar_mensaje(bruto: str) -> str:
    """Descarta el volcado del assert y las rutas absolutas del runner."""
    texto = " ".join((bruto or "").split())
    texto = re.split(r"\s+assert\b", texto)[0].strip()
    texto = re.sub(r"PosixPath\('[^']*'\)", "", texto)
    texto = re.sub(r"/home/runner/\S+", "", texto)
    return re.sub(r"\s+", " ", texto).strip()[:300]


def leer_resultados(xml: str) -> tuple[list[str], dict, dict]:
    raiz = ET.parse(xml).getroot()
    orden: list[str] = []
    filas: dict[str, dict[str, int]] = {}
    fallos: dict[str, list[str]] = {}
    for tc in raiz.iter("testcase"):
        mod = (tc.get("classname") or "desconocido").rsplit(".", 1)[-1]
        if mod not in filas:
            filas[mod] = {"ok": 0, "fail": 0, "skip": 0}
            orden.append(mod)
        nodo = tc.find("failure") if tc.find("failure") is not None else tc.find("error")
        if nodo is not None:
            filas[mod]["fail"] += 1
            texto = limpiar_mensaje(nodo.get("message") or nodo.text or "")
            fallos.setdefault(mod, []).append(f"{tc.get('name')} — {texto}")
        elif tc.find("skipped") is not None:
            filas[mod]["skip"] += 1
        else:
            filas[mod]["ok"] += 1
    return orden, filas, fallos


def _sha_del_evento() -> str:
    ruta = os.environ.get("GITHUB_EVENT_PATH")
    if not ruta or not Path(ruta).exists():
        return ""
    evento = json.loads(Path(ruta).read_text())
    return ((evento.get("pull_request") or {}).get("head") or {}).get("sha", "")


def markdown(orden: list[str], filas: dict, fallos: dict) -> str:
    total = {k: sum(d[k] for d in filas.values()) for k in ("ok", "fail", "skip")}
    sha = (os.environ.get("GITHUB_SHA") or "")[:7]
    sha_pr = _sha_del_evento()[:7]
    referencia = f"commit {sha}" + (f" · PR {sha_pr}" if sha_pr else "")
    lineas = [MARCADOR, "## Resultados verify", "", referencia, "",
              "| Dimensión | Pasados | Fallos | Omitidos |", "|---|---:|---:|---:|"]
    for mod in orden:
        d = filas[mod]
        lineas.append(f"| {mod} | {d['ok']} | {d['fail']} | {d['skip']} |")
    lineas.append(f"| **TOTAL** | {total['ok']} | {total['fail']} | {total['skip']} |")
    lineas.append("")
    if total["fail"]:
        lineas.append(f"### Detalle de fallos ({total['fail']})")
        lineas.append("")
        for mod in orden:
            if mod in fallos:
                lineas.append(f"**{mod}**")
                for f in fallos[mod]:
                    lineas.append(f"- {f}")
                lineas.append("")
    else:
        lineas.append("Sin fallos.")
    return "\n".join(lineas)


def publicar_comentario(cuerpo: str) -> None:
    repo = os.environ["GITHUB_REPOSITORY"]
    evento = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    num = (evento.get("pull_request") or {}).get("number")
    if not num:
        return
    base = f"https://api.github.com/repos/{repo}"
    cabeceras = {
        "Authorization": f"token {os.environ['GH_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    req = urllib.request.Request(f"{base}/issues/{num}/comments", headers=cabeceras)
    with urllib.request.urlopen(req) as resp:
        existente = next(
            (c["url"] for c in json.load(resp) if (c.get("body") or "").startswith(MARCADOR)),
            None,
        )
    datos = json.dumps({"body": cuerpo}).encode()
    if existente:
        urllib.request.urlopen(
            urllib.request.Request(existente, data=datos, headers=cabeceras, method="PATCH")
        )
    else:
        urllib.request.urlopen(
            urllib.request.Request(f"{base}/issues/{num}/comments", data=datos, headers=cabeceras)
        )


def main() -> int:
    xml = os.environ.get("RESULTADOS", "")
    if not xml or not Path(xml).exists():
        print("::warning::La suite no generó resultados (error de infraestructura)")
        return 0
    orden, filas, fallos = leer_resultados(xml)
    cuerpo = markdown(orden, filas, fallos)
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        Path(resumen).write_text(cuerpo + "\n", encoding="utf-8")
    total_fallos = sum(d["fail"] for d in filas.values())
    total = sum(sum(d.values()) for d in filas.values())
    if total_fallos:
        print(f"::warning::{total_fallos} de {total} tests con fallos; detalle en el resumen del run")
    else:
        print(f"::notice::{total} tests, ninguno con fallos")
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        publicar_comentario(cuerpo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
