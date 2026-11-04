"""Instalador separado para o workflow Axo_Anima_Personagem_Refino.json.

No Colab Axo: interrompa a célula de execução do ComfyUI, envie este arquivo
para /content pelo painel Arquivos e execute em uma nova célula:
    %run /content/Instalar_Dependencias_Personagem.py
Depois execute Restart no notebook Axo e recarregue a página do ComfyUI.
O notebook atualizado instala estas dependências automaticamente quando
ENABLE_CHARACTER_WORKFLOW está ativado; este arquivo também permite a instalação manual.
Não é necessário instalar ou habilitar o ComfyUI Manager.
"""
import json
import os
from pathlib import Path
import struct
import subprocess
import urllib.request

COMFY_DIR = Path('/content/axo-comfyui')
COMFY_PYTHON = Path('/content/axo-comfy-runtime-py312/bin/python')
PACKAGES = (
    ('ComfyUI-Impact-Pack', 'https://github.com/ltdrdata/ComfyUI-Impact-Pack.git',
     'eace4a9059908330936c6514f35f5e0c84935394'),
    ('ComfyUI-Impact-Subpack', 'https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git',
     '50c7b71a6a224734cc9b21963c6d1926816a97f1'),
    ('ComfyUI-Anima-Ref-Adapter', 'https://github.com/ArcAnima/ComfyUI-Anima-Ref-Adapter.git',
     '99c222e1c2da472f4b514583b2dbd1b5afb4bdd9'),
)


def environment():
    env = os.environ.copy()
    for key in ('PIP_CONSTRAINT', 'REQS_FILE', 'PYTHONHOME', 'PYTHONPATH'):
        env.pop(key, None)
    env['VIRTUAL_ENV'] = str(COMFY_PYTHON.parent.parent)
    env['PATH'] = str(COMFY_PYTHON.parent) + os.pathsep + env.get('PATH', '')
    env['COMFYUI_PATH'] = str(COMFY_DIR)
    return env


def run(args, cwd=None):
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=environment(), check=True)


def checkout(name, repo, revision):
    folder = COMFY_DIR / 'custom_nodes' / name
    if not folder.exists():
        run(['git', 'clone', '--depth', '1', repo, folder])
    if not (folder / '.git').is_dir():
        raise RuntimeError(f'{folder}: pasta existente sem Git. Preserve seus arquivos antes de instalar.')
    head = subprocess.check_output(['git', '-C', str(folder), 'rev-parse', 'HEAD'], text=True).strip()
    if head != revision:
        dirty = subprocess.check_output(['git', '-C', str(folder), 'status', '--porcelain'], text=True).strip()
        if dirty:
            raise RuntimeError(f'{name}: há alterações locais; elas não serão sobrescritas.')
        run(['git', '-C', folder, 'fetch', '--depth', '1', 'origin', revision])
        run(['git', '-C', folder, 'checkout', '--detach', revision])
    print(f'Extensão pronta: {name}', flush=True)
    return folder


def valid_model(path, safetensors):
    if not path.is_file() or path.stat().st_size < 1_000_000:
        return False
    try:
        with path.open('rb') as handle:
            prefix = handle.read(8)
            if not safetensors:
                return prefix.startswith((b'PK\x03\x04', b'\x80'))
            size = struct.unpack('<Q', prefix)[0]
            if not 2 <= size <= min(100_000_000, path.stat().st_size - 8):
                return False
            header = json.loads(handle.read(size))
            tensors = [value for key, value in header.items() if key != '__metadata__']
            payload_size = path.stat().st_size - size - 8
            return bool(tensors) and all(
                isinstance(tensor, dict) and isinstance(tensor.get('data_offsets'), list)
                and len(tensor['data_offsets']) == 2
                and 0 <= tensor['data_offsets'][0] <= tensor['data_offsets'][1] <= payload_size
                for tensor in tensors)
    except (OSError, ValueError, TypeError, struct.error):
        return False


def download(url, path, safetensors=False):
    if valid_model(path, safetensors):
        print(f'Reutilizando: {path}', flush=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + '.part')
    request = urllib.request.Request(url, headers={'User-Agent': 'Axo-Image-Studio'})
    try:
        print(f'Baixando: {path.name}', flush=True)
        with urllib.request.urlopen(request, timeout=120) as response, partial.open('wb') as handle:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type or 'application/json' in content_type:
                raise RuntimeError(f'O servidor retornou uma página em vez do modelo {path.name}.')
            total = int(response.headers.get('Content-Length', 0))
            received = 0
            while chunk := response.read(1024 * 1024):
                handle.write(chunk)
                received += len(chunk)
            if total and received != total:
                raise RuntimeError(f'Download incompleto: {path.name}')
        if not valid_model(partial, safetensors):
            raise RuntimeError(f'Arquivo inválido: {path.name}. Execute o instalador novamente.')
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)


def model_root(config):
    shared = config.get('axo') or {}
    base = shared.get('base_path')
    if base:
        path = Path(os.path.expandvars(os.path.expanduser(base)))
        return path if path.is_absolute() else COMFY_DIR / path
    return COMFY_DIR / 'models'


def main(standalone=True):
    if not (COMFY_DIR / 'main.py').is_file() or not COMFY_PYTHON.is_file():
        raise RuntimeError('Execute este arquivo no Colab Axo após instalar o ComfyUI. O ambiente esperado não foi encontrado.')
    # Avoid changing dependencies while the running server has them imported.
    import socket
    with socket.socket() as sock:
        sock.settimeout(1)
        if sock.connect_ex(('127.0.0.1', 8188)) == 0:
            raise RuntimeError('Interrompa primeiro a célula que executa o ComfyUI; depois execute este instalador.')
    config_path = COMFY_DIR / 'extra_model_paths.yaml'
    # Read existing YAML in ComfyUI's own Python (PyYAML is already installed there).
    raw = subprocess.check_output([str(COMFY_PYTHON), '-c',
        'import json,sys,yaml; from pathlib import Path; p=Path(sys.argv[1]); '
        'print(json.dumps((yaml.safe_load(p.read_text()) or {}) if p.is_file() else {}))',
        str(config_path)], env=environment(), text=True)
    config = json.loads(raw)
    models = model_root(config)
    if not models.is_dir():
        raise RuntimeError(f'Pasta de modelos indisponível: {models}. Se usa Drive, monte-o primeiro.')

    folders = [checkout(*package) for package in PACKAGES]
    work = COMFY_DIR / 'axo-character-setup'
    work.mkdir(exist_ok=True)
    constraints = work / 'constraints.txt'
    constraints.write_text('torch==2.8.0\ntorchvision==0.23.0\ntorchaudio==2.8.0\n', encoding='utf-8')
    # SAM2 is optional in this pinned Impact version and unused by the workflow.
    # Install all other declared requirements without compiling optional SAM2.
    requirements = []
    for folder in folders:
        file = folder / 'requirements.txt'
        if file.is_file():
            requirements.extend(line for line in file.read_text().splitlines()
                                if line.strip() and 'facebookresearch/sam2' not in line)
    requirements += ['ultralytics==8.3.253', 'huggingface-hub']
    requirement_file = work / 'requirements.txt'
    requirement_file.write_text('\n'.join(requirements) + '\n', encoding='utf-8')
    run([COMFY_PYTHON, '-m', 'pip', 'install', '-c', constraints, '-r', requirement_file])
    run([COMFY_PYTHON, '-m', 'pip', 'check'])
    # Complete Impact's config initialization without its unrelated SAM downloads.
    run([COMFY_PYTHON, '-c',
         'import sys; sys.path.insert(0,sys.argv[1]); import impact.config; impact.config.write_config()',
         folders[0] / 'modules'])

    for filename in ('face_yolov8n.pt', 'hand_yolov8n.pt'):
        download('https://huggingface.co/Bingsu/adetailer/resolve/main/' + filename,
                 models / 'adetailer' / filename)
    download('https://huggingface.co/ElectronGirl/anima-ref-adapter/resolve/main/'
             'anima_ref_adapter_v2_r64.safetensors',
             models / 'Lora/anima_ref_adapter_v2_r64.safetensors', safetensors=True)
    config['axo_character'] = {'base_path': str(models), 'is_default': True,
                               'ultralytics_bbox': 'adetailer', 'loras': 'Lora'}
    backup = config_path.with_name('extra_model_paths.before-character.yaml')
    if config_path.is_file() and not backup.exists():
        backup.write_bytes(config_path.read_bytes())
    # JSON is a YAML subset, preserving every existing mapping.
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
    print('\nDependências e modelos do workflow de personagem instalados.')
    if standalone:
        print('Execute Restart no notebook Axo e recarregue a página do ComfyUI.')
        print('Reabra o mesmo workflow. Se os nós ainda aparecerem ausentes, confira comfy.log.')
    print('Anima base v1.0, Qwen encoder e Qwen Image VAE continuam necessários.')


if __name__ == '__main__':
    main()
