import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def controls(monkeypatch):
    loader = Mock()
    loader.INPUT_TYPES.return_value = {'required': {'image': (['character.png'], {'image_upload': True})}}
    loader.VALIDATE_INPUTS.return_value = True
    loader.IS_CHANGED.return_value = 'image-hash'
    loader.return_value.load_image.return_value = ('pixels', 'mask')
    lora = Mock()
    lora.return_value.load_lora_model_only.side_effect = lambda model, name, weight: (f'{model}+{name}@{weight}',)
    adapter = Mock()
    adapter.return_value.apply.return_value = ('reference-model',)
    core = SimpleNamespace(LoadImage=loader, LoraLoaderModelOnly=lora,
                           NODE_CLASS_MAPPINGS={'AnimaRefAdapter': adapter})
    monkeypatch.setitem(sys.modules, 'nodes', core)
    monkeypatch.setitem(sys.modules, 'folder_paths', SimpleNamespace(get_filename_list=lambda kind:
        ['style.safetensors', 'character.safetensors', 'anima_ref_adapter_v2_r64.safetensors']))
    spec = importlib.util.spec_from_file_location('axo_character_controls', ROOT / 'comfy_backend/character_nodes.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, core, adapter


def test_default_workflow_needs_neither_image_nor_lora(controls):
    module, core, adapter = controls
    base = object()
    assert module.AxoAnimaLoraStack().apply(base) == (base,)
    node = module.AxoOptionalAnimaReference()
    assert node.apply(base, 'vae') == (base,)
    assert node.VALIDATE_INPUTS(False, 'deleted.png') is True
    assert node.IS_CHANGED(False, 'deleted.png') is False
    core.LoadImage.assert_not_called()
    core.LoadImage.VALIDATE_INPUTS.assert_not_called()
    core.LoadImage.IS_CHANGED.assert_not_called()
    core.LoraLoaderModelOnly.assert_not_called()
    adapter.assert_not_called()


def test_lora_slots_apply_in_order_and_skip_zero_weight(controls):
    module, core, _ = controls
    result = module.AxoAnimaLoraStack().apply('base', 'style.safetensors', 0.6,
                                              'disabled.safetensors', 0,
                                              'character.safetensors', 0.8)
    assert result == ('base+style.safetensors@0.6+character.safetensors@0.8',)
    assert core.LoraLoaderModelOnly.return_value.load_lora_model_only.call_count == 2


def test_reference_can_be_combined_with_lora_model(controls):
    module, core, adapter = controls
    model = module.AxoAnimaLoraStack().apply('base', 'character.safetensors', 0.7)[0]
    node = module.AxoOptionalAnimaReference()
    assert node.apply(model, 'vae', True, 'character.png') == ('reference-model',)
    call = adapter.return_value.apply.call_args.kwargs
    assert call['model'] == model and call['image'] == 'pixels'
    assert call['lora_name'] == 'anima_ref_adapter_v2_r64.safetensors'
    assert node.IS_CHANGED(True, 'character.png') == 'image-hash'


def test_enabled_reference_requires_selected_valid_image(controls):
    module, core, adapter = controls
    node = module.AxoOptionalAnimaReference()
    with pytest.raises(ValueError, match='enviar'):
        node.apply('model', 'vae', True)
    core.LoadImage.VALIDATE_INPUTS.return_value = 'Invalid image file'
    with pytest.raises(ValueError, match='Invalid image'):
        node.apply('model', 'vae', True, 'missing.png')
    adapter.assert_not_called()


def test_schema_offers_empty_slots_and_optional_upload(controls):
    module, _, _ = controls
    stack = module.AxoAnimaLoraStack.INPUT_TYPES()['required']
    assert stack['lora_1'][0] == ['Nenhuma', 'style.safetensors', 'character.safetensors']
    reference = module.AxoOptionalAnimaReference.INPUT_TYPES()['required']
    assert reference['image'][0][0] == 'Nenhuma'
    assert reference['image'][1]['image_upload'] is True
    assert reference['use_reference'][1]['default'] is False
