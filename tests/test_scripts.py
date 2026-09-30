"""Dimensión: scripts de shell y workflows con sintaxis válida."""
import subprocess

import pytest

from util import ROOT


def scripts():
    d = ROOT / "scripts"
    return sorted(d.glob("*.sh")) if d.is_dir() else []


def workflows():
    d = ROOT / ".github" / "workflows"
    return sorted(d.glob("*.yml")) + sorted(d.glob("*.yaml")) if d.is_dir() else []


@pytest.mark.parametrize("sh", scripts(), ids=lambda p: p.name)
def test_shell_sintaxis(sh):
    r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
    assert r.returncode == 0, f"bash -n falla: {r.stderr.strip()[:200]}"


@pytest.mark.parametrize("yml", workflows(), ids=lambda p: p.name)
def test_workflow_yaml_valido(yml):
    import yaml
    doc = yaml.safe_load(yml.read_text(errors="replace"))
    assert isinstance(doc, dict) and "jobs" in doc, "YAML sin clave jobs"
