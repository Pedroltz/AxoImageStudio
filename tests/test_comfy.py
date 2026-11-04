"""Exercise Colab routing and Comfy setup without installing engines or using GPU."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def launcher(tmp_path):
    tree = ast.parse((ROOT / 'axo_launcher.py').read_text(encoding='utf-8'))
    # Exclude only the final installer invocation, not its function definitions.
    tree.body = [node for node in tree.body if not isinstance(node, ast.Try)]
    ns = {}
    exec(compile(tree, 'axo_launcher.py', 'exec'), ns)
    ns['AXO_COMFY_FILES'] = {p.name: p.read_text(encoding='utf-8')
                              for p in (ROOT / 'comfy_backend').iterdir() if p.is_file()}
    exec(compile(ns['AXO_COMFY_FILES']['backend.py'], 'backend.py', 'exec'), ns)
    ns.update(ROOT=tmp_path, MODELS=tmp_path / 'models', AXO_OUTPUT_ROOT=tmp_path / 'outputs',
              COMFY=tmp_path / 'comfy', INTERFACE='ComfyUI')
    ns['COMFY'].mkdir()
    return ns


def test_paths_workflows_and_user_edits(launcher, capsys):
    ns = launcher
    ns['configure_comfy']()
    config = json.loads((ns['COMFY'] / 'extra_model_paths.yaml').read_text())['axo']
    assert config['checkpoints'] == 'Stable-diffusion/SDXL'
    assert config['diffusion_models'] == 'Stable-diffusion/Anima'
    assert 'missing files' in capsys.readouterr().out
    workflows = ns['ROOT'] / 'comfy-user/default/workflows'
    assert len(list(workflows.glob('*.json'))) == 2
    edited = workflows / 'Axo Anima.json'
    edited.write_text('{"edited":true}')
    ns['configure_comfy']()
    assert json.loads(edited.read_text()) == {'edited': True}
    assert (ns['AXO_OUTPUT_ROOT'] / 'ComfyUI').is_dir()


def test_workflow_links_and_model_loaders(launcher):
    for family in ('anima', 'sdxl'):
        workflow = json.loads(launcher['AXO_COMFY_FILES'][family + '.json'])
        nodes = {n['id']: n for n in workflow['nodes']}
        assert len(nodes) == workflow['last_node_id']
        for link, source, slot, target, target_slot, kind in workflow['links']:
            assert link in nodes[source]['outputs'][slot]['links']
            assert nodes[target]['inputs'][target_slot]['link'] == link
            assert nodes[source]['outputs'][slot]['type'] == kind
            assert nodes[target]['inputs'][target_slot]['type'] == kind
        types = {n['type'] for n in nodes.values()}
        assert 'SaveImage' in types and 'KSampler' in types
        assert ('UNETLoader' in types) == (family == 'anima')
        assert ('CheckpointLoaderSimple' in types) == (family == 'sdxl')


def test_env_and_arguments_do_not_inherit_forge_constraints(launcher, monkeypatch):
    ns = launcher
    monkeypatch.setenv('PIP_CONSTRAINT', 'forge-constraints.txt')
    monkeypatch.setenv('REQS_FILE', 'forge-requirements.txt')
    assert 'PIP_CONSTRAINT' not in ns['child_environment']()
    assert 'REQS_FILE' not in ns['child_environment']()
    ns.update(LOW_VRAM=True, FORCE_FP32=True)
    args = ns['comfy_arguments']()
    assert '--lowvram' in args and '--force-fp32' in args and '--share' not in args


def test_start_routes_to_selected_engine(launcher):
    ns = launcher
    names = ('stop', 'check_gpu', 'prepare_paths', 'load_download_dependencies', 'read_colab_token',
             'ensure_runtime', 'prepare_comfy', 'download_models', 'configure_comfy', 'launch_comfy',
             'prepare_webui', 'install_dependencies', 'configure_workspace', 'launch_webui')
    for name in names:
        ns[name] = Mock()
    for interface, expected, excluded in [('ComfyUI', 'launch_comfy', 'prepare_webui'),
                                         ('Forge Neo', 'launch_webui', 'prepare_comfy')]:
        ns['INTERFACE'] = interface
        for name in names:
            ns[name].reset_mock()
        ns['start']()
        ns[expected].assert_called_once()
        ns[excluded].assert_not_called()
        assert ('comfy' in str(ns['PYTHON'])) == (interface == 'ComfyUI')


def test_restart_requires_install_after_interface_change(launcher):
    launcher.update(AXO_ACTIVE_INTERFACE='Forge Neo', INTERFACE='ComfyUI')
    with pytest.raises(RuntimeError, match='Interface changed'):
        launcher['restart_interface']()


def test_readiness_failure_and_timeout(launcher):
    ns = launcher
    ns['requests'] = SimpleNamespace(get=Mock(), RequestException=OSError)
    with pytest.raises(RuntimeError, match='exited'):
        ns['wait_comfy'](SimpleNamespace(poll=lambda: 1, returncode=1))
    ns['time'] = SimpleNamespace(monotonic=Mock(side_effect=[0, 361]))
    with pytest.raises(RuntimeError, match='timed out'):
        ns['wait_comfy'](SimpleNamespace(poll=lambda: None))


def test_tunnel_failure_cleans_up(launcher):
    ns = launcher
    ns['stop'] = Mock()
    ns['check_gpu'] = Mock()
    ns['wait_comfy'] = Mock()
    ns['comfy_process'] = Mock(side_effect=[SimpleNamespace(poll=lambda: None),
                                           SimpleNamespace(poll=lambda: 1)])
    with pytest.raises(RuntimeError, match='tunnel failed'):
        ns['launch_comfy']()
    assert ns['stop'].call_count == 2


def test_comfy_download_skips_forge_extras(launcher):
    ns = launcher
    ns['download'] = Mock()
    ns['download_models']()
    names = [str(call.args[1]) for call in ns['download'].call_args_list]
    assert any('anima-base' in name for name in names)
    assert any('sd_xl_base' in name for name in names)
    assert not any('adetailer' in name or 'ControlNet' in name for name in names)


def test_notebook_embeds_backend_and_workflows():
    notebook = json.loads((ROOT / 'Axo_Image_Studio.ipynb').read_text(encoding='utf-8'))
    source = ''.join(notebook['cells'][2]['source'])
    assignment = next(n for n in ast.parse(source).body if isinstance(n, ast.Assign)
                      and any(getattr(t, 'id', '') == 'AXO_COMFY_FILES' for t in n.targets))
    embedded = ast.literal_eval(assignment.value)
    expected = {p.name: p.read_text(encoding='utf-8') for p in (ROOT / 'comfy_backend').iterdir()
                if p.is_file() and p.suffix in {'.py', '.js', '.json'}}
    assert embedded == expected
