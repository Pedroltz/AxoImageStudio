"""Initialize the two native ADetailer passes before their state is captured."""
import os
from modules import script_callbacks


def detailer_defaults(component, **kwargs):
    name = getattr(component, 'elem_id', '') or ''
    if not name.startswith(('script_txt2img_adetailer_', 'script_img2img_adetailer_')):
        return
    field = name.split('_adetailer_', 1)[1]
    second = field.endswith('_2nd')
    field = field.removesuffix('_2nd')
    values = {
        'ad_main_accordion': os.environ.get('AXO_ADETAILER_DEFAULT') == '1',
        'ad_model': 'hand_yolov8n.pt' if second else 'face_yolov8n.pt',
        'ad_denoising_strength': 0.40 if second else 0.30,
        'ad_use_inpaint_width_height': True,
        'ad_inpaint_width': 768,
        'ad_inpaint_height': 768,
        'ad_use_steps': True,
        'ad_steps': 20,
        'ad_controlnet_model': 'None',
    }
    if field in values:
        value = values[field]
        choices = getattr(component, 'choices', None)
        if choices and value not in [c[1] if isinstance(c, (list, tuple)) else c for c in choices]:
            return
        component.value = value


script_callbacks.on_after_component(detailer_defaults)
