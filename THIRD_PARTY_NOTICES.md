# Créditos e componentes externos

O Axo Image Studio personaliza e integra ferramentas existentes. O motor de geração, as bibliotecas, os modelos e as extensões abaixo pertencem aos seus respectivos projetos. Os links dos projetos são a referência para as licenças e condições de uso de cada componente.

| Componente | Papel | Referência |
|---|---|---|
| Forge Neo | Interface base e inferência | [Haoming02/sd-webui-forge-classic](https://github.com/Haoming02/sd-webui-forge-classic) |
| ComfyUI | Interface de nós e inferência alternativa | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) |
| Civicomfy | Busca e download de modelos Civitai no ComfyUI | [MoonGoblinDev/Civicomfy](https://github.com/MoonGoblinDev/Civicomfy) |
| Anima Ref Adapter | Condicionamento pela imagem da personagem | [ArcAnima/ComfyUI-Anima-Ref-Adapter](https://github.com/ArcAnima/ComfyUI-Anima-Ref-Adapter) |
| Impact Pack / Impact Subpack | Refinamento e detectores de rosto/mãos | [Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack), [Impact Subpack](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) |
| Anima Reference Adapter v2 | Pesos de referência da personagem | [ElectronGirl/anima-ref-adapter](https://huggingface.co/ElectronGirl/anima-ref-adapter) |
| Detectores ADetailer | Pesos YOLO de rosto e mãos | [Bingsu/adetailer](https://huggingface.co/Bingsu/adetailer) |
| Workflows ComfyUI | Referência para o starter Anima básico, sem Turbo | [Workflow oficial Anima](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_anima_base_v1.json) |
| cloudflared | Túnel temporário de acesso ao ComfyUI | [cloudflare/cloudflared](https://github.com/cloudflare/cloudflared) |
| Stable Diffusion WebUI | Recursos e sintaxe herdados pelo Forge | [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) |
| ADetailer Neo | Detalhamento automático | [Haoming02/ADetailer-Neo](https://github.com/Haoming02/ADetailer-Neo) |
| CivBrowser | Navegação e download de modelos | [SignalFlagZ/sd-webui-civbrowser](https://github.com/SignalFlagZ/sd-webui-civbrowser) |
| Localização pt-BR | Tradução da interface base | [M-art-ucci/stable-diffusion-webui-localization-pt_BR](https://github.com/M-art-ucci/stable-diffusion-webui-localization-pt_BR) |
| Gradio | Componentes e transporte da interface | [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| PyTorch | Execução de modelos na GPU | [pytorch/pytorch](https://github.com/pytorch/pytorch) |
| SDXL Base | Modelo base SDXL | [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) |
| Anima | Modelo e módulos Anima | [circlestone-labs/Anima](https://huggingface.co/circlestone-labs/Anima) |

## Revisões fixadas no instalador

| Projeto | Commit |
|---|---|
| Forge Neo | `bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3` |
| ComfyUI | `5f415e31abfd837870bbc733ba1e158de71ed985` |
| Civicomfy | `555e984bbcb02fc955075cb8eb699a6884c51239` |
| Anima Ref Adapter | `99c222e1c2da472f4b514583b2dbd1b5afb4bdd9` |
| Impact Pack | `eace4a9059908330936c6514f35f5e0c84935394` |
| Impact Subpack | `50c7b71a6a224734cc9b21963c6d1926816a97f1` |
| cloudflared | Release `2026.10.0`, binário Linux amd64 verificado por SHA256 |
| ADetailer Neo | `af228eba7a3f3691a25bcd1fc94aa95e600dd3e6` |
| CivBrowser | `7c9c32040722ee125cebb9bc3c9454322b14a2a3` |

O notebook baixa esses componentes na sessão do Colab. O repositório distribui a extensão Axo e o instalador, sem os pesos de modelos e sem uma cópia completa do Forge. Outros pesos e pré-processadores baixados pelo instalador têm referências no código e continuam sujeitos às condições de seus autores.

Os exemplos da wiki são orientações didáticas; resultados e configurações dependem do modelo. A arte de identidade visual foi preservada do notebook fornecido para este projeto; a captura de interface em `docs/assets` mostra o Axo Guide.
