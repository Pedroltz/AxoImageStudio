"""Colab installer contracts without downloading models or starting Forge."""
import ast
import json
from pathlib import Path
import types
from unittest.mock import Mock, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def launcher(tmp_path):
    tree = ast.parse((ROOT / 'axo_launcher.py').read_text())
    tree.body = [node for node in tree.body if isinstance(node, (
        ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef))]
    namespace = {'__file__': str(ROOT / 'axo_launcher.py')}
    exec(compile(tree, 'axo_launcher.py', 'exec'), namespace)
    namespace.update(ROOT=tmp_path, MODELS=tmp_path / 'models',
        WEBUI=tmp_path / 'webui', EXTENSIONS=tmp_path / 'webui/extensions',
        AXO_OUTPUT_ROOT=tmp_path / 'outputs', ENABLE_PROMPT_ENHANCER=True,
        PYTHON=tmp_path / 'python', OLLAMA_HOME=tmp_path / 'ollama')
    namespace['WEBUI'].mkdir()
    return namespace


def seed_extension(launcher):
    script = launcher['EXTENSIONS'] / launcher['PROMPT_ENHANCER_NAME'] / 'scripts/prompt_enhancer.py'
    script.parent.mkdir(parents=True)
    script.write_text('DEFAULT_API_URL = "http://localhost:11434"\nDEFAULT_MODEL = "old"\n')
    launcher['clone_at'] = Mock()
    return script


def test_setup_is_pinned_idempotent_and_preserves_ui_settings(launcher):
    script = seed_extension(launcher)
    path = launcher['WEBUI'] / 'ui-config.json'
    path.write_text(json.dumps({'unrelated/value': 42}))
    launcher['prepare_prompt_enhancer']()
    launcher['prepare_prompt_enhancer']()
    launcher['clone_at'].assert_called_with(launcher['PROMPT_ENHANCER_REPO'],
        launcher['EXTENSIONS'] / launcher['PROMPT_ENHANCER_NAME'], launcher['PROMPT_ENHANCER_REVISION'])
    assert "DEFAULT_MODEL = 'qwen3:4b'" in script.read_text()
    config = json.loads(path.read_text())
    assert config['unrelated/value'] == 42
    for tab in ('txt2img', 'img2img'):
        assert config[f'customscript/prompt_enhancer.py/{tab}/Model/value'] == 'qwen3:4b'
    assert (launcher['ROOT'] / 'prompt-enhancer').is_dir()


@pytest.mark.parametrize('url', ['http://host/api/chat', 'bad', 'http://user:pass@host', 'http://host?token=x'])
def test_invalid_api_urls_rejected_before_clone(launcher, url):
    launcher.update(PROMPT_ENHANCER_BACKEND='external', PROMPT_ENHANCER_API_URL=url, clone_at=Mock())
    with pytest.raises(ValueError):
        launcher['prepare_prompt_enhancer']()
    launcher['clone_at'].assert_not_called()


def test_disabled_mode_does_no_backend_work(launcher):
    launcher.update(ENABLE_PROMPT_ENHANCER=False, clone_at=Mock(), requests=Mock())
    launcher['prepare_prompt_enhancer']()
    launcher['start_prompt_backend']()
    launcher['clone_at'].assert_not_called()
    launcher['requests'].get.assert_not_called()


def test_external_backend_checks_model_without_local_install(launcher):
    response = Mock()
    response.json.return_value = {'models': [{'name': 'qwen3:4b'}]}
    launcher.update(PROMPT_ENHANCER_BACKEND='external', requests=Mock(), run=Mock())
    launcher['requests'].get.return_value = response
    launcher['start_prompt_backend']()
    launcher['run'].assert_not_called()
    response.json.return_value = {'models': []}
    with pytest.raises(RuntimeError, match='model unavailable'):
        launcher['start_prompt_backend']()


def test_enabling_then_disabling_existing_extension_preserves_other_settings(launcher):
    seed_extension(launcher)
    checkpoint = launcher['MODELS'] / 'Stable-diffusion/SDXL/sd_xl_base_1.0.safetensors'
    checkpoint.parent.mkdir(parents=True)
    checkpoint.touch()
    path = launcher['WEBUI'] / 'config.json'
    path.write_text(json.dumps({'disabled_extensions': ['other', 'sd-webui-prompt-enhancer'], 'custom': 42}))
    launcher['connect_browser_token'] = Mock()
    launcher['configure_workspace']()
    config = json.loads(path.read_text())
    assert config['disabled_extensions'] == ['other']
    assert config['custom'] == 42
    launcher['ENABLE_PROMPT_ENHANCER'] = False
    launcher['configure_workspace']()
    assert json.loads(path.read_text())['disabled_extensions'] == ['other', 'sd-webui-prompt-enhancer']


def test_backend_launch_failure_stops_owned_processes(launcher):
    launcher['stop'] = Mock()
    launcher['start_prompt_backend'] = Mock(side_effect=RuntimeError('backend failed'))
    with pytest.raises(RuntimeError, match='backend failed'):
        launcher['launch_webui']()
    assert launcher['stop'].call_count == 2


def test_local_backend_cpu_environment_readiness_and_pull(launcher, monkeypatch):
    binary = launcher['OLLAMA_HOME'] / 'bin/ollama'
    binary.parent.mkdir(parents=True)
    binary.touch()
    (launcher['OLLAMA_HOME'] / 'axo-version').write_text(launcher['OLLAMA_VERSION'])
    socket = MagicMock()
    socket.return_value.__enter__.return_value.connect_ex.return_value = 1
    monkeypatch.setattr(launcher['socket'], 'socket', socket)
    process = Mock()
    process.poll.return_value = None
    popen = Mock(return_value=process)
    monkeypatch.setattr(launcher['subprocess'], 'Popen', popen)
    response = Mock(ok=True)
    response.json.return_value = {'models': [{'name': 'qwen3:4b'}]}
    launcher.update(requests=Mock(), run=Mock())
    launcher['requests'].get.return_value = response
    launcher['start_prompt_backend']()
    env = popen.call_args.kwargs['env']
    assert env['CUDA_VISIBLE_DEVICES'] == '-1'
    assert env['OLLAMA_KEEP_ALIVE'] == '0'
    assert env['OLLAMA_HOST'] == '127.0.0.1:11434'
    assert env['OLLAMA_MODELS'] == str(launcher['MODELS'] / 'Ollama')
    assert launcher['PROCESSES'] == [process]
    launcher['run'].assert_called_once_with([binary, 'pull', 'qwen3:4b'], env=env)


def test_ui_validation_requires_enhancer_in_both_tabs(launcher):
    scripts_response = Mock()
    scripts_response.json.return_value = {'txt2img': ['adetailer', 'controlnet']}
    ui_response = Mock()
    components = [ {'props': {'label': 'CivBrowser'}}, {'props': {'elem_id': 'axo-gallery'}},
        {'props': {'elem_id': 'txt2img_pe_source'}}]
    ui_response.json.return_value = {'components': components}
    launcher['requests'] = Mock()
    launcher['requests'].get.side_effect = lambda url, **kw: scripts_response if url.endswith('/scripts') else ui_response
    with pytest.raises(RuntimeError, match='both tabs'):
        launcher['validate_running_ui']()
    components.append({'props': {'elem_id': 'img2img_pe_source'}})
    launcher['validate_running_ui']()


def test_missing_colab_secret_preserves_existing_fallback(launcher, monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, 'google.colab', None)
    launcher['CIVITAI_TOKEN'] = 'previous'
    launcher['read_colab_token']()
    assert launcher['CIVITAI_TOKEN'] == ''


def test_yaml_installed_before_forge_preflight_and_dependency_check(launcher, monkeypatch):
    launcher['run'] = Mock()
    monkeypatch.setattr(launcher['subprocess'], 'check_output', Mock(return_value=json.dumps({'bf16': False, 'gpu': 'mock'})))
    launcher['install_dependencies']()
    commands = [call.args[0] for call in launcher['run'].call_args_list]
    yaml_index = next(i for i, args in enumerate(commands) if 'PyYAML==6.0.2' in args)
    preflight_index = next(i for i, args in enumerate(commands) if '--exit' in args)
    check_index = next(i for i, args in enumerate(commands) if args[-2:] == ['pip', 'check'])
    assert yaml_index < preflight_index < check_index
    assert json.loads((launcher['ROOT'] / 'runtime-info.json').read_text())['prompt_enhancer']['enabled']
