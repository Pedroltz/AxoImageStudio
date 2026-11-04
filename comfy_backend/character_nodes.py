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


class AxoOptionalHires:
    @classmethod
    def INPUT_TYPES(cls):
        sampler = nodes.KSampler.INPUT_TYPES()['required']
        return {'required': {
            'image': ('IMAGE',), 'model': ('MODEL',), 'vae': ('VAE',),
            'positive': ('CONDITIONING',), 'negative': ('CONDITIONING',),
            'enabled': ('BOOLEAN', {'default': False, 'label_on': 'Hires ligado', 'label_off': 'sem Hires'}),
            'scale': ('FLOAT', {'default': 1.5, 'min': 1.0, 'max': 2.0, 'step': 0.05}),
            'denoise': ('FLOAT', {'default': 0.2, 'min': 0.0, 'max': 0.6, 'step': 0.01,
                                  'tooltip': '0 = só redimensionar; acima de 0 faz uma nova passagem do Anima.'}),
            'steps': ('INT', {'default': 16, 'min': 1, 'max': 100, 'step': 1}),
            'cfg': ('FLOAT', {'default': 4.0, 'min': 1.0, 'max': 15.0, 'step': 0.1}),
            'seed': ('INT', {'default': 20261104, 'min': 0, 'max': 0xffffffffffffffff}),
            'sampler_name': sampler['sampler_name'], 'scheduler': sampler['scheduler'],
            'upscale_method': (['bicubic', 'lanczos'], {'default': 'bicubic'}),
            'tiled_vae': ('BOOLEAN', {'default': True,
                                     'tooltip': 'Codifica/decodifica em blocos para reduzir uso de VRAM; a amostragem continua na imagem inteira.'}),
        }}

    RETURN_TYPES = ('IMAGE',)
    FUNCTION = 'upscale'
    CATEGORY = 'Axo/Anima'

    def upscale(self, image, model, vae, positive, negative, enabled=False, scale=1.5,
                denoise=0.2, steps=16, cfg=4.0, seed=20261104, sampler_name='euler',
                scheduler='simple', upscale_method='bicubic', tiled_vae=True):
        if not enabled:
            return (image,)
        # Anima works on a 16px grid; align the target before encoding so the
        # encode/decode roundtrip does not unexpectedly crop the enlarged image.
        height, width = image.shape[1:3]
        target_width = max(16, round(width * scale / 16) * 16)
        target_height = max(16, round(height * scale / 16) * 16)
        enlarged = nodes.ImageScale().upscale(image, upscale_method, target_width, target_height, 'disabled')[0]
        if denoise == 0:
            return (enlarged,)
        if tiled_vae:
            latent = nodes.VAEEncodeTiled().encode(vae, enlarged, tile_size=512, overlap=64)[0]
        else:
            latent = nodes.VAEEncode().encode(vae, enlarged)[0]
        sampled = nodes.KSampler().sample(model, seed, steps, cfg, sampler_name, scheduler,
                                          positive, negative, latent, denoise=denoise)[0]
        if tiled_vae:
            return nodes.VAEDecodeTiled().decode(vae, sampled, tile_size=512, overlap=64)
        return nodes.VAEDecode().decode(vae, sampled)


NODE_CLASS_MAPPINGS = {
    'AxoAnimaLoraStack': AxoAnimaLoraStack,
    'AxoOptionalAnimaReference': AxoOptionalAnimaReference,
    'AxoOptionalHires': AxoOptionalHires,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'AxoAnimaLoraStack': 'Axo · LoRAs do Anima (3 opcionais)',
    'AxoOptionalAnimaReference': 'Axo · Referência opcional da personagem',
    'AxoOptionalHires': 'Axo · Hires / Upscale opcional',
}
