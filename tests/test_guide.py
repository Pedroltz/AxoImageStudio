"""Search and navigation behavior for the Portuguese wiki, without GPU inference."""
import importlib.util
import sys
import types
from pathlib import Path

import gradio as gr
import pytest


@pytest.fixture
def guide(monkeypatch):
    modules = types.ModuleType('modules')
    modules.script_callbacks = types.SimpleNamespace(on_ui_tabs=lambda callback: None)
    monkeypatch.setitem(sys.modules, 'modules', modules)
    path = Path(__file__).resolve().parents[1] / 'extension/scripts/axo_guide.py'
    spec = importlib.util.spec_from_file_location('axo_guide_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_search_understands_accents_and_common_spelling(guide):
    assert guide.find_topics(query='sempler')[0]['id'] == 'samplers'
    assert any(article['id'] == 'inpaint' for article in guide.find_topics(query='MÁSCARA'))


def test_category_limits_search_results(guide):
    results = guide.find_topics(category='Prompts', query='prompt')
    assert results and all(article['category'] == 'Prompts' for article in results)
    assert guide.view(category='Prompts', current='inicio')[0]['value'] == 'prompt'


def test_no_results_disables_navigation(guide):
    menu, body, status, previous, following = guide.view(query='zznaoexiste')
    assert menu['choices'] == [] and menu['value'] is None
    assert 'Nenhum' in body and 'Nenhum' in status
    assert previous['interactive'] is False and following['interactive'] is False


def test_navigation_stays_within_filtered_results(guide):
    articles = guide.find_topics(category='Prompts')
    first, last = articles[0]['id'], articles[-1]['id']
    assert guide.view(category='Prompts', current=first, direction=-1)[0]['value'] == first
    assert guide.view(category='Prompts', current=last, direction=1)[0]['value'] == last
    assert guide.view(category='Prompts', current=first, direction=1)[0]['value'] == articles[1]['id']


def test_wiki_renders_inside_forge_tabs(guide):
    panel, _, _ = guide.guide()[0]
    with gr.Blocks() as demo:
        with gr.Tab('Axo Guide'):
            panel.render()
    config = demo.get_config_file()
    assert any(c['props'].get('elem_id') == 'axo-wiki-layout' for c in config['components'])
    assert len(guide.ARTICLES) == 29
