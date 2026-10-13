"""Verify the notebook includes exactly the source files shipped in the repository."""
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_notebook_matches_sources():
    subprocess.run([sys.executable, 'tools/build_notebook.py', '--check'], cwd=ROOT, check=True)
    notebook = json.loads((ROOT / 'Axo_Image_Studio.ipynb').read_text(encoding='utf-8'))
    source = ''.join(notebook['cells'][2]['source'])
    assignment = next(node for node in ast.parse(source).body
                      if isinstance(node, ast.Assign)
                      and any(getattr(t, 'id', '') == 'AXO_EXTENSION_FILES' for t in node.targets))
    files = ast.literal_eval(assignment.value)
    base = ROOT / 'extension'
    expected = {p.relative_to(base).as_posix(): p.read_text(encoding='utf-8')
                for p in base.rglob('*')
                if p.is_file() and p.suffix in {'.py', '.js', '.css', '.b64', '.yaml'}}
    assert files == expected


def test_distributed_notebook_has_no_saved_runtime_outputs_or_token():
    notebook = json.loads((ROOT / 'Axo_Image_Studio.ipynb').read_text(encoding='utf-8'))
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            assert cell['outputs'] == [] and cell['execution_count'] is None
    tree = ast.parse((ROOT / 'axo_launcher.py').read_text(encoding='utf-8'))
    token = next(node for node in tree.body if isinstance(node, ast.Assign)
                 and any(getattr(t, 'id', '') == 'CIVITAI_TOKEN' for t in node.targets))
    assert ast.literal_eval(token.value) == ''
