"""Dimensión: higiene del repo (sin basura versionada, .gitignore)."""
import subprocess

from util import ROOT

PATRONES_MALOS = ["*.bak", "*.orig", "*.rej", ".DS_Store", "__pycache__/*", "*.pyc", ".pytest_cache/*", ".venv/*", ".shacl_*.ttl"]


def test_gitignore_presente():
    assert (ROOT / ".gitignore").exists(), "falta .gitignore"


def test_sin_basura_versionada():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    ).stdout.splitlines()
    import fnmatch
    mal = [f for f in tracked for pat in PATRONES_MALOS if fnmatch.fnmatch(f, pat)]
    assert not mal, f"ficheros basura versionados: {sorted(set(mal))[:10]}"
