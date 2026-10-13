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
    script.write_text('DEFAULT_API_URL = "http://localhost:11434"\nDEFAULT_MODEL = "old"\n'
                      'base = gr.Dropdown(label="Base", value="Default", scale=1)\n'
                      'base_description = gr.HTML(value=_base_description_html("Default"))\n')
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
    assert "DEFAULT_MODEL = 'huihui_ai/qwen3.5-abliterated:9b'" in script.read_text()
    config = json.loads(path.read_text())
    assert config['unrelated/value'] == 42
    for tab in ('txt2img', 'img2img'):
        assert config[f'customscript/prompt_enhancer.py/{tab}/Model/value'] == 'huihui_ai/qwen3.5-abliterated:9b'
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
    response.json.return_value = {'models': [{'name': 'huihui_ai/qwen3.5-abliterated:9b'}]}
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
    response.json.return_value = {'models': [{'name': 'huihui_ai/qwen3.5-abliterated:9b'}]}
    launcher.update(requests=Mock(), run=Mock())
    launcher['requests'].get.return_value = response
    launcher['start_prompt_backend']()
    env = popen.call_args.kwargs['env']
    assert env['CUDA_VISIBLE_DEVICES'] == '-1'
    assert env['OLLAMA_KEEP_ALIVE'] == '0'
    assert env['OLLAMA_HOST'] == '127.0.0.1:11434'
    assert env['OLLAMA_MODELS'] == str(launcher['MODELS'] / 'Ollama')
    assert launcher['PROCESSES'] == [process]
    launcher['run'].assert_called_once_with([binary, 'pull', 'huihui_ai/qwen3.5-abliterated:9b'], env=env)


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


@pytest.mark.parametrize('family, expected', [('SDXL', 'Axo SDXL - PT-BR'), ('Anima', 'Axo Anima - PT-BR')])
def test_auto_base_matches_starting_family_and_preserves_personal_yaml(launcher, family, expected):
    seed_extension(launcher)
    launcher['START_WITH'] = family
    personal = launcher['ROOT'] / 'prompt-enhancer'
    personal.mkdir()
    overrides = personal / '_bases.yaml'
    overrides.write_text('My Base: personal instructions\n')
    launcher['prepare_prompt_enhancer']()
    script = launcher['EXTENSIONS'] / launcher['PROMPT_ENHANCER_NAME'] / 'scripts/prompt_enhancer.py'
    assert 'value=' + repr(expected) in script.read_text()
    assert '_base_description_html(' + repr(expected) + ')' in script.read_text()
    assert overrides.read_text() == 'My Base: personal instructions\n'
    managed = launcher['ROOT'] / 'prompt-enhancer-axo'
    for name in ('_bases.yaml', '_prompts.yaml'):
        assert (managed / name).read_text() == (ROOT / 'extension/assets/prompt-enhancer' / name).read_text()
    config = json.loads((launcher['WEBUI'] / 'ui-config.json').read_text())
    for tab in ('txt2img', 'img2img'):
        assert config[f'customscript/prompt_enhancer.py/{tab}/Base/value'] == expected
    assert launcher['child_environment']()['PROMPT_ENHANCER_LOCAL'].split(',') == [str(managed), str(personal)]


def test_explicit_base_overrides_initial_family(launcher):
    seed_extension(launcher)
    launcher.update(START_WITH='Anima', PROMPT_ENHANCER_BASE='Axo SDXL - PT-BR')
    launcher['prepare_prompt_enhancer']()
    config = json.loads((launcher['WEBUI'] / 'ui-config.json').read_text())
    assert config['customscript/prompt_enhancer.py/txt2img/Base/value'] == 'Axo SDXL - PT-BR'


def test_prompt_assets_are_valid_upstream_yaml_mappings():
    import yaml
    base = ROOT / 'extension/assets/prompt-enhancer'
    profiles = yaml.safe_load((base / '_bases.yaml').read_text())
    assert set(profiles) == {'_preamble', 'Axo SDXL - PT-BR', 'Axo Anima - PT-BR'}
    assert all(isinstance(entry['body'], str) and entry['body'].strip() for entry in profiles.values())
    assert profiles['Axo SDXL - PT-BR']['target'] == ['sdxl']
    assert profiles['Axo Anima - PT-BR']['target'] == ['anima']
    prompts = yaml.safe_load((base / '_prompts.yaml').read_text())
    assert set(prompts) == {'edit_prose'}
