"""Small Axo workflow controls, installed as the axo_starter custom-node entrypoint."""
import os

import folder_paths
import nodes

WEB_DIRECTORY = './web'
NONE = 'Nenhuma'


class AxoAnimaLoraStack:
    @classmethod
    def INPUT_TYPES(cls):
        names = [NONE] + [name for name in folder_paths.get_filename_list('loras')
                          if not os.path.basename(name).startswith('anima_ref_adapter_')]
        required = {'model': ('MODEL',)}
        for index in range(1, 4):
            required[f'lora_{index}'] = (names, {'default': NONE})
            required[f'strength_{index}'] = ('FLOAT', {'default': 0.8, 'min': -2.0, 'max': 2.0, 'step': 0.05})
        return {'required': required}

    RETURN_TYPES = ('MODEL',)
    FUNCTION = 'apply'
    CATEGORY = 'Axo/Anima'

    def apply(self, model, lora_1=NONE, strength_1=0.8, lora_2=NONE, strength_2=0.8,
              lora_3=NONE, strength_3=0.8):
        for name, strength in ((lora_1, strength_1), (lora_2, strength_2), (lora_3, strength_3)):
            if name != NONE and strength != 0:
                model = nodes.LoraLoaderModelOnly().load_lora_model_only(model, name, strength)[0]
        return (model,)


class AxoOptionalAnimaReference:
    @classmethod
    def INPUT_TYPES(cls):
        images = nodes.LoadImage.INPUT_TYPES()['required']['image'][0]
        return {'required': {
            'model': ('MODEL',), 'vae': ('VAE',),
            'use_reference': ('BOOLEAN', {'default': False, 'label_on': 'com imagem', 'label_off': 'só prompt + LoRAs'}),
            'image': ([NONE] + list(images), {'default': NONE, 'image_upload': True}),
            'ref_guidance': ('FLOAT', {'default': 4.5, 'min': 1.0, 'max': 10.0, 'step': 0.1}),
            'ref_end': ('FLOAT', {'default': 0.65, 'min': 0.0, 'max': 1.0, 'step': 0.05}),
            'ref_megapixels': ('FLOAT', {'default': 1.0, 'min': 0.25, 'max': 2.0, 'step': 0.25}),
        }}

    RETURN_TYPES = ('MODEL',)
    FUNCTION = 'apply'
    CATEGORY = 'Axo/Anima'

    @classmethod
    def VALIDATE_INPUTS(cls, use_reference, image):
        if not use_reference:
            return True
        if image == NONE:
            return 'Ative a referência somente depois de enviar e selecionar uma imagem.'
        return nodes.LoadImage.VALIDATE_INPUTS(image)

    @classmethod
    def IS_CHANGED(cls, use_reference, image, **kwargs):
        if not use_reference or image == NONE:
            return False
        return nodes.LoadImage.IS_CHANGED(image)

    def apply(self, model, vae, use_reference=False, image=NONE, ref_guidance=4.5,
              ref_end=0.65, ref_megapixels=1.0):
        if not use_reference:
            return (model,)
        valid = self.VALIDATE_INPUTS(True, image)
        if valid is not True:
            raise ValueError(valid)
        adapter = nodes.NODE_CLASS_MAPPINGS.get('AnimaRefAdapter')
        if adapter is None:
            raise RuntimeError('Anima Ref Adapter não carregou. Execute Install and launch novamente e confira comfy.log.')
        pixels = nodes.LoadImage().load_image(image)[0]
        return adapter().apply(model=model, vae=vae, image=pixels,
                               lora_name='anima_ref_adapter_v2_r64.safetensors',
                               ref_guidance=ref_guidance, correction='apg', strength=1.0,
                               ref_end=ref_end, ref_megapixels=ref_megapixels)


NODE_CLASS_MAPPINGS = {
    'AxoAnimaLoraStack': AxoAnimaLoraStack,
    'AxoOptionalAnimaReference': AxoOptionalAnimaReference,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'AxoAnimaLoraStack': 'Axo · LoRAs do Anima (3 opcionais)',
    'AxoOptionalAnimaReference': 'Axo · Referência opcional da personagem',
}
