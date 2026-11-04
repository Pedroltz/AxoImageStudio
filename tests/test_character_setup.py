"""Check dependency setup without installing packages, downloading weights or using a GPU."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]


def test_reference_workflow_connections_and_refinement_order():
    graph = json.loads((ROOT / 'workflows/Axo_Anima_Personagem_Refino.json').read_text(encoding='utf-8'))
    nodes = {node['id']: node for node in graph['nodes']}
    for link, source, slot, target, target_slot, kind in graph['links']:
        assert link in nodes[source]['outputs'][slot]['links']
        assert nodes[target]['inputs'][target_slot]['link'] == link
        assert nodes[source]['outputs'][slot]['type'] == nodes[target]['inputs'][target_slot]['type'] == kind
    adapter = next(n for n in nodes.values() if n['type'] == 'AnimaRefAdapter')
    sampler = next(n for n in nodes.values() if n['type'] == 'KSampler')
    assert sampler['inputs'][0]['link'] in adapter['outputs'][0]['links']
    latent = next(n for n in nodes.values() if n['type'] == 'EmptyLatentImage')
    assert sampler['inputs'][3]['link'] in latent['outputs'][0]['links']
    hands = next(n for n in nodes.values() if n['type'] == 'FaceDetailer' and 'MÃOS' in n['title'])
    face = next(n for n in nodes.values() if n['type'] == 'FaceDetailer' and 'ROSTO' in n['title'])
    assert face['inputs'][0]['link'] in hands['outputs'][0]['links']
    final = next(n for n in nodes.values() if n['type'] == 'SaveImage' and n['widgets_values'] == ['Axo/Personagem/final'])
    assert final['inputs'][0]['link'] in face['outputs'][0]['links']


def test_installer_preserves_paths_and_targets_comfy_runtime(tmp_path, monkeypatch):
    source = ROOT / 'workflows/Instalar_Dependencias_Personagem.py'
    spec = importlib.util.spec_from_file_location('character_setup_test', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.COMFY_DIR = tmp_path / 'ComfyUI'
    module.COMFY_PYTHON = tmp_path / 'runtime/bin/python'
    module.COMFY_DIR.mkdir()
    (module.COMFY_DIR / 'main.py').touch()
    module.COMFY_PYTHON.parent.mkdir(parents=True)
    module.COMFY_PYTHON.touch()
    models = tmp_path / 'MyDrive/Axo-Image-Studio-Forge/models'
    models.mkdir(parents=True)
    original = {'axo': {'base_path': str(models), 'checkpoints': 'Stable-diffusion/SDXL'},
                'user_paths': {'base_path': '/custom', 'loras': 'my_loras'}}
    config = module.COMFY_DIR / 'extra_model_paths.yaml'
    config.write_text(json.dumps(original))
    for name, _, _ in module.PACKAGES:
        folder = module.COMFY_DIR / 'custom_nodes' / name
        folder.mkdir(parents=True)
        (folder / 'requirements.txt').write_text('numpy\ngit+https://github.com/facebookresearch/sam2\n')
    def checkout(name, repo, revision):
        assert len(revision) == 40
        return module.COMFY_DIR / 'custom_nodes' / name
    sock = Mock()
    sock.__enter__ = Mock(return_value=sock)
    sock.__exit__ = Mock(return_value=False)
    sock.connect_ex.return_value = 1
    monkeypatch.setattr('socket.socket', Mock(return_value=sock))
    monkeypatch.setattr(module, 'checkout', checkout)
    monkeypatch.setattr(module.subprocess, 'check_output', Mock(return_value=json.dumps(original)))
    run, downloads = Mock(), Mock()
    monkeypatch.setattr(module, 'run', run)
    monkeypatch.setattr(module, 'download', downloads)
    module.main(standalone=False)
    saved = json.loads(config.read_text())
    assert saved['user_paths'] == original['user_paths'] and saved['axo'] == original['axo']
    assert saved['axo_character']['base_path'] == str(models)
    assert saved['axo_character']['ultralytics_bbox'] == 'adetailer'
    assert downloads.call_count == 3
    assert all(str(call.args[1]).startswith(str(models)) for call in downloads.call_args_list)
    assert json.loads(config.with_name('extra_model_paths.before-character.yaml').read_text()) == original
    requirements = (module.COMFY_DIR / 'axo-character-setup/requirements.txt').read_text()
    assert 'facebookresearch/sam2' not in requirements and 'ultralytics==8.3.253' in requirements
    assert all(call.args[0][0] == module.COMFY_PYTHON for call in run.call_args_list)
