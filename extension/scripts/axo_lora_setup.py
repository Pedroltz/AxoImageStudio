"""Align CivBrowser download folders with Forge Neo's LoRA directory."""
import json
from pathlib import Path
from modules import script_callbacks, shared


def configure_lora_downloads():
    lora = Path(shared.cmd_opts.lora_dir).resolve()
    lora.mkdir(parents=True, exist_ok=True)
    matched = False
    for key, info in list(shared.opts.data_labels.items()):
        if not key.startswith('civsfz'):
            continue
        current = shared.opts.data.get(key, info.default)
        def parse(value):
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    return parsed if isinstance(parsed, dict) else {}
                except ValueError:
                    return {}
            return {}
        defaults = parse(info.default)
        folders = parse(current)
        # Identify the native folder-map option by its schema, not a guessed key.
        if not {'LORA', 'Checkpoint'}.issubset(defaults.keys() | folders.keys()):
            continue
        merged = {**defaults, **folders}
        merged.update({'Checkpoint': str(lora.parent / 'Stable-diffusion'), 'LORA': str(lora), 'LoCon': str(lora / '_LyCORIS'), 'DoRA': str(lora / '_DoRA')})
        for target in [lora / '_LyCORIS', lora / '_DoRA']:
            target.mkdir(parents=True, exist_ok=True)
        shared.opts.set(key, merged if isinstance(current, dict) else json.dumps(merged))
        matched = True
    if matched:
        shared.opts.save(shared.config_filename)
        print(f'Axo Studio: CivBrowser LoRA downloads aligned with {lora}')
    else:
        print('Axo Studio: CivBrowser folder-map setting was not detected. LoRA directory is configured; check upstream CivBrowser settings if downloads go elsewhere.')


script_callbacks.on_before_ui(configure_lora_downloads)
