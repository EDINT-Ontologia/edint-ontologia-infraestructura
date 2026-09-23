"""Dimensión: higiene del repo (sin basura versionada, .gitignore)."""
import fnmatch
import subprocess

from util import PATRONES_BASURA, ROOT


def test_gitignore_presente():
    assert (ROOT / ".gitignore").exists(), "falta .gitignore"


def test_sin_basura_versionada():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    ).stdout.splitlines()
    mal = [f for f in tracked for pat in PATRONES_BASURA if fnmatch.fnmatch(f, pat)]
    assert not mal, f"ficheros basura versionados: {sorted(set(mal))[:10]}"
