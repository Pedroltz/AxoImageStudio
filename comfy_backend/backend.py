"""Colab ComfyUI backend; embedded and executed in the launcher's namespace."""
COMFY = Path('/content/axo-comfyui')
COMFY_REVISION = '5f415e31abfd837870bbc733ba1e158de71ed985'
CIVICOMFY_REVISION = '555e984bbcb02fc955075cb8eb699a6884c51239'


def prepare_civicomfy():
    folder = COMFY / 'custom_nodes/Civicomfy'
    clone_at('https://github.com/MoonGoblinDev/Civicomfy.git', folder, CIVICOMFY_REVISION)
    # This revision uses requests/aiohttp already supplied by ComfyUI.
    for relative in ('__init__.py', 'web/js/civitaiDownloader.js', 'web/js/civitaiDownloader.css'):
        if not (folder / relative).is_file():
            raise RuntimeError('Incomplete Civicomfy installation: ' + relative)


def prepare_comfy():
    print('Installing ComfyUI in its isolated runtime…', flush=True)
    clone_at('https://github.com/Comfy-Org/ComfyUI.git', COMFY, COMFY_REVISION)
    run([PYTHON, '-m', 'pip', 'install', 'torch==2.8.0', 'torchvision==0.23.0',
         'torchaudio==2.8.0', '--index-url', 'https://download.pytorch.org/whl/cu126'])
    run([PYTHON, '-m', 'pip', 'install', '-r', COMFY / 'requirements.txt'])
    prepare_civicomfy()
    run([PYTHON, '-m', 'pip', 'check'])
    run([PYTHON, '-c', 'import torch; assert torch.cuda.is_available(), "CUDA unavailable"'])
    binary = Path('/content/axo-tools/cloudflared')
    if not binary.is_file():
        download('https://github.com/cloudflare/cloudflared/releases/download/2026.10.0/cloudflared-linux-amd64',
                 binary, file_format='binary')
    import hashlib
    if hashlib.sha256(binary.read_bytes()).hexdigest() != 'd33ff2d14475178d2012c2c56beba87389ac5ded27649519f198a7d3134a99db':
        binary.unlink()
        raise RuntimeError('cloudflared checksum failed. Rerun installation to download it again.')
    binary.chmod(0o755)
    print('ComfyUI uses its native node interface. Forge panels, ADetailer and pose helpers are skipped.', flush=True)


def configure_comfy():
    # Default download locations are the same persistent folders used by Forge.
    mapping = {'base_path': str(MODELS), 'is_default': True, 'checkpoints': 'Stable-diffusion/SDXL',
               'diffusion_models': 'Stable-diffusion/Anima', 'text_encoders': 'text_encoder',
               'vae': 'VAE', 'loras': 'Lora', 'upscale_models': 'ESRGAN',
               'controlnet': 'ControlNet', 'embeddings': 'embeddings'}
    # Search all Forge checkpoint subfolders plus common Comfy/A1111 aliases.
    # Keep the original SDXL/Anima roots, so existing starter filenames still work.
    additional = {'base_path': str(MODELS), 'checkpoints': 'Stable-diffusion\ncheckpoints',
                  'diffusion_models': 'diffusion_models\nunet',
                  'text_encoders': 'text_encoders\nclip', 'loras': 'loras\nLyCORIS',
                  'vae': 'vae', 'upscale_models': 'upscale_models\nRealESRGAN\nSwinIR',
                  'controlnet': 'controlnet'}
    for key, value in mapping.items():
        if key not in ('base_path', 'is_default'):
            (MODELS / value).mkdir(parents=True, exist_ok=True)
    # JSON is valid YAML; quoting Drive paths this way also handles spaces safely.
    (COMFY / 'extra_model_paths.yaml').write_text(
        json.dumps({'axo_additional': additional, 'axo': mapping}), encoding='utf-8')
    print(f'Shared model folder: {MODELS}. Civicomfy downloads use these folders by default.', flush=True)
    user = ROOT / 'comfy-user'
    workflows = user / 'default/workflows'
    workflows.mkdir(parents=True, exist_ok=True)
    for name in ('Anima', 'SDXL'):
        destination = workflows / f'Axo {name}.json'
        if not destination.exists():
            destination.write_text(AXO_COMFY_FILES[f'{name.lower()}.json'], encoding='utf-8')
    # A tiny native extension offers the selected starter on a fresh browser,
    # without replacing a graph the user is already editing.
    extension = COMFY / 'custom_nodes/axo_starter'
    web = extension / 'web'
    web.mkdir(parents=True, exist_ok=True)
    (extension / '__init__.py').write_text("WEB_DIRECTORY = './web'\nNODE_CLASS_MAPPINGS = {}\n", encoding='utf-8')
    (web / 'starter.js').write_text(AXO_COMFY_FILES['starter.js'], encoding='utf-8')
    (web / 'initial.json').write_text(AXO_COMFY_FILES[START_WITH.lower() + '.json'], encoding='utf-8')
    required = {
        'Anima': ['Stable-diffusion/Anima/anima-base-v1.0.safetensors',
                  'text_encoder/qwen_3_06b_base.safetensors', 'VAE/qwen_image_vae.safetensors'],
        'SDXL': ['Stable-diffusion/SDXL/sd_xl_base_1.0.safetensors'],
    }
    for family, paths in required.items():
        missing = [path for path in paths if not (MODELS / path).is_file()]
        if missing:
            print(f'{family}: missing files: {", ".join(missing)}. Enable DOWNLOAD_{family.upper()}_BASE and rerun, or supply these files.')
    (AXO_OUTPUT_ROOT / 'ComfyUI').mkdir(parents=True, exist_ok=True)
    print(f'Starter: {START_WITH}. Both starters are available under Workflows → Axo Anima / Axo SDXL.')


def comfy_arguments():
    args = [PYTHON, '-u', 'main.py', '--listen', '127.0.0.1', '--port', '8188',
            '--disable-auto-launch', '--user-directory', ROOT / 'comfy-user',
            '--output-directory', AXO_OUTPUT_ROOT / 'ComfyUI']
    if LOW_VRAM:
        args.append('--lowvram')
    if FORCE_FP32:
        args.append('--force-fp32')
    return args


def comfy_process(args, logfile, on_line=None):
    process = subprocess.Popen([str(x) for x in args], cwd=COMFY, env=child_environment(),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding='utf-8', errors='replace', bufsize=1)
    PROCESSES.append(process)
    def stream():
        with (ROOT / logfile).open('a', encoding='utf-8') as log:
            for line in process.stdout:
                log.write(line)
                log.flush()
                print(line, end='', flush=True)
                if on_line:
                    on_line(line)
    threading.Thread(target=stream, daemon=True).start()
    return process


def wait_comfy(server):
    deadline = time.monotonic() + 360
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError(f'ComfyUI exited ({server.returncode}). Inspect comfy.log.')
        try:
            response = requests.get('http://127.0.0.1:8188/object_info', timeout=3)
            if response.ok:
                nodes = response.json()
                required = {'UNETLoader', 'CLIPLoader', 'VAELoader', 'CheckpointLoaderSimple', 'KSampler'}
                if not required.issubset(nodes):
                    raise RuntimeError('Required ComfyUI nodes missing. Inspect comfy.log.')
                status = requests.get('http://127.0.0.1:8188/civitai/status', timeout=10)
                if not status.ok or not isinstance(status.json(), dict):
                    raise RuntimeError('Civicomfy failed to load. Inspect comfy.log and rerun installation.')
                print('Civicomfy loaded. Open the Civicomfy button to search/download models.', flush=True)
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError('ComfyUI startup timed out. Inspect comfy.log.')


def launch_comfy():
    stop()
    try:
        check_gpu()
        server = comfy_process(comfy_arguments(), 'comfy.log')
        wait_comfy(server)
        urls = []
        def find_url(line):
            match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
            if match:
                urls.append(match.group())
        tunnel = comfy_process(['/content/axo-tools/cloudflared', 'tunnel', '--no-autoupdate',
                                '--url', 'http://127.0.0.1:8188', '--protocol', 'http2'],
                               'comfy-tunnel.log', find_url)
        deadline = time.monotonic() + 90
        while not urls:
            if tunnel.poll() is not None or server.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('ComfyUI tunnel failed. Inspect comfy-tunnel.log and comfy.log.')
            time.sleep(1)
        print(f'Open ComfyUI: {urls[0]}', flush=True)
        while server.poll() is None and tunnel.poll() is None:
            time.sleep(1)
        raise RuntimeError('ComfyUI or its tunnel stopped. Inspect logs, then run Restart.')
    finally:
        stop()
