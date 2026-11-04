"""Embed maintained sources into the standalone Colab notebook."""
import argparse
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'Axo_Image_Studio.ipynb'


def build():
    notebook = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
    source = (ROOT / 'axo_launcher.py').read_text(encoding='utf-8')
    assignment = next(
        node for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and any(getattr(target, 'id', '') == 'AXO_EXTENSION_FILES' for target in node.targets)
    )
    base = ROOT / 'extension'
    files = {
        path.relative_to(base).as_posix(): path.read_text(encoding='utf-8')
        for path in sorted(base.rglob('*'))
        if path.is_file() and path.suffix in {'.py', '.js', '.css', '.b64'}
    }
    lines = source.splitlines(keepends=True)
    lines[assignment.lineno - 1:assignment.end_lineno] = [
        'AXO_EXTENSION_FILES = ' + repr(files) + '\n'
    ]
    comfy_files = {p.name: p.read_text(encoding='utf-8')
                   for p in sorted((ROOT / 'comfy_backend').iterdir())
                   if p.is_file() and p.suffix in {'.py', '.js', '.json'}}
    comfy_files['character_setup.py'] = (ROOT / 'workflows/Instalar_Dependencias_Personagem.py').read_text(encoding='utf-8')
    comfy_files['character.json'] = (ROOT / 'workflows/Axo_Anima_Personagem_Refino.json').read_text(encoding='utf-8')
    embedded = ''.join(lines).replace(
        'AXO_COMFY_FILES = None  # Embedded by tools/build_notebook.py',
        'AXO_COMFY_FILES = ' + repr(comfy_files))
    launch_cells = [cell for cell in notebook['cells']
                    if cell['cell_type'] == 'code'
                    and 'AXO_EXTENSION_FILES' in ''.join(cell['source'])]
    if len(launch_cells) != 1:
        raise ValueError('Expected one installation cell in the notebook.')
    launch_cells[0]['source'] = embedded.splitlines(keepends=True)
    launch_cells[0].setdefault('metadata', {})['id'] = 'axo-install-launch'
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    return json.dumps(notebook, ensure_ascii=False, indent=1) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without modifying files.')
    args = parser.parse_args()
    built = build()
    if args.check:
        if NOTEBOOK.read_text(encoding='utf-8') != built:
            parser.exit(1, 'Notebook out of date. Run: python tools/build_notebook.py\n')
        print('Notebook and maintained sources are synchronized.')
    else:
        NOTEBOOK.write_text(built, encoding='utf-8')
        print(f'Updated {NOTEBOOK.name}')


if __name__ == '__main__':
    main()
