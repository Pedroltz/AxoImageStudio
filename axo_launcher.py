#@title ▶ Install and launch Axo Image Studio — Forge Neo { display-mode: "form" }
LANGUAGE = 'pt-BR' #@param ['en', 'pt-BR']
START_WITH = 'SDXL' #@param ['SDXL', 'Anima']
USE_GOOGLE_DRIVE = False #@param {type:'boolean'}
DOWNLOAD_SDXL_BASE = True #@param {type:'boolean'}
DOWNLOAD_ANIMA_BASE = True #@param {type:'boolean'}
DOWNLOAD_CONTROLNET_SDXL = True #@param {type:'boolean'}
DOWNLOAD_ANIMA_POSE = True #@param {type:'boolean'}
PRELOAD_POSE_DETECTORS = True #@param {type:'boolean'}
ENABLE_GALLERY = True #@param {type:'boolean'}
LOW_VRAM = True #@param {type:'boolean'}
ENABLE_ADETAILER_BY_DEFAULT = True #@param {type:'boolean'}
FORCE_FP32 = False #@param {type:'boolean'}
ENABLE_PROMPT_ENHANCER = False #@param {type:'boolean'}
PROMPT_ENHANCER_BACKEND = 'local' #@param ['local', 'external']
PROMPT_ENHANCER_API_URL = 'http://127.0.0.1:11434' #@param {type:'string'}
PROMPT_ENHANCER_MODEL = 'huihui_ai/qwen3.5-abliterated:9b' #@param {type:'string'}
PROMPT_ENHANCER_BASE = 'Auto' #@param ['Auto', 'Axo SDXL - PT-BR', 'Axo Anima - PT-BR', 'Default']

import ast
import io
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
from urllib.parse import urlparse

WEBUI = Path('/content/axo-forge-webui')
EXTENSIONS = WEBUI / 'extensions'
RUNTIME = Path('/content/axo-forge-runtime-py312')
PYTHON = RUNTIME / 'bin/python'
ROOT = Path('/content/axo-forge-studio')
MODELS = ROOT / 'models'
AXO_OUTPUT_ROOT = ROOT / 'outputs'
FORGE_REPO = 'https://github.com/Haoming02/sd-webui-forge-classic.git'
FORGE_REVISION = 'bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3'
EXTENSION_REVISIONS = {
    'ADetailer-Neo': ('https://github.com/Haoming02/ADetailer-Neo.git', 'af228eba7a3f3691a25bcd1fc94aa95e600dd3e6'),
    'sd-webui-civbrowser': ('https://github.com/SignalFlagZ/sd-webui-civbrowser.git', '7c9c32040722ee125cebb9bc3c9454322b14a2a3'),
}
PROMPT_ENHANCER_NAME = 'sd-webui-prompt-enhancer'
PROMPT_ENHANCER_REPO = 'https://github.com/Gunther-Schulz/sd-webui-prompt-enhancer.git'
PROMPT_ENHANCER_REVISION = '349f28e61780472816b9f688dc2af635eee35e8f'
OLLAMA_VERSION = 'v0.40.3'
OLLAMA_HOME = Path('/content/axo-ollama')
CIVITAI_TOKEN = ''
NOTICES = []
PROCESSES = globals().get('AXO_FORGE_PROCESSES', [])
GPU_BF16 = False


def child_environment(overrides=None):
    env = os.environ.copy()
    if overrides:
        env.update(overrides)
    env.update(MPLBACKEND='Agg', PYTHONUNBUFFERED='1',
               GRADIO_ANALYTICS_ENABLED='False', WEBUI_LAUNCH_LIVE_OUTPUT='1',
               AXO_OUTPUT_ROOT=str(AXO_OUTPUT_ROOT), AXO_LANGUAGE=LANGUAGE,
               AXO_GALLERY_CACHE='/content/axo-forge-gallery-cache',
               AXO_MODEL_ROOT=str(MODELS), AXO_ENABLE_GALLERY='1' if ENABLE_GALLERY else '0',
               AXO_ADETAILER_DEFAULT='1' if ENABLE_ADETAILER_BY_DEFAULT else '0')
    if ENABLE_PROMPT_ENHANCER:
        env['PROMPT_ENHANCER_LOCAL'] = ','.join(map(str, (
            ROOT / 'prompt-enhancer-axo', ROOT / 'prompt-enhancer')))
        env['PROMPT_ENHANCER_STALL_TIMEOUT'] = '60'
        env['PROMPT_ENHANCER_MAX_TIME'] = '300'
    if PYTHON.is_file():
        env['VIRTUAL_ENV'] = str(RUNTIME)
        env['PATH'] = str(RUNTIME / 'bin') + ':' + env.get('PATH', '')
    constraint = ROOT / 'constraints.txt'
    if constraint.is_file():
        env['PIP_CONSTRAINT'] = str(constraint)
    # Do not inherit A1111 or another notebook's dependency overrides.
    for key in ('REQS_FILE', 'TORCH_COMMAND', 'GRADIO_PACKAGE', 'COMMANDLINE_ARGS', 'PYTHONPATH', 'PYTHONHOME'):
        env.pop(key, None)
    compat = ROOT / 'forge-requirements.txt'
    if compat.is_file():
        env['REQS_FILE'] = str(compat)
    return env


def run(args, cwd=None, **kwargs):
    env = child_environment(kwargs.pop('env', None))
    with subprocess.Popen([str(x) for x in args], cwd=cwd, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding='utf-8', errors='replace', bufsize=1,
                          **kwargs) as process:
        tail = []
        try:
            for line in process.stdout:
                print(line, end='', flush=True)
                tail.append(line)
                tail = tail[-40:]
            status = process.wait()
        except BaseException:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    if status:
        raise RuntimeError(f'Command failed (exit {status}): {args[0]}\n' + ''.join(tail))


def stop():
    for process in reversed(PROCESSES):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    PROCESSES.clear()


def clone_at(repo, folder, revision=None, branch=None):
    folder = Path(folder)
    if not folder.exists():
        args = ['git', 'clone', '--depth', '1']
        if branch:
            args += ['--branch', branch]
        run(args + [repo, folder])
    if not (folder / '.git').is_dir():
        raise RuntimeError(f'{folder.name}: existing folder is not a Git checkout.')
    current = subprocess.check_output(['git', '-C', str(folder), 'rev-parse', 'HEAD'], text=True).strip()
    if revision and current != revision:
        changes = subprocess.check_output(['git', '-C', str(folder), 'status', '--porcelain'], text=True).strip()
        if changes:
            raise RuntimeError(f'{folder.name}: preserve local changes before changing its revision.')
        run(['git', '-C', folder, 'fetch', '--depth', '1', 'origin', revision])
        run(['git', '-C', folder, 'checkout', '--detach', revision])
    print(f'{folder.name}: {revision or current}', flush=True)


def prepare_paths():
    global ROOT, MODELS, AXO_OUTPUT_ROOT
    if USE_GOOGLE_DRIVE:
        from google.colab import drive
        drive.mount('/content/drive', force_remount=False)
        ROOT = Path('/content/drive/MyDrive/Axo-Image-Studio-Forge')
    MODELS = ROOT / 'models'
    AXO_OUTPUT_ROOT = ROOT / 'outputs'
    for name in ('Stable-diffusion', 'Lora', 'VAE', 'text_encoder', 'ControlNet',
                 'ControlNetPreprocessor', 'adetailer', 'ESRGAN', 'embeddings'):
        (MODELS / name).mkdir(parents=True, exist_ok=True)
    AXO_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    # Pin shared packages, while keeping Neo's own NumPy/OpenCV requirements.
    # MediaPipe legacy Solutions is not used: pose uses DWPose, detailers use YOLO.
    (ROOT / 'constraints.txt').write_text(
        'torch==2.8.0\ntorchvision==0.23.0\nultralytics==8.3.253\nmediapipe==0.10.35\n'
        'gradio==4.40.0\nhuggingface-hub==0.36.2\nPillow==10.4.0\npillow-heif==0.18.0\n'
    )


def check_gpu():
    if not Path('/content').is_dir() or not shutil.which('nvidia-smi'):
        raise RuntimeError('Open in Google Colab: Runtime → Change runtime type → GPU.')
    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                            capture_output=True, text=True, timeout=30)
    if result.returncode or not result.stdout.strip():
        raise RuntimeError('A GPU runtime is required.')
    print('GPU:', result.stdout.strip(), flush=True)
    with socket.socket() as sock:
        sock.settimeout(1)
        if sock.connect_ex(('127.0.0.1', 7860)) == 0:
            raise RuntimeError('Port 7860 is busy. Stop the other notebook before launching Forge.')


def prepare_webui():
    clone_at(FORGE_REPO, WEBUI, FORGE_REVISION, 'neo')
    EXTENSIONS.mkdir(parents=True, exist_ok=True)
    required = (
        'backend/diffusion_engine/anima.py',
        'extensions-builtin/sd_forge_controlnet/scripts/controlnet.py',
        'extensions-builtin/sd_forge_controlllite/scripts/forge_controllllite.py',
    )
    for relative in required:
        if not (WEBUI / relative).is_file():
            raise RuntimeError('Forge checkout lacks required Anima/ControlNet support: ' + relative)
    # Gradio 4.40 requires Pillow <11. Resolve that declared dependency
    # explicitly instead of installing an inconsistent environment.
    requirements = (WEBUI / 'requirements.txt').read_text()
    requirements = re.sub(r'^Pillow[^\n]*', 'Pillow==10.4.0', requirements, flags=re.M)
    requirements = re.sub(r'^pillow-heif[^\n]*', 'pillow-heif==0.18.0', requirements, flags=re.M)
    (ROOT / 'forge-requirements.txt').write_text(requirements)
    for name, (repo, revision) in EXTENSION_REVISIONS.items():
        clone_at(repo, EXTENSIONS / name, revision)
    if LANGUAGE == 'pt-BR':
        clone_at('https://github.com/M-art-ucci/stable-diffusion-webui-localization-pt_BR.git',
                 EXTENSIONS / 'axo-localization-pt-BR')
    prepare_prompt_enhancer()
    install_axo_workspace()


def prepare_prompt_enhancer():
    if not ENABLE_PROMPT_ENHANCER:
        return
    if PROMPT_ENHANCER_BACKEND not in {'local', 'external'}:
        raise ValueError('Prompt Enhancer backend must be local or external.')
    parsed = urlparse(PROMPT_ENHANCER_API_URL)
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname
            or parsed.path not in {'', '/'} or parsed.query or parsed.fragment
            or parsed.username or parsed.password):
        raise ValueError('Use an Ollama base URL, without credentials or an API path.')
    if not PROMPT_ENHANCER_MODEL.strip() or PROMPT_ENHANCER_MODEL.startswith('-'):
        raise ValueError('Choose a nonempty Ollama model name.')
    if PROMPT_ENHANCER_BACKEND == 'local' and PROMPT_ENHANCER_API_URL.rstrip('/') != 'http://127.0.0.1:11434':
        raise ValueError('Local Ollama uses http://127.0.0.1:11434; select external for another URL.')
    if PROMPT_ENHANCER_BASE not in {'Auto', 'Axo SDXL - PT-BR', 'Axo Anima - PT-BR', 'Default'}:
        raise ValueError('Choose a supported Prompt Enhancer base.')
    base = PROMPT_ENHANCER_BASE
    if base == 'Auto':
        base = 'Axo Anima - PT-BR' if START_WITH == 'Anima' else 'Axo SDXL - PT-BR'
    clone_at(PROMPT_ENHANCER_REPO, EXTENSIONS / PROMPT_ENHANCER_NAME, PROMPT_ENHANCER_REVISION)
    # Upstream has hardcoded defaults, not environment settings. Adapt their
    # assignments and Base UI defaults; fail if the pinned contract changes.
    script = EXTENSIONS / PROMPT_ENHANCER_NAME / 'scripts/prompt_enhancer.py'
    source = script.read_text(encoding='utf-8')
    for key, value in {'DEFAULT_API_URL': PROMPT_ENHANCER_API_URL.rstrip('/'),
                       'DEFAULT_MODEL': PROMPT_ENHANCER_MODEL}.items():
        source, count = re.subn(r'^' + key + r' = [^\n]*',
                               lambda match: key + ' = ' + repr(value), source, flags=re.M)
        if count != 1:
            raise RuntimeError('Prompt Enhancer default assignment changed: ' + key)
    # Neo's saved-dropdown validator compares tuple labels rather than values.
    # Seed the actual Base value too, so decorated labels cannot block Auto.
    patterns = (
        (r'(base = gr\.Dropdown\([^\n]*?value=)[^,\n]+', repr(base)),
        (r'(base_description = gr\.HTML\(value=_base_description_html\()[^)]*', repr(base)),
    )
    for pattern, value in patterns:
        source, count = re.subn(pattern, lambda match: match.group(1) + value, source)
        if count != 1:
            raise RuntimeError('Prompt Enhancer Base UI contract changed.')
    script.write_text(source, encoding='utf-8')
    (ROOT / 'prompt-enhancer').mkdir(parents=True, exist_ok=True)
    managed = ROOT / 'prompt-enhancer-axo'
    managed.mkdir(parents=True, exist_ok=True)
    files = globals().get('AXO_EXTENSION_FILES')
    for name in ('_bases.yaml', '_prompts.yaml'):
        relative = 'assets/prompt-enhancer/' + name
        content = (files[relative] if files is not None else
                   (Path(__file__).resolve().parent / 'extension' / relative).read_text(encoding='utf-8'))
        (managed / name).write_text(content, encoding='utf-8')
    # ui-config.json overrides component defaults on subsequent launches.
    path = WEBUI / 'ui-config.json'
    config = json.loads(path.read_text()) if path.is_file() else {}
    for tab in ('txt2img', 'img2img'):
        for field, value in {'API URL': PROMPT_ENHANCER_API_URL.rstrip('/'),
                             'Model': PROMPT_ENHANCER_MODEL, 'Base': base}.items():
            config[f'customscript/prompt_enhancer.py/{tab}/{field}/value'] = value
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2))


def check_prompt_backend():
    base = PROMPT_ENHANCER_API_URL.rstrip('/')
    response = requests.get(base + '/api/tags', timeout=10)
    response.raise_for_status()
    models = {item['name'] for item in response.json().get('models', [])}
    selected = PROMPT_ENHANCER_MODEL
    if selected not in models and selected + ':latest' not in models:
        raise RuntimeError('Ollama model unavailable: ' + selected + '. Pull it on the server first.')


def start_prompt_backend():
    if not ENABLE_PROMPT_ENHANCER:
        return
    if PROMPT_ENHANCER_BACKEND == 'external':
        check_prompt_backend()
        return
    with socket.socket() as sock:
        sock.settimeout(1)
        if sock.connect_ex(('127.0.0.1', 11434)) == 0:
            raise RuntimeError('Port 11434 is busy. Select external to use an existing Ollama server.')
    binary = OLLAMA_HOME / 'bin/ollama'
    marker = OLLAMA_HOME / 'axo-version'
    if not binary.is_file() or not marker.is_file() or marker.read_text() != OLLAMA_VERSION:
        OLLAMA_HOME.mkdir(parents=True, exist_ok=True)
        archive = OLLAMA_HOME / 'ollama.tar.zst'
        urllib.request.urlretrieve(
            f'https://github.com/ollama/ollama/releases/download/{OLLAMA_VERSION}/ollama-linux-amd64.tar.zst', archive)
        digest = hashlib.sha256()
        with archive.open('rb') as downloaded:
            for chunk in iter(lambda: downloaded.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != 'ce6f8b671a699bf1ebafb28d60dbbabf4f37b30b499145fa308a8ba72de021d6':
            archive.unlink()
            raise RuntimeError('Ollama archive checksum mismatch; rerun to download again.')
        # Colab's GNU tar uses the zstd executable for this official archive.
        run(['apt-get', 'install', '-y', 'zstd'])
        run(['tar', '--zstd', '-xf', archive, '-C', OLLAMA_HOME])
        archive.unlink()
        marker.write_text(OLLAMA_VERSION)
    env = child_environment({'OLLAMA_HOST': '127.0.0.1:11434',
        'OLLAMA_MODELS': str(MODELS / 'Ollama'), 'OLLAMA_KEEP_ALIVE': '0',
        'OLLAMA_NO_CLOUD': '1', 'CUDA_VISIBLE_DEVICES': '-1', 'ROCR_VISIBLE_DEVICES': '-1'})
    with (ROOT / 'ollama.log').open('a') as log:
        process = subprocess.Popen([str(binary), 'serve'], env=env, stdout=log, stderr=subprocess.STDOUT)
    PROCESSES.append(process)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('Ollama exited. Inspect ollama.log.')
        try:
            response = requests.get(PROMPT_ENHANCER_API_URL.rstrip('/') + '/api/version', timeout=2)
            if response.ok:
                break
        except requests.RequestException:
            pass
        time.sleep(1)
    else:
        raise RuntimeError('Ollama startup timed out. Inspect ollama.log.')
    run([binary, 'pull', PROMPT_ENHANCER_MODEL], env=env)
    check_prompt_backend()


def install_dependencies():
    global GPU_BF16
    run([PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    # CUDA 12.6 wheels support T4 as well as newer Colab GPUs.
    run([PYTHON, '-m', 'pip', 'install', 'torch==2.8.0', 'torchvision==0.23.0',
         '--index-url', 'https://download.pytorch.org/whl/cu126'])
    run([PYTHON, '-m', 'pip', 'install', '-r', ROOT / 'forge-requirements.txt',
         'gradio==4.40.0', 'gradio_rangeslider==0.0.8', 'requests', 'colorama',
         'Send2Trash', 'ultralytics==8.3.253', 'mediapipe==0.10.35',
         'matplotlib', 'onnxruntime', 'timm', 'addict', 'ftfy', 'fvcore', 'svglib', 'yapf', 'onnx'])
    if ENABLE_PROMPT_ENHANCER:
        run([PYTHON, '-m', 'pip', 'install', 'PyYAML==6.0.2'])
    # Run the upstream startup installers before attempting a public launch.
    run([PYTHON, '-u', 'launch.py', '--model-ref', MODELS,
         '--skip-python-version-check', '--exit'], cwd=WEBUI)
    run([PYTHON, '-m', 'pip', 'check'])
    probe = subprocess.check_output([str(PYTHON), '-c',
        'import json,torch;assert torch.cuda.is_available(),"CUDA unavailable";'
        'print(json.dumps({"gpu":torch.cuda.get_device_name(0),'
        '"bf16":torch.cuda.is_bf16_supported(),"torch":torch.__version__}))'],
        env=child_environment(), text=True)
    data = json.loads(probe.strip().splitlines()[-1])
    GPU_BF16 = bool(data['bf16'])
    print('Runtime:', data, flush=True)
    (ROOT / 'runtime-info.json').write_text(json.dumps({
        **data, 'forge_revision': FORGE_REVISION, 'extensions': EXTENSION_REVISIONS,
        'python': str(PYTHON), 'language': LANGUAGE,
        'prompt_enhancer': {'enabled': ENABLE_PROMPT_ENHANCER,
            'revision': PROMPT_ENHANCER_REVISION, 'backend': PROMPT_ENHANCER_BACKEND,
            'model': PROMPT_ENHANCER_MODEL, 'base': PROMPT_ENHANCER_BASE,
            'ollama_version': OLLAMA_VERSION},
    }, indent=2))


def download_models():
    hf = 'https://huggingface.co/'
    if DOWNLOAD_SDXL_BASE:
        download(hf + 'stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors',
                 MODELS / 'Stable-diffusion/SDXL/sd_xl_base_1.0.safetensors')
    if DOWNLOAD_ANIMA_BASE:
        base = hf + 'circlestone-labs/Anima/resolve/main/split_files/'
        download(base + 'diffusion_models/anima-base-v1.0.safetensors',
                 MODELS / 'Stable-diffusion/Anima/anima-base-v1.0.safetensors')
        download(base + 'text_encoders/qwen_3_06b_base.safetensors',
                 MODELS / 'text_encoder/qwen_3_06b_base.safetensors')
        download(base + 'vae/qwen_image_vae.safetensors',
                 MODELS / 'VAE/qwen_image_vae.safetensors')
    download(hf + 'madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors',
             MODELS / 'VAE/sdxl_vae_fp16_fix.safetensors')
    if DOWNLOAD_CONTROLNET_SDXL:
        for name in ('sai_xl_canny_256lora', 'sai_xl_depth_256lora', 'thibaud_xl_openpose_256lora'):
            download(hf + 'lllyasviel/sd_control_collection/resolve/main/' + name + '.safetensors',
                     MODELS / 'ControlNet/SDXL' / (name + '.safetensors'))
    if DOWNLOAD_ANIMA_POSE:
        download(hf + 'kohya-ss/Anima-LLLite/resolve/main/anima-lllite-pose-1.safetensors',
                 MODELS / 'ControlNet/Anima/anima-lllite-pose-1.safetensors')
    for name in ('face_yolov8n.pt', 'hand_yolov8n.pt', 'person_yolov8n-seg.pt'):
        download(hf + 'Bingsu/adetailer/resolve/main/' + name,
                 MODELS / 'adetailer' / name, file_format='torch')
    if PRELOAD_POSE_DETECTORS:
        for name in ('yolox_l.onnx', 'dw-ll_ucoco_384.onnx'):
            download(hf + 'yzd-v/DWPose/resolve/main/' + name,
                     MODELS / 'ControlNetPreprocessor/openpose' / name, file_format='onnx')


def configure_workspace():
    path = WEBUI / 'config.json'
    config = json.loads(path.read_text()) if path.is_file() else {}
    anima = MODELS / 'Stable-diffusion/Anima/anima-base-v1.0.safetensors'
    sdxl = MODELS / 'Stable-diffusion/SDXL/sd_xl_base_1.0.safetensors'
    anima_modules = [MODELS / 'text_encoder/qwen_3_06b_base.safetensors', MODELS / 'VAE/qwen_image_vae.safetensors']
    # Exact Neo preset option names; UI switching restores each family's modules.
    if anima.is_file():
        config.setdefault('forge_checkpoint_anima', 'Anima/anima-base-v1.0.safetensors')
    if sdxl.is_file():
        config.setdefault('forge_checkpoint_xl', 'SDXL/sd_xl_base_1.0.safetensors')
    if all(file.is_file() for file in anima_modules):
        config['forge_additional_modules_anima'] = list(map(str, anima_modules))
    config['forge_additional_modules_xl'] = [str(MODELS / 'VAE/sdxl_vae_fp16_fix.safetensors')]
    selected = 'anima' if START_WITH == 'Anima' else 'xl'
    checkpoint = config.get('forge_checkpoint_' + selected)
    if not checkpoint:
        candidates = sorted((MODELS / 'Stable-diffusion').rglob('*.safetensors'))
        if not candidates:
            raise RuntimeError('No checkpoint installed. Enable a base-model download or add a checkpoint to models/Stable-diffusion.')
        raise RuntimeError('Selected starting family has no checkpoint. Enable its download or configure forge_checkpoint_' + selected + ' in config.json.')
    config.update(forge_preset=selected, sd_model_checkpoint=checkpoint,
                  forge_additional_modules=config['forge_additional_modules_' + selected],
                  forge_unet_storage_dtype='Automatic',
                  control_net_models_path=str(MODELS / 'ControlNet'),
                  control_net_unit_count=2, ad_max_models=2, lora_show_all=True,
                  lora_hide_unknown_for_versions=[], extra_networks_show_hidden_directories=True,
                  localization='pt_BR' if LANGUAGE == 'pt-BR' else 'None',
                  disable_all_extensions='none', samples_save=True,
                  outdir_samples='', outdir_grids='', save_images_add_number=True)
    # Keep absent legacy A1111 extensions disabled; use Neo's built-in ControlNet.
    disabled = config.get('disabled_extensions', [])
    required = {'ADetailer-Neo', 'sd-webui-civbrowser', 'axo-image-studio', 'sd_forge_controlnet',
                'sd_forge_controlllite', 'forge_legacy_preprocessors'}
    if ENABLE_PROMPT_ENHANCER:
        required.add(PROMPT_ENHANCER_NAME)
    elif (EXTENSIONS / PROMPT_ENHANCER_NAME).exists():
        disabled = list(disabled) + [PROMPT_ENHANCER_NAME]
    config['disabled_extensions'] = [name for name in disabled if Path(name).name not in required]
    for key, folder in {
        'outdir_txt2img_samples':'txt2img', 'outdir_img2img_samples':'img2img',
        'outdir_extras_samples':'extras', 'outdir_txt2img_grids':'grids/txt2img',
        'outdir_img2img_grids':'grids/img2img', 'outdir_save':'saved',
    }.items():
        target = AXO_OUTPUT_ROOT / folder
        target.mkdir(parents=True, exist_ok=True)
        config[key] = str(target)
    connect_browser_token(config)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2))


def install_axo_workspace():
    target = EXTENSIONS / 'axo-image-studio'
    files = globals().get('AXO_EXTENSION_FILES')
    if files is None:
        base = Path(__file__).resolve().parent / 'extension'
        files = {str(p.relative_to(base)): p.read_text() for p in base.rglob('*')
                 if p.is_file() and p.suffix in {'.py', '.js', '.css', '.b64', '.yaml'}}
    for relative, content in files.items():
        file = target / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding='utf-8')
    if LANGUAGE == 'pt-BR':
        translations = list((EXTENSIONS / 'axo-localization-pt-BR/localizations').glob('*.json'))
        if not translations:
            raise RuntimeError('Portuguese localization file missing.')
        preferred = next((file for file in translations if file.stem == 'pt_BR'), translations[0])
        file = target / 'localizations/pt_BR.json'
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(preferred.read_text(encoding='utf-8'), encoding='utf-8')


def launch_arguments():
    args = [PYTHON, '-u', 'launch.py', '--model-ref', MODELS, '--share', '--api',
            '--port', '7860', '--theme', 'dark', '--skip-python-version-check',
            '--skip-prepare-environment', '--ad-no-huggingface', '--fp32-vae', '--use-pytorch-cross-attention']
    if LOW_VRAM:
        args.append('--lowvram')
    if FORCE_FP32 or not GPU_BF16:
        args.append('--force-fp32')
    # Reuse a previous A1111 installation's models without changing its files.
    previous = Path('/content/stable-diffusion-webui')
    if (previous / 'models').is_dir():
        args += ['--forge-ref-a1111-home', previous]
    return args


def validate_running_ui():
    response = requests.get('http://127.0.0.1:7860/sdapi/v1/scripts', timeout=10)
    response.raise_for_status()
    names = ' '.join(response.json().get('txt2img', [])).lower()
    for required in ('adetailer', 'controlnet'):
        if required not in names:
            raise RuntimeError(f'{required} failed to load. Inspect forge.log above.')
    response = requests.get('http://127.0.0.1:7860/config', timeout=10)
    response.raise_for_status()
    ui = response.json()
    labels = [c.get('props', {}).get('label', '') for c in ui.get('components', [])]
    if 'CivBrowser' not in labels and not any('civ' in str(label).lower() for label in labels):
        raise RuntimeError('CivBrowser failed to load. Inspect forge.log above.')
    if ENABLE_GALLERY and not any(c.get('props', {}).get('elem_id') == 'axo-gallery' for c in ui.get('components', [])):
        raise RuntimeError('Axo Studio gallery failed to load. Inspect forge.log.')
    if ENABLE_PROMPT_ENHANCER:
        ids = {c.get('props', {}).get('elem_id') for c in ui.get('components', [])}
        if not {'txt2img_pe_source', 'img2img_pe_source'} <= ids:
            raise RuntimeError('Prompt Enhancer failed to load in both tabs. Inspect forge.log.')
    print('Verified: ControlNet, ADetailer, CivBrowser and enabled Axo Studio panels loaded.', flush=True)


def launch_webui():
    stop()
    try:
        start_prompt_backend()
    except BaseException:
        stop()
        raise
    try:
        process = subprocess.Popen([str(x) for x in launch_arguments()], cwd=WEBUI,
                                   env=child_environment(), stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                   errors='replace', bufsize=1)
    except BaseException:
        stop()
        raise
    PROCESSES.append(process)
    def stream():
        with (ROOT / 'forge.log').open('a', encoding='utf-8') as log:
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end='', flush=True)
    threading.Thread(target=stream, daemon=True).start()
    try:
        deadline = time.monotonic() + 360
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Forge exited with code {process.returncode}. Inspect forge.log.')
            try:
                ready = requests.get('http://127.0.0.1:7860/sdapi/v1/scripts', timeout=3)
                if ready.ok:
                    validate_running_ui()
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            raise RuntimeError('Forge startup timed out. Inspect forge.log.')
        while process.poll() is None:
            time.sleep(1)
        if process.returncode:
            raise RuntimeError(f'Forge exited with code {process.returncode}. Inspect forge.log.')
    finally:
        stop()


def start():
    global AXO_FORGE_PROCESSES
    AXO_FORGE_PROCESSES = PROCESSES
    stop()
    check_gpu()
    prepare_paths()
    load_download_dependencies()
    read_colab_token()
    print('[1/6] Preparing Python 3.12…', flush=True)
    ensure_runtime()
    print('[2/6] Installing Forge Neo and extensions…', flush=True)
    prepare_webui()
    print('[3/6] Installing CUDA/runtime dependencies…', flush=True)
    install_dependencies()
    print('[4/6] Downloading models and pose detectors…', flush=True)
    download_models()
    print('[5/6] Configuring SDXL and Anima presets…', flush=True)
    configure_workspace()
    print('[6/6] Starting Axo Studio. Wait for the gradio.live link…', flush=True)
    print('Choose UI Preset: xl or anima. Pose: ControlNet. Face/hands: ADetailer.', flush=True)
    launch_webui()

# Runtime/download helpers for the isolated Colab environment.

def runtime_healthy(python):
    if not Path(python).is_file():
        return False
    try:
        check = subprocess.run([str(python), '-c',
            'import sys,pip; assert sys.version_info[:2] == (3,12)'],
            capture_output=True, text=True, timeout=30)
        return check.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False

def ensure_runtime():
    if runtime_healthy(PYTHON):
        print('Reusing isolated Python 3.12 runtime.', flush=True)
        return
    # Preserve any incomplete environment rather than trusting bin/python alone.
    if RUNTIME.exists():
        backup = RUNTIME.with_name(RUNTIME.name + '-incomplete-' + str(time.time_ns()))
        RUNTIME.rename(backup)
        print('Incomplete runtime moved aside; rebuilding.', flush=True)
    uv = shutil.which('uv')
    if not uv:
        binary = Path('/content/axo-tools/uv')
        if not binary.is_file():
            print('Installing the uv environment bootstrap…', flush=True)
            url = 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz'
            request = urllib.request.Request(url, headers={'User-Agent': 'Axo-Image-Studio'})
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
            with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
                member = next((item for item in archive.getmembers()
                               if item.isfile() and Path(item.name).name == 'uv'), None)
                if member is None:
                    raise RuntimeError('The uv archive has no executable.')
                with archive.extractfile(member) as handle:
                    executable = handle.read()
            if not executable.startswith(b'\x7fELF'):
                raise RuntimeError('The uv download is not a Linux executable.')
            binary.parent.mkdir(parents=True, exist_ok=True)
            temporary = binary.with_suffix('.part')
            temporary.write_bytes(executable)
            temporary.chmod(0o755)
            temporary.replace(binary)
        uv = str(binary)
    print('Creating Python 3.12 runtime with pip (independent of Colab Python)…', flush=True)
    run([uv, 'venv', '--python', '3.12', '--managed-python', '--seed', RUNTIME])
    if not runtime_healthy(PYTHON):
        raise RuntimeError('Runtime verification failed: Python 3.12 and pip are required.')

def load_download_dependencies():
    global requests, tqdm
    try:
        import requests
        from tqdm.auto import tqdm
    except ImportError:
        run([sys.executable, '-m', 'pip', 'install', 'requests', 'tqdm'])
        import requests
        from tqdm.auto import tqdm

def read_colab_token():
    global CIVITAI_TOKEN
    try:
        from google.colab import userdata
        CIVITAI_TOKEN = userdata.get('CIVITAI_TOKEN') or ''
    except Exception:
        CIVITAI_TOKEN = ''

def valid_file(path, file_format, minimum):
    path = Path(path)
    if not path.is_file() or path.stat().st_size < minimum:
        return False
    try:
        with path.open('rb') as f:
            if file_format == 'safetensors':
                raw = f.read(8)
                if len(raw) != 8:
                    return False
                header_size = struct.unpack('<Q', raw)[0]
                if not 2 <= header_size <= min(100_000_000, path.stat().st_size - 8):
                    return False
                header = json.loads(f.read(header_size))
                payload = path.stat().st_size - 8 - header_size
                tensors = [v for k, v in header.items() if k != '__metadata__']
                if not tensors:
                    return False
                return all(isinstance(t, dict) and isinstance(t.get('data_offsets'), list)
                           and len(t['data_offsets']) == 2
                           and 0 <= t['data_offsets'][0] <= t['data_offsets'][1] <= payload
                           for t in tensors)
            prefix = f.read(512)
            if file_format == 'torch':
                return prefix.startswith(b'PK\x03\x04') or prefix.startswith(b'\x80')
            if file_format == 'yaml':
                text = prefix.decode('utf-8').lower().lstrip()
                return ':' in text and not text.startswith(('<', '{'))
            return True
    except (ValueError, TypeError, OSError, KeyError):
        return False

def download(url, destination, file_format='safetensors', minimum=1_000_000, civitai=False):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if valid_file(destination, file_format, minimum):
        print(f'Already available: {destination.name}')
        return
    partial = destination.with_name(destination.name + '.part')
    params = {'token': CIVITAI_TOKEN} if civitai and CIVITAI_TOKEN else None
    for attempt in range(1, 4):
        try:
            with requests.get(url, params=params, stream=True, timeout=(30, 120)) as response:
                if response.status_code in (401, 403):
                    if civitai:
                        raise PermissionError('Civitai: configure CIVITAI_TOKEN in Colab Secrets and check model access.')
                    raise PermissionError(f'Access denied while downloading {destination.name}.')
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type or 'application/json' in content_type:
                    raise ValueError('The server returned a page or error instead of a model.')
                total = int(response.headers.get('Content-Length', 0))
                received = 0
                with partial.open('wb') as f, tqdm(total=total or None, unit='B', unit_scale=True, desc=destination.name) as bar:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            received += len(chunk)
                            bar.update(len(chunk))
                if total and not response.headers.get('Content-Encoding') and received != total:
                    raise ValueError('Incomplete download.')
            if not valid_file(partial, file_format, minimum):
                raise ValueError('The downloaded file failed the format/size check.')
            partial.replace(destination)
            print(f'Ready: {destination.name}')
            return
        except PermissionError as exc:
            partial.unlink(missing_ok=True)
            raise RuntimeError(str(exc)) from None
        except (requests.RequestException, ValueError, OSError):
            partial.unlink(missing_ok=True)
            if attempt == 3:
                raise RuntimeError(f'Failed to download {destination.name} after 3 attempts. Check the connection and model access, then rerun this cell.') from None
            print(f'Retry ({attempt + 1}/3): {destination.name}')

def connect_browser_token(config):
    if not CIVITAI_TOKEN:
        return
    repo = EXTENSIONS / 'sd-webui-civbrowser'
    for source_path in (repo / 'scripts').glob('*.py'):
        try:
            tree = ast.parse(source_path.read_text())
        except (OSError, UnicodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values):
                if not (isinstance(key, ast.Constant) and isinstance(key.value, str) and isinstance(value, ast.Call)):
                    continue
                func = value.func
                name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ''
                if name != 'OptionInfo':
                    continue
                labels = [arg.value.lower() for arg in value.args[1:] if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
                labels += [kw.value.value.lower() for kw in value.keywords if kw.arg == 'label' and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str)]
                if any('api' in label and 'key' in label for label in labels):
                    config[key.value] = CIVITAI_TOKEN
                    print('Colab secret connected to CivBrowser.')
                    return
    NOTICES.append('Could not detect the API key setting in this CivBrowser version. Enter it under Settings → CivBrowser for authenticated downloads.')

AXO_EXTENSION_FILES = None  # Embedded by tools/build_notebook.py

try:
    start()
except KeyboardInterrupt:
    stop()
    print('Stopped. Run the restart cell to launch again.')
except Exception:
    stop()
    print('Installation/startup failed. Fix the error above and rerun; completed downloads are reused.')
    raise
